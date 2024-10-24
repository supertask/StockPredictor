import googlemaps
import pandas as pd
from datetime import datetime
import time

class GoogleReviewGetter:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
        # 定数の定義
        self.SEARCH_RADIUS = 1000  # メートル単位での検索半径
        self.MAX_STORES = 200      # 店舗情報の最大取得件数
        self.MAX_REVIEWS = 30      # 1店舗あたりのレビュー最大取得件数
        
        self.target_company = {
            'フィットイージー': 'フィットイージー'
        }
        self.competitors = {
            'エニタイムフィットネス': 'エニタイムフィットネス',
            'チョコザップ': 'チョコザップ'
        }

    def get_store_info(self, company_name):
        keyword = self.target_company[company_name]
        places_result = self.gmaps.places(keyword, max_results=self.MAX_STORES)  # max_resultsパラメータを追加
        stores = []
        
        for place in places_result['results']:
            store_info = {
                'place_id': place['place_id'],
                'name': place['name'],
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'rating': place.get('rating', 0),
                'review_count': place.get('user_ratings_total', 0),
                'company': company_name
            }
            stores.append(store_info)
            
            location = (store_info['lat'], store_info['lng'])
            self._find_nearby_competitors(location, stores, company_name)
            
        return pd.DataFrame(stores)

    def _find_nearby_competitors(self, location, stores, main_company):
        for comp_name, comp_keyword in self.competitors.items():
            nearby_result = self.gmaps.places_nearby(
                location=location,
                radius=self.SEARCH_RADIUS,
                keyword=comp_keyword
            )
            
            if nearby_result['results']:
                nearest = nearby_result['results'][0]
                store_info = {
                    'place_id': nearest['place_id'],
                    'name': nearest['name'],
                    'lat': nearest['geometry']['location']['lat'],
                    'lng': nearest['geometry']['location']['lng'],
                    'rating': nearest.get('rating', 0),
                    'review_count': nearest.get('user_ratings_total', 0),
                    'company': comp_name
                }
                stores.append(store_info)

    def get_reviews(self, stores_df):
        reviews = []
        
        for _, store in stores_df.iterrows():
            place_details = self.gmaps.place(
                store['place_id'], 
                fields=['reviews'],
                reviews_no_translations=True,
                reviews_sort='newest',
                max_reviews=self.MAX_REVIEWS  # max_reviewsパラメータを追加
            )
            
            if 'reviews' in place_details['result']:
                for review in place_details['result']['reviews']:
                    review_info = {
                        'place_id': store['place_id'],
                        'rating': review['rating'],
                        'text': review['text'],
                        'time': datetime.fromtimestamp(review['time']).strftime('%Y-%m-%d %H:%M:%S'),
                        'company': store['company']
                    }
                    reviews.append(review_info)
            
            time.sleep(2)  # API制限を考慮した待機時間
            
        return pd.DataFrame(reviews)

def main():
    API_KEY = 'あなたのAPIキーをここに入力'
    reviewer = GoogleReviewGetter(API_KEY)
    
    # 店舗情報の取得
    stores_df = reviewer.get_store_info('company_A')
    stores_df.to_csv('stores_data.csv', index=False, encoding='utf-8')
    
    # レビュー情報の取得
    #reviews_df = reviewer.get_reviews(stores_df)
    #reviews_df.to_csv('reviews_data.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
