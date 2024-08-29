import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class StockAnalyzer:
    def __init__(self, symbol, start_date, end_date, rsi_sell_threshold, rsi_buy_threshold, days_after_rsi):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.RSI_SELL_THRESHOLD = rsi_sell_threshold
        self.RSI_BUY_THRESHOLD = rsi_buy_threshold
        self.DAYS_AFTER_RSI = days_after_rsi
        self.data = None
        self.buy_signal_days = None
        self.sell_signal_days = None
    
    def download_data(self):
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date)

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        self.data['ShortEMA'] = self.data['Close'].ewm(span=short_window, adjust=False).mean()
        self.data['LongEMA'] = self.data['Close'].ewm(span=long_window, adjust=False).mean()
        self.data['MACD'] = self.data['ShortEMA'] - self.data['LongEMA']
        self.data['SignalLine'] = self.data['MACD'].ewm(span=signal_window, adjust=False).mean()

    def calculate_rsi(self, window=14):
        delta = self.data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
    
    def identify_signals(self):
        self.data['BuySignal'] = False
        self.data['SellSignal'] = False
        
        for i in range(len(self.data)):
            if self.data['RSI'].iloc[i] < self.RSI_BUY_THRESHOLD:
                for j in range(1, self.DAYS_AFTER_RSI + 1):
                    if i + j < len(self.data) and (self.data['MACD'].iloc[i + j] > self.data['SignalLine'].iloc[i + j]) and (self.data['MACD'].shift(1).iloc[i + j] <= self.data['SignalLine'].shift(1).iloc[i + j]):
                        self.data['BuySignal'].iloc[i + j] = True
                        break

            if self.data['RSI'].iloc[i] > self.RSI_SELL_THRESHOLD:
                for j in range(1, self.DAYS_AFTER_RSI + 1):
                    if i + j < len(self.data) and (self.data['MACD'].iloc[i + j] < self.data['SignalLine'].iloc[i + j]) and (self.data['MACD'].shift(1).iloc[i + j] >= self.data['SignalLine'].shift(1).iloc[i + j]):
                        self.data['SellSignal'].iloc[i + j] = True
                        break
        
        self.buy_signal_days = self.data[self.data['BuySignal']]
        self.sell_signal_days = self.data[self.data['SellSignal']]
    
    def get_signals(self):
        return self.buy_signal_days, self.sell_signal_days

class StockPlotter:
    def __init__(self, data, buy_signal_days, sell_signal_days, symbol, rsi_sell_threshold, rsi_buy_threshold):
        self.data = data
        self.buy_signal_days = buy_signal_days
        self.sell_signal_days = sell_signal_days
        self.symbol = symbol
        self.RSI_SELL_THRESHOLD = rsi_sell_threshold
        self.RSI_BUY_THRESHOLD = rsi_buy_threshold
    
    def plot(self):
        plt.figure(figsize=(14, 10))

        # 株価のグラフ
        plt.subplot(3, 1, 1)
        plt.plot(self.data.index, self.data['Close'], label='Close Price')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['Close'], color='green', label='Buy Signal', marker='^', alpha=1)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['Close'], color='red', label='Sell Signal', marker='v', alpha=1)
        plt.title(f'{self.symbol} Stock Price and Buy/Sell Signals')
        plt.legend()

        # MACDとシグナルラインのグラフ
        plt.subplot(3, 1, 2)
        plt.plot(self.data.index, self.data['MACD'], label='MACD')
        plt.plot(self.data.index, self.data['SignalLine'], label='Signal Line')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['MACD'], color='green', label='Buy Signal', marker='^', alpha=1)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['MACD'], color='red', label='Sell Signal', marker='v', alpha=1)
        plt.axhline(0, color='grey', linestyle='--')
        plt.title(f'{self.symbol} MACD and Signal Line')
        plt.legend()

        # RSIのグラフ
        plt.subplot(3, 1, 3)
        plt.plot(self.data.index, self.data['RSI'], label='RSI')
        plt.axhline(self.RSI_SELL_THRESHOLD, color='red', linestyle='--', label='Overbought')
        plt.axhline(self.RSI_BUY_THRESHOLD, color='green', linestyle='--', label='Oversold')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['RSI'], color='green', label='Buy Signal', marker='^', alpha=1)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['RSI'], color='red', label='Sell Signal', marker='v', alpha=1)
        plt.title(f'{self.symbol} RSI')
        plt.legend()

        plt.tight_layout()
        plt.show()

# 使用例
symbol = '2516.T'
start_date = '2023-01-01'
end_date = '2024-07-12'
RSI_SELL_THRESHOLD = 65
RSI_BUY_THRESHOLD = 35
DAYS_AFTER_RSI = 15

# 分析クラスのインスタンスを作成し、データを取得・計算
analyzer = StockAnalyzer(symbol, start_date, end_date, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD, DAYS_AFTER_RSI)
analyzer.download_data()
analyzer.calculate_macd()
analyzer.calculate_rsi()
analyzer.identify_signals()

# シグナルを取得
buy_signal_days, sell_signal_days = analyzer.get_signals()

# プロットクラスのインスタンスを作成し、グラフをプロット
plotter = StockPlotter(analyzer.data, buy_signal_days, sell_signal_days, symbol, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD)
plotter.plot()
