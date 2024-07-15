import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 銘柄のシンボルと期間を設定
symbol = '2516.T'  # 例としてAppleのシンボルを使用
start_date = '2023-01-01'
end_date = '2024-07-12'

# データを取得
data = yf.download(symbol, start=start_date, end=end_date)

# MACDの計算
def calculate_macd(data, short_window, long_window, signal_window):
    data['ShortEMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['LongEMA'] = data['Close'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = data['ShortEMA'] - data['LongEMA']
    data['SignalLine'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    return data

# 12日と26日のEMA、9日のシグナルラインを使用してMACDを計算
data = calculate_macd(data, 12, 26, 9)

# MACDがシグナルラインを下から上にクロスする日を特定
data['BuySignal'] = (data['MACD'] > data['SignalLine']) & (data['MACD'].shift(1) <= data['SignalLine'].shift(1))

# 買いシグナルの日を特定
buy_signal_days = data[data['BuySignal']]

# 結果を表示
print(buy_signal_days[['Close', 'MACD', 'SignalLine', 'BuySignal']])

# グラフを作成
plt.figure(figsize=(14, 7))

# 株価のグラフ
plt.subplot(2, 1, 1)
plt.plot(data.index, data['Close'], label='Close Price')
plt.scatter(buy_signal_days.index, buy_signal_days['Close'], color='green', label='Buy Signal', marker='^')
plt.title(f'{symbol} Stock Price and Buy Signals')
plt.legend()

# MACDとシグナルラインのグラフ
plt.subplot(2, 1, 2)
plt.plot(data.index, data['MACD'], label='MACD')
plt.plot(data.index, data['SignalLine'], label='Signal Line')
plt.scatter(buy_signal_days.index, buy_signal_days['MACD'], color='green', label='Buy Signal', marker='^')
plt.axhline(0, color='grey', linestyle='--')
plt.title(f'{symbol} MACD and Signal Line')
plt.legend()

plt.tight_layout()
plt.show()

