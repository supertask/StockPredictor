import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'  # 例としてAppleのシンボルを使用
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# ボリンジャーバンドの計算
def calculate_bollinger_bands(data, window, no_of_std):
    data['SMA'] = data['Close'].rolling(window=window).mean()
    data['STD'] = data['Close'].rolling(window=window).std()
    data['UpperBand'] = data['SMA'] + (data['STD'] * no_of_std)
    data['LowerBand'] = data['SMA'] - (data['STD'] * no_of_std)
    return data

# 20日間のボリンジャーバンドを計算（標準偏差2倍）
data = calculate_bollinger_bands(data, 20, 2)

# ボリンジャーバンドの下限に達し、その後バンド内に戻る日を特定
data['BuySignal'] = (data['Close'] < data['LowerBand']) & (data['Close'].shift(1) >= data['LowerBand'])

# 買いシグナルの日を特定
buy_signal_days = data[data['BuySignal']]

# 結果を表示
print(buy_signal_days[['Close', 'LowerBand', 'BuySignal']])

# グラフを作成
plt.figure(figsize=(14, 7))

# 株価とボリンジャーバンドのグラフ
plt.plot(data.index, data['Close'], label='Close Price')
plt.plot(data.index, data['UpperBand'], label='Upper Band', linestyle='--')
plt.plot(data.index, data['LowerBand'], label='Lower Band', linestyle='--')
plt.scatter(buy_signal_days.index, buy_signal_days['Close'], color='green', label='Buy Signal', marker='^')
plt.fill_between(data.index, data['LowerBand'], data['UpperBand'], color='grey', alpha=0.1)
plt.title(f'{symbol} Bollinger Bands and Buy Signals')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

