#株価が下落している際に取引量が急増し、その後取引量が減少する動きは底打ちの兆候とされる。

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'  # 例としてAppleのシンボルを使用
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# 移動平均を計算（ここでは20日移動平均）
data['20_MA'] = data['Volume'].rolling(window=20).mean()

# 取引量が急増し、その後減少するかどうかを確認
data['Volume_Surge'] = (data['Volume'] > 1.5 * data['20_MA']) & (data['Volume'].shift(-1) < data['Volume'])

# ボリュームサージが発生した日を特定
volume_surge_days = data[data['Volume_Surge']]

# 結果を表示
print(volume_surge_days)

# グラフを作成
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Close'], label='Close Price')
plt.scatter(volume_surge_days.index, volume_surge_days['Close'], color='red', label='Volume Surge', marker='o')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title(f'{symbol} Stock Price and Volume Surge')
plt.legend()
plt.show()

