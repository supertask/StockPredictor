from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

class StockAnalyzer:
    def __init__(self, individual_stock_symbol, nikkei_index_symbol='^N225', start_date=datetime(2013, 11, 17), end_date=datetime.now()):
        self.individual_stock_symbol = individual_stock_symbol
        self.nikkei_index_symbol = nikkei_index_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.display_only_ajusted_stock = True

    def fetch_data(self):
        individual_stock_data = yf.download(self.individual_stock_symbol, start=self.start_date, end=self.end_date)
        nikkei_index_data = yf.download(self.nikkei_index_symbol, start=self.start_date, end=self.end_date)

        stock_return = individual_stock_data['Adj Close'].pct_change()
        index_return = nikkei_index_data['Adj Close'].pct_change()

        self.data = pd.DataFrame({'Individual_Stock': stock_return, 'Nikkei_Index': index_return}).dropna()

        individual_stock_start_price = individual_stock_data['Adj Close'].iloc[0]
        nikkei_index_start_price = nikkei_index_data['Adj Close'].iloc[0]

        X = sm.add_constant(self.data['Nikkei_Index'])
        model = sm.OLS(self.data['Individual_Stock'], X).fit()
        beta = model.params['Nikkei_Index']
        self.data['Individual_Stock_Adjusted'] = self.data['Individual_Stock'] - beta * self.data['Nikkei_Index']

        self.data['Cumulative_Return_Individual_Stock'] = (1 + self.data['Individual_Stock']).cumprod()
        self.data['Cumulative_Return_Individual_Stock_Ajusted'] = (1 + self.data['Individual_Stock_Adjusted']).cumprod()
        self.data['Cumulative_Return_Nikkei_Index']  = (1 + self.data['Nikkei_Index']).cumprod() # 日経平均の累積リターンの計算

        self.data['Real_Individual_Stock_Price'] = individual_stock_start_price * self.data['Cumulative_Return_Individual_Stock']
        self.data['Real_Individual_Stock_Price_Adjusted'] = individual_stock_start_price * self.data['Cumulative_Return_Individual_Stock_Ajusted']
        self.data['Real_Nikkei_Index_Price'] = nikkei_index_start_price * self.data['Cumulative_Return_Nikkei_Index']

    def plot_stock_prices(self):
        # Y軸の値のフォーマット
        def price_formatter(x, pos):
            return f'{x:.0f} JPY'
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 日経平均の株価を左側の軸に設定
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Nikkei Stock Price (JPY)', color='tab:blue')
        if not self.display_only_ajusted_stock:
            ax1.plot(self.data.index, self.data['Real_Nikkei_Index_Price'], label='Real Stock Price Nikkei', color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.legend(loc='upper left')
        ax1.yaxis.set_major_formatter(FuncFormatter(price_formatter))  # 日経平均用のフォーマッター
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # X軸の日付フォーマット

        # 個別銘柄の株価を右側の軸に設定
        ax2 = ax1.twinx()
        ax2.set_ylabel('Individual Stock Price (JPY)', color='tab:orange')
        if not self.display_only_ajusted_stock:
            ax2.plot(self.data.index, self.data['Real_Individual_Stock_Price'], label='Real Stock Price', color='tab:orange')
        ax2.plot(self.data.index, self.data['Real_Individual_Stock_Price_Adjusted'], label='Beta Adjusted Real Stock Price', color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:orange')
        ax2.legend(loc='upper right')
        ax2.yaxis.set_major_formatter(FuncFormatter(price_formatter))  # 個別銘柄用のフォーマッター
        plt.show()

        plt.title(f'Comparison of Stock Prices: {self.individual_stock_symbol} and {self.nikkei_index_symbol}')
        fig.tight_layout()
        plt.show()

    def calculate_max_min_return(self, start_date, days = 90):
        end_date = start_date + timedelta(days=days)
        print("start = %s, end = %s" % (start_date, end_date))
        specific_period_data = self.data[(start_date <= self.data.index) & (self.data.index <= end_date)]

        period_prices = specific_period_data['Real_Individual_Stock_Price_Adjusted'] # Extract the relevant period of stock prices
        #print(period_prices)
        #print("-" * 10)

        start_price = period_prices.iloc[0]
        print(start_price)
        changes = ((period_prices / start_price) - 1) * 100 # Calculate percentage changes from the start price
        #print(changes)

        max_increase = np.max(changes)
        max_decrease = np.min(changes)  # More negative value indicates a larger drop

        # 最大増加と最大減少の日付を取得
        date_of_max_increase = period_prices.index[np.argmax(changes)]
        date_of_max_decrease = period_prices.index[np.argmin(changes)]

        # start_dateからの差分日数を計算
        days_to_max_increase = (date_of_max_increase - start_date).days
        days_to_max_decrease = (date_of_max_decrease - start_date).days

        return max_increase, max_decrease, days_to_max_increase, days_to_max_decrease


if __name__ == "__main__":
    analyzer = StockAnalyzer('8316.T')  # 例：三井住友銀行の銘柄コード
    analyzer.fetch_data()

    # 特定期間の最大上昇率と最大下降率を計算
    start_date = datetime(2021, 1, 1)
    max_increase, max_decrease, days_to_max_increase, days_to_max_decrease = analyzer.calculate_max_min_return(start_date)
    print(f"Max Increase: {max_increase}%, Days to Max Increase: {days_to_max_increase}")
    print(f"Max Decrease: {max_decrease}%, Days to Max Decrease: {days_to_max_decrease}")

    analyzer.plot_stock_prices()