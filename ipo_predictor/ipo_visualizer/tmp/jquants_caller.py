
import os
import pandas as pd
import requests


class JQuantsCaller:
    def __init__(self):
        self.base_url = "https://api.jquants.com/v1"
        email, password = os.environ['JQUANTS_MAIL_ADDRESS'], os.environ['JQUANTS_PASSWORD']
        self.refresh_token = self.auth_user(email, password)
        self.id_token = self.get_id_token(self.refresh_token)
        
    def auth_user(self, email, password):
        body = {
            "mailaddress": email,
            "password": password
        }
        response = requests.post(f"{self.base_url}/token/auth_user", json=body)
        return response.json()['refresh_token']

    # リフレッシュトークンを使用してIDトークンを取得する関数
    def get_id_token(self, refresh_token):
        r_post = requests.post(
            f"{self.base_url}/token/auth_refresh?refreshtoken={refresh_token}"
        )
        id_token = r_post.json()['idToken']
        return id_token

    # 株価情報を取得する関数
    def get_stock_prices(self, code):
        headers = {'Authorization': 'Bearer {}'.format(self.id_token)}
        r = requests.get(
            f"{self.base_url}/prices/daily_quotes?code={code}",
            headers=headers
        )
        price_df = pd.DataFrame(r.json()['daily_quotes'])
        return price_df
        
    # 財務データを取得する関数
    def get_financial_statements(self, code):
        headers = {'Authorization': 'Bearer {}'.format(self.id_token)}
        r = requests.get(
            f"{self.base_url}/fins/statements?code={code}",
            headers=headers
        )
        statements_df = pd.DataFrame(r.json()['statements'])
        return statements_df
        
