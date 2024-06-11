import yfinance as yf
from requests.exceptions import HTTPError

def is_delisted(code):
    symbol = code + ".T"
    try:
        ticker = yf.Ticker(symbol)
        ticker_info = ticker.info
        if not ticker_info:
            #print("ティッカー情報が取得できませんでした。上場廃止の可能性があります。")
            return True
        
        # 最近の株価データを確認する
        hist = ticker.history(period="1d")
        if hist.empty:
            #print("最近の取引データがありません。上場廃止の可能性があります。")
            return True
        
        #print("ティッカーは存在し、取引データがあります。")
        return False
    except HTTPError as http_err:
        #print(f"HTTPエラーが発生しました: {http_err}")
        return True
    except Exception as e:
        #print(f"ティッカー情報の取得に失敗しました: {e}")
        return True

delisted = is_delisted("3464")
print(f"上場廃止確認: {delisted}")

