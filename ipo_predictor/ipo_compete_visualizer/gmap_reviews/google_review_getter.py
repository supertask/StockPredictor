import googlemaps
import pandas as pd
from datetime import datetime
import time
from geopy.distance import geodesic
import argparse

class GoogleReviewGetter:
    def __init__(self, api_key):
        self.rural_prefectures = [
            "北海道", "青森県", "岩手県", "秋田県", "山形県", "福島県",
            "栃木県", "群馬県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県",
            "三重県", "奈良県", "和歌山県",
            "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県",
            "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        self.gmaps = googlemaps.Client(key=api_key)
        self.URBAN_NEARBY_RADIUS_KM = 5 * 2 # 都市部でジムに通う際の距離は1〜5kmであり、競合との距離はその倍の最大10km
        self.COUNTRY_SIDE_NEARBY_RADIUS_KM = 20 * 2 #地方でジムに通う際の距離は10 ~ 20kmであり、競合との距離はその倍の40km
        #self.MAX_TARGET_STORE_NUM = 200      # 店舗情報の最大取得件数
        self.MAX_TARGET_STORE_NUM = 20     # 店舗情報の最大取得件数
        self.MAX_SEARCHING_COMPETITOR_NUM = 20  # 近隣で店舗を探す際の最大件数
        self.MAX_SAVING_COMPETITOR_NUM = 3
        self.target_company = {
            'name': 'FIT-EASY',
            'search_keyword': 'FIT-EASY',
            'is_correct': lambda k: (not 'パーソナル' in k) and ('fit' in k and 'easy' in k) or ('フィット' in k and 'イージー' in k)
        }
        self.competitors = [
            {
                'name': 'Anytime Fitness',
                'search_keyword': 'Anytime Fitness',
                'is_correct': lambda k: (not 'パーソナル' in k) and ('anytime' in k and 'fitness' in k) or ('エニタイム' in k and 'フィットネス' in k)
            }
#            {
#                'name': 'chocoZAP',
#                'search_keyword': 'chocoZAP',
#                'is_correct': lambda k: (not 'パーソナル' in k) and ('choco' in k and 'zap' in k) or ('チョコ' in k and 'ザップ' in k)
#            }
        ]

    def get_store_info(self):
        stores = []
        next_page_token = None

        while len(stores) < self.MAX_TARGET_STORE_NUM:
            # Places APIで基本情報のみを取得
            places_result = self.gmaps.places(
                self.target_company['search_keyword'], 
                page_token=next_page_token
            )
            
            target_company_num = 0
            for place in places_result.get('results', []):
                # ターゲット企業の名称と一致しているか確認
                if self.target_company['is_correct'](place['name'].lower()):
                    target_company_num+=1
                    store_info = {
                        'place_id': place['place_id'],
                        'name': place['name'], #店舗名
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'rating': place.get('rating', 0),
                        'review_count': place.get('user_ratings_total', 0),
                        'company': self.target_company['name'],
                        'target_company_num': target_company_num,
                        'competitors_disance': 0
                    }
                    print('place: ', place)

                    stores.append(store_info)
                    
                    location = (store_info['lat'], store_info['lng'])
                    self._find_nearby_competitors(location, stores, target_company_num)
                
            next_page_token = places_result.get('next_page_token')
            if not next_page_token:
                break
            time.sleep(2)

        return pd.DataFrame(stores)

    def _find_nearby_competitors(self, location, stores, target_company_num):
        for competitor in self.competitors:
            searching_competitor_count = 0
            saving_competitor_count = 0
            next_page_token = None

            while searching_competitor_count < self.MAX_SEARCHING_COMPETITOR_NUM:
                nearby_result = self.gmaps.places_nearby(
                    location=location,
                    rank_by='distance',
                    keyword=competitor['search_keyword'],
                    page_token=next_page_token
                )
                
                for nearest in nearby_result.get('results', []):
                    if competitor['is_correct'](nearest['name'].lower()):
                        competitor_location = (nearest['geometry']['location']['lat'], nearest['geometry']['location']['lng'])
                        distance_km = geodesic(location, competitor_location).kilometers
                        if distance_km < self.COUNTRY_SIDE_NEARBY_RADIUS_KM and saving_competitor_count < self.MAX_SAVING_COMPETITOR_NUM:
                            store_info = {
                                'place_id': nearest['place_id'],
                                'name': nearest['name'],
                                'lat': nearest['geometry']['location']['lat'],
                                'lng': nearest['geometry']['location']['lng'],
                                'rating': nearest.get('rating', 0),
                                'review_count': nearest.get('user_ratings_total', 0),
                                'company': competitor['name'],
                                'target_company_num': target_company_num,
                                'competitors_disance': round(distance_km, 2)  # 距離を小数第2桁まで
                            }
                            print("nearest: ", nearest)
                            stores.append(store_info)
                            saving_competitor_count+=1
                    searching_competitor_count += 1

                next_page_token = nearby_result.get('next_page_token')
                if not next_page_token:
                    break
                time.sleep(2)

    def get_reviews(self, stores_df):
        reviews = []
        
        for _, store in stores_df.iterrows():
            # Place APIでレビュー情報を取得
            place_details = self.gmaps.place(
                store['place_id'], 
                fields=['reviews'],  # レビューのみを取得
                reviews_no_translations=True,  # 翻訳を除外
                #reviews_sort='newest'  # 最新のレビューを優先
                reviews_sort='most_relevant'  # 最新のレビューを優先
            )
            
            if 'reviews' in place_details.get('result', {}):
                for review in place_details['result']['reviews']:
                    review_info = {
                        'place_id': store['place_id'],
                        'rating': review['rating'],
                        'text': review['text'],
                        'time': datetime.fromtimestamp(review['time']).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    reviews.append(review_info)
            
            time.sleep(2)

        return pd.DataFrame(reviews)

def main():
    API_KEY = 'AIzaSyBwPdwD8WwieNmMyXwOGmATY3glOXvVAa8'
    reviewer = GoogleReviewGetter(API_KEY)
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('command', choices=['store', 'review', 'all'], help='Command to execute')
    args = parser.parse_args()

    if args.command in ['store', 'all']:
        # 店舗情報の取得
        stores_df = reviewer.get_store_info()
        stores_df.to_csv('stores_data.csv', index=False, encoding='utf-8')
    
    if args.command in ['review', 'all']:
        # CSVファイルから店舗情報を読み込む
        stores_df = pd.read_csv('stores_data.csv')
        # レビュー情報の取得
        reviews_df = reviewer.get_reviews(stores_df)
        reviews_df.to_csv('reviews_data.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
