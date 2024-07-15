import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'  # 例としてAppleのシンボルを使用
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# サポートラインを計算（過去の最安値）
support_level = data['Close'].min()

# サポートラインでの反発を特定
data['SupportBounce'] = (data['Close'] <= support_level) & (data['Close'].shift(-1) > support_level)

# 反発の日を特定
support_bounce_days = data[data['SupportBounce']]

# 結果を表示
print(support_bounce_days[['Close', 'SupportBounce']])

# グラフを作成
plt.figure(figsize=(14, 7))

# 株価のグラフ
plt.plot(data.index, data['Close'], label='Close Price')
plt.axhline(support_level, color='red', linestyle='--', label='Support Level')
plt.scatter(support_bounce_days.index, support_bounce_days['Close'], color='green', label='Support Bounce', marker='^')
plt.title(f'{symbol} Stock Price and Support Bounces')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

