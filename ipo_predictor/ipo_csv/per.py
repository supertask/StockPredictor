import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄コードを指定
ticker = '5588.T'  # トヨタ自動車の例

# データを取得
stock = yf.Ticker(ticker)
historical_data = stock.history(period='5y')  # 過去5年分のデータを取得

# EPSデータを取得（最新のEPSを使用）
eps = stock.info['trailingEps']

# PERを計算
historical_data['PER'] = historical_data['Close'] / eps

# チャートを描画
plt.figure(figsize=(10, 5))
plt.plot(historical_data.index, historical_data['PER'], label='PER')
plt.xlabel('Date')
plt.ylabel('PER')
plt.title('PER Chart')
plt.legend()
plt.show()

