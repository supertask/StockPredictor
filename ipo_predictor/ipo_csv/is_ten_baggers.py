import pandas as pd
import requests
from datetime import datetime

# リフレッシュトークンを使用してIDトークンを取得する関数
def get_id_token(refresh_token):
    r_post = requests.post(
        f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"
    )
    id_token = r_post.json()['idToken']
    return id_token

# 株価情報を取得する関数
def get_stock_prices(id_token, code):
    headers = {'Authorization': 'Bearer {}'.format(id_token)}
    r = requests.get(
        f"https://api.jquants.com/v1/prices/daily_quotes?code={code}",
        headers=headers
    )
    price_df = pd.DataFrame(r.json()['daily_quotes'])
    return price_df

# 財務データを取得する関数
def get_financial_statements(id_token, code):
    headers = {'Authorization': 'Bearer {}'.format(id_token)}
    r = requests.get(
        f"https://api.jquants.com/v1/fins/statements?code={code}",
        headers=headers
    )
    statements_df = pd.DataFrame(r.json()['statements'])
    return statements_df

def get_ten_bagger_description(ticker, refresh_token):
    # IDトークンを取得
    id_token = get_id_token(refresh_token)

    # 株価データを取得
    price_df = get_stock_prices(id_token, ticker)
    
    close_param = 'AdjustmentClose'

    # 約最初の12ヶ月(上場して1年以内)
    first_year_price_df = price_df.iloc[:min(12 * 20, len(price_df))]
    min_price_index = first_year_price_df[close_param].idxmin()
    buy_price = first_year_price_df[close_param].min()
    buy_date_str = first_year_price_df.loc[min_price_index, 'Date']
    
    entire_period_price_df = price_df.iloc[:]  # 全ての期間
    max_price_index = entire_period_price_df[close_param].idxmax()
    sell_price = entire_period_price_df[close_param].max()
    sell_date_str = entire_period_price_df.loc[max_price_index, 'Date']

    buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d')
    sell_date = datetime.strptime(sell_date_str, '%Y-%m-%d')

    # 期間を計算
    delta = sell_date - buy_date
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30

    n_times = round(sell_price / buy_price, 1)

    ten_bagger_description = f"{years}年{months}ヶ月{days}日で{n_times}倍株\n"

    if sell_price >= 10 * buy_price:
        pass
    else:
        pass
        
    ten_bagger_description += f"最小: {buy_price}円 on {buy_date_str}\n最大: {sell_price}円 on {sell_date_str}"
    #ten_bagger_description += f"最初の12ヶ月の最小株価: {buy_price}円 ({buy_date_str}),\n全ての期間での最大株価: {sell_price}円 ({sell_date_str})"
    return ten_bagger_description


#ticker = '7203' #トヨタ
#ticker = '5588' #ファーストアカウンティング
#ticker = '9166' #GENDA
ticker = '3496' #アズーム
refresh_token = "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.t_KDmSYrgWo6jJfppD5Y0gxRCeB5QMkgmBM2o_Ys3azs13Fb4iIju-2cU4_0PLEV0Ov-S2KOI57_hVYN35HZnzLFWRvufQ_n1hRrrRKwKShzL0heoMMS11Hlmn1_g8tIIwWLa59_xW-w2t4kSpk27rv8YiWIixeWEb5_VhLcWy13aiMxOD9rChaty2wCU_vt7KrrQyL4iApr3f5ESU5cIhWZdXbCiEbxGuSX8cbvKFTkYOiVZ0FTEI_s5oY1wSmG35AfWJV9JgEjWLkx0ZMPH5ZdQcZRQtMW6oHmBAiEHym5GTrbNiLc03PfsP7XmjV3MKQQUbujQRsOzhV9bLSfzQ.4N7p77HAwBiYCkhj.o8LnVLanx3gTt-YSYZ1rGp4d8-2l-8pnJ-inqM81TkbdZ3IX8-Bw2nulvGut42AwC1YzW5CXltdeQm2gJay_GUJ1cmgV0tRt4sZ0D5xmH8_fMKQ86vth4cqxWXQyJq1fMW1_cJE7ZAzuBaUdyDEGiCho6CNePz_FbzP5JUOcIwadmoSUPV0w6puQXCZDdsbf1jtR2rbwgbERjTxcv1rN8Ul1Yl3r64l1uZrzRWo4Za5IS6pYTb_UB5DV7_pX8KY297XcFtHUt6tnDybyZPl-T8Tv15MsIBpmRvaHVdeVYh6h7yh4aN9Q18bGUoaW0yMNwspmIiWHz9RxaFQXsDFv8vkY-7V7PvoRo5iMVNq1Qpxq9WrXBGcNyo12yp5e9LGzmK2RKi_It1Q9PRbmXkbGjt9bspNDepd6EgpIhTYh_EHUHsm52YD25B818QMup3YktnFdastn8k3Qq8WmlB8ncsLuOS0oy1_DIvZDCsR2rp05HHQ6jGfxNZ5IZsgxMVmvL23eDY99Qim2aEJ0FmFRrQQKaGfXAQlLme-jKN0Jb8kfpQLZjb5yubo9kpe2AQLF7NY8WP5Lxe-4ceI7Ib-DCHygpay4P1zlE7ubLa44uRuVxYFtdnYKzTLwEnQi3qhEnso7Q_hEGJ1rplKeI88Aaa4AhlGc8dP_9yJdwsiZdGpJPB9z5r_3JTftmSAC5IkJe5nxw-xsTaZC2X3Q-7jFYc0_xgPqLlDSGvY0m-fkYk6xN88D1dy2oeSi99PbakvKKBl9PgGcejzLtH_5QQbC63pJQzOV8YKjmUzd2ygzJB9fMiaQSQTVxxlgJtOz-3tebmHtkt861tWh28rR7RkRCYif3Jr5phOR7JEx1SyYVv0mXZk0M2NARQql5NsH0wgcAZBzku27OzpfCyFK-M46hvQ-nWTUKnxo8LBqstJun4Z0v4dxHslcxN9216VP8e6QYFBLtr3dnJqX_9wpkYPcbJXEewt2FoJIUR3tfl3H75fajXLhWEIE8SaFvmuXWpJc80sE69Z05KEbM-1kjQOEs24gVmXTRCX9_CupsGwVobZwKMJ8dG7jnPFt7p-WSx-_tKwO61W-6i2YmYguulLf-h5viOqXHK-YrIoRnu3Mbo-D-PImUH36izA3z8GA5M31dN-iVHYsrQWoVZhlDP2yrNhzbxVrvliN4_oFnHCeXKkHGR25-3zgkqq82jIKosK6UY_46ECydZHeEwenlf4SSWWHSjjzngqZgofm3N5Hr81pqc9Z0bkLWJZqMJHidgBjPl6_893qAF9Wkd2-VStkBbuvdkDQCl66LStErn9W_EBfe5RY9BGfW5nBpKEWBt5Y78oNdxDGIvDv9w.7XQT9Wi6UXyv4JCAAq97iw"
ten_bagger_description = get_ten_bagger_description(ticker, refresh_token)

