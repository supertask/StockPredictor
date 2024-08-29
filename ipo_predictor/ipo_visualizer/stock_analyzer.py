import yfinance as yf
import statsmodels.api as sm

# 銘柄のデータを取得し、MACDとRSIを計算
class StockAnalyzer:
    def __init__(self, start_date, end_date, rsi_sell_threshold, rsi_buy_threshold, days_after_rsi, is_regression_analysis):
        self.start_date = start_date
        self.end_date = end_date
        self.RSI_SELL_THRESHOLD = rsi_sell_threshold
        self.RSI_BUY_THRESHOLD = rsi_buy_threshold
        self.DAYS_AFTER_RSI = days_after_rsi
        self.data = None
        self.buy_signal_days = None
        self.sell_signal_days = None
        self.is_regression_analysis = is_regression_analysis
        self.price_column = 'AdjustedClose' if self.is_regression_analysis else 'Close'  # 表示する列を動的に設定
        if self.is_regression_analysis:
            self.index_data = yf.download('2516.T', start=self.start_date, end=self.end_date)
            self.index_close = self.index_data['Close']  # ここでindex_closeを定義
    
    def calculate(self, symbol):
        self.symbol = symbol
        self.download_data()
        if self.is_regression_analysis:
            self.remove_index_influence()
        self.calculate_macd()
        self.calculate_rsi()
        self.identify_signals()
        self.assign_stock_info()
        
    def remove_index_influence(self):
        # インデックスを揃える
        aligned_index_close, aligned_stock_close = self.index_close.align(self.data['Close'], join='inner')
        
        # OLS回帰分析
        X = sm.add_constant(aligned_index_close)
        model = sm.OLS(aligned_stock_close, X).fit()
        self.data['AdjustedClose'] = self.data['Close'] - model.params[1] * aligned_index_close
    
    def download_data(self):
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date)
    
    def assign_stock_info(self):
        self.stock_info = {}
        self.stock_info['next_earnings_date'] = None
        self.stock_info['per'] = None
        self.stock_info['turnover_rate'] = None
        
        if self.symbol != '2516.T':
            stock = yf.Ticker(self.symbol)
            
            if stock:
                earnings_dates = stock.earnings_dates
                forward_eps = stock.info.get('forwardEps')
                trailing_per = stock.info.get('trailingPE')
                if trailing_per:
                    self.stock_info['per'] = round(trailing_per, 1)
                
                #if not self.data.empty:
                #    current_price = self.data[self.price_column][-1]
                #    if forward_eps is not None:
                #        per = current_price / forward_eps
                #        self.stock_info['per'] = per

                if earnings_dates is not None and not earnings_dates.empty:
                    self.stock_info['next_earnings_date'] = earnings_dates.index[0].strftime('%Y-%m-%d')


    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        self.data['ShortEMA'] = self.data[self.price_column].ewm(span=short_window, adjust=False).mean()
        self.data['LongEMA'] = self.data[self.price_column].ewm(span=long_window, adjust=False).mean()
        self.data['MACD'] = self.data['ShortEMA'] - self.data['LongEMA']
        self.data['SignalLine'] = self.data['MACD'].ewm(span=signal_window, adjust=False).mean()

    def calculate_rsi(self, window=14):
        delta = self.data[self.price_column].diff(1)
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
    
    def get_stock_info(self):
        return self.stock_info