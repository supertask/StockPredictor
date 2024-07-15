#
# TODO: RSI結構使えるかも
#
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'
#symbol = '9158.T'
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# RSIの計算
def calculate_rsi(data, window):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 14日間のRSIを計算
data['RSI'] = calculate_rsi(data, 14)

# RSIが30以下の日を特定
rsi_low_days = data[data['RSI'] <= 30]

# 結果を表示
print(rsi_low_days[['Close', 'RSI']])

# グラフを作成
plt.figure(figsize=(14, 7))

# 株価のグラフ
plt.subplot(2, 1, 1)
plt.plot(data.index, data['Close'], label='Close Price')
plt.scatter(rsi_low_days.index, rsi_low_days['Close'], color='red', label='RSI <= 30', marker='o')
plt.title(f'{symbol} Stock Price')
plt.legend()

# RSIのグラフ
plt.subplot(2, 1, 2)
plt.plot(data.index, data['RSI'], label='RSI')
plt.axhline(30, color='red', linestyle='--', label='RSI 30')
plt.axhline(70, color='green', linestyle='--', label='RSI 70')
plt.title(f'{symbol} RSI')
plt.legend()

plt.tight_layout()
plt.show()

