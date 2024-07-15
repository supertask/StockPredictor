
import yfinance as yf

# 銘柄のデータを取得し、MACDとRSIを計算
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

            if self.data['RSI'].iloc[i] > 80:
                self.data['SellSignal'].iloc[i] = True        

        self.buy_signal_days = self.data[self.data['BuySignal']]
        self.sell_signal_days = self.data[self.data['SellSignal']]
    
    def get_signals(self):
        return self.buy_signal_days, self.sell_signal_days
