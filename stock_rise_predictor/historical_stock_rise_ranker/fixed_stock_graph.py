import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import datetime

# データ取得の開始日と終了日を設定
start = datetime(2013, 11, 17)
end = datetime.now()

# 日経平均株価指数と三井住友銀行の株価データを取得
nikkei = yf.download('^N225', start=start, end=end)
mitsui = yf.download('8316.T', start=start, end=end)

# 日次リターンを計算
nikkei['Return'] = nikkei['Adj Close'].pct_change()
mitsui['Return'] = mitsui['Adj Close'].pct_change()

# NaN値を削除
data = pd.DataFrame({'Nikkei': nikkei['Return'], 'Mitsui': mitsui['Return']}).dropna()

# ベータ係数の計算
X = sm.add_constant(data['Nikkei']) # 定数項を追加
model = sm.OLS(data['Mitsui'], X).fit()
beta = model.params['Nikkei']

# ベータ調整後のリターンの計算
data['Adjusted_Mitsui'] = data['Mitsui'] - beta * data['Nikkei']





# ============================-

# ここで 'starting_price_mitsui' を実際の開始日の株価に置き換えます。
print(data['Mitsui'].iloc[0])
print(mitsui['Adj Close'].iloc[0])
starting_price_mitsui = mitsui['Adj Close'].iloc[0]
starting_price_nikkei = nikkei['Adj Close'].iloc[0] # ここで 'starting_price_nikkei' を日経平均の開始日の実際の株価に置き換えます。

# 累積リターンの計算
cumulative_returns_mitsui = (1 + data['Mitsui']).cumprod()
cumulative_returns_adjusted = (1 + data['Adjusted_Mitsui']).cumprod()
cumulative_returns_nikkei = (1 + data['Nikkei']).cumprod() # 日経平均の累積リターンの計算

# 株価への変換
real_stock_price_mitsui = starting_price_mitsui * cumulative_returns_mitsui
real_stock_price_adjusted = starting_price_mitsui * cumulative_returns_adjusted
real_stock_price_nikkei = starting_price_nikkei * cumulative_returns_nikkei # 日経平均の実際の株価への変換

# データフレームに追加
data['Real_Stock_Price_Mitsui'] = real_stock_price_mitsui
data['Real_Stock_Price_Adjusted'] = real_stock_price_adjusted
data['Real_Stock_Price_Nikkei'] = real_stock_price_nikkei

# 結果をグラフに表示
#plt.figure(figsize=(12, 6))
#plt.plot(data.index, data['Real_Stock_Price_Mitsui'], label='Real Stock Price Mitsui')
#plt.plot(data.index, data['Real_Stock_Price_Adjusted'], label='Beta Adjusted Real Stock Price Mitsui')
#plt.plot(data.index, data['Real_Stock_Price_Nikkei'], label='Real Stock Price Nikkei', color='green')
#plt.title('Real Stock Prices: Original vs Beta Adjusted')
#plt.xlabel('Date')
#plt.ylabel('Stock Price (JPY)')
#plt.legend()
#plt.show()

#==============



fig, ax1 = plt.subplots(figsize=(12, 6))

# 三井住友銀行の株価用の軸を設定
ax1.set_xlabel('Date')
ax1.set_ylabel('Mitsui Stock Price (JPY)', color='tab:blue')
ax1.plot(data.index, data['Real_Stock_Price_Mitsui'], label='Real Stock Price Mitsui', color='tab:blue')
ax1.plot(data.index, data['Real_Stock_Price_Adjusted'], label='Beta Adjusted Real Stock Price Mitsui', color='tab:orange')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.legend(loc='upper left')

# 日経平均株価用の軸を追加
ax2 = ax1.twinx()  
ax2.set_ylabel('Nikkei Stock Price (JPY)', color='tab:green')
ax2.plot(data.index, data['Real_Stock_Price_Nikkei'], label='Real Stock Price Nikkei', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')
ax2.legend(loc='upper right')

# タイトルを設定
plt.title('Comparison of Stock Prices: Mitsui and Nikkei')
fig.tight_layout()  # グラフが重ならないようにレイアウトを調整

plt.show()
