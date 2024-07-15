import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'  # 例としてAppleのシンボルを使用
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# ハンマーを特定する関数
def is_hammer(row):
    body_length = abs(row['Close'] - row['Open'])
    lower_shadow = row['Low'] - min(row['Close'], row['Open'])
    upper_shadow = max(row['Close'], row['Open']) - row['High']
    return (lower_shadow > 2 * body_length) and (upper_shadow < body_length)

# ハンマーを特定
data['Hammer'] = data.apply(is_hammer, axis=1)

# ハンマーの日を特定
hammer_days = data[data['Hammer']]

# 結果を表示
print(hammer_days[['Open', 'High', 'Low', 'Close', 'Hammer']])

# グラフを作成
plt.figure(figsize=(14, 7))

# 株価のグラフ
plt.plot(data.index, data['Close'], label='Close Price')
plt.scatter(hammer_days.index, hammer_days['Close'], color='green', label='Hammer', marker='^')
plt.title(f'{symbol} Stock Price and Hammer Patterns')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

