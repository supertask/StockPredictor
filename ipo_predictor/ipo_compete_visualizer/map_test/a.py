import googlemaps
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球の半径（km）
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def get_place_details(gmaps, place_id):
    place = gmaps.place(place_id, fields=['name', 'geometry', 'rating', 'reviews'])
    reviews = place['result'].get('reviews', [])
    review_texts = '|'.join([review['text'] for review in reviews]) if reviews else ''
    
    return {
        'name': place['result']['name'],
        'lat': place['result']['geometry']['location']['lat'],
        'lng': place['result']['geometry']['location']['lng'],
        'rating': place['result'].get('rating', 0),
        'reviews': review_texts
    }

def main():
    # Google Maps APIキーを設定
    API_KEY = 'あなたのAPIキーをここに入力'
    gmaps = googlemaps.Client(key=API_KEY)
    
    # フィットイージーの店舗を検索
    fit_easy_results = gmaps.places(query='フィットイージー')
    
    # エニタイムフィットネスの店舗を検索
    anytime_results = gmaps.places(query='エニタイムフィットネス')
    
    comparison_data = []
    
    # 各フィットイージー店舗に対して処理
    for fit_easy in fit_easy_results['results']:
        fit_easy_details = get_place_details(gmaps, fit_easy['place_id'])
        
        # 最も近いエニタイムフィットネスを見つける
        nearest_anytime = None
        min_distance = float('inf')
        
        for anytime in anytime_results['results']:
            distance = calculate_distance(
                fit_easy_details['lat'],
                fit_easy_details['lng'],
                anytime['geometry']['location']['lat'],
                anytime['geometry']['location']['lng']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_anytime = anytime
        
        if nearest_anytime:
            anytime_details = get_place_details(gmaps, nearest_anytime['place_id'])
            
            comparison_data.append({
                'fit_easy_name': fit_easy_details['name'],
                'fit_easy_rating': fit_easy_details['rating'],
                'fit_easy_reviews': fit_easy_details['reviews'],
                'anytime_name': anytime_details['name'],
                'anytime_rating': anytime_details['rating'],
                'anytime_reviews': anytime_details['reviews']
            })
    
    # DataFrameを作成して保存
    df = pd.DataFrame(comparison_data)
    df.to_csv('gym_comparison.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()

