import googlemaps
import pandas as pd
from datetime import datetime
import time

class GoogleReviewGetter:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
        self.SEARCH_RADIUS = 10000  # メートル単位での検索半径. 10km
        #self.MAX_STORES = 200      # 店舗情報の最大取得件数
        self.MAX_STORES = 20     # 店舗情報の最大取得件数
        self.MAX_NEARBY_STORES = 40  # 最大近隣店舗件数
        self.target_company = {
            'name': 'FIT-EASY',
            'search_keyword': 'FIT-EASY',
            'is_correct': lambda k: ('fit' in k and 'easy' in k) or ('フィット' in k and 'イージー' in k)
        }
        self.competitors = [
            {
                'name': 'Anytime Fitness',
                'search_keyword': 'Anytime Fitness',
                'is_correct': lambda k: ('anytime' in k and 'fitness' in k) or ('エニタイム' in k and 'フィットネス' in k)
            }
#            {
#                'name': 'chocoZAP',
#                'search_keyword': 'chocoZAP',
#                'is_correct': lambda k: ('choco' in k and 'zap' in k) or ('チョコ' in k and 'ザップ' in k)
#            }
        ]

    def get_store_info(self):
        stores = []
        next_page_token = None

        while len(stores) < self.MAX_STORES:
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
                        'target_company_num': target_company_num
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
            nearby_stores_count = 0
            next_page_token = None

            while nearby_stores_count < self.MAX_NEARBY_STORES:
                nearby_result = self.gmaps.places_nearby(
                    location=location,
                    radius=self.SEARCH_RADIUS,
                    keyword=competitor['search_keyword'],
                    page_token=next_page_token
                )
                
                # 競合の名称と一致していれば, 1件だけ保存
                for nearest in nearby_result.get('results', []):
                    if competitor['is_correct'](nearest['name'].lower()):
                        store_info = {
                            'place_id': nearest['place_id'],
                            'name': nearest['name'],
                            'lat': nearest['geometry']['location']['lat'],
                            'lng': nearest['geometry']['location']['lng'],
                            'rating': nearest.get('rating', 0),
                            'review_count': nearest.get('user_ratings_total', 0),
                            'company': competitor['name'],
                            'target_company_num': target_company_num
                        }
                        print("nearest: ", nearest)
                        stores.append(store_info)
                        break  # 1件保存したら次の競合へ
                    nearby_stores_count += 1

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
    
    # 店舗情報の取得
    stores_df = reviewer.get_store_info()
    stores_df.to_csv('stores_data.csv', index=False, encoding='utf-8')
    
    # レビュー情報の取得
    #reviews_df = reviewer.get_reviews(stores_df)
    #reviews_df.to_csv('reviews_data.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
