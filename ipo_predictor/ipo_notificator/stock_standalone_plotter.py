import streamlit as st
import matplotlib.pyplot as plt

# グラフをプロット
class StockStandalonePlotter:
    def __init__(self, data, buy_signal_days, sell_signal_days, symbol, rsi_sell_threshold, rsi_buy_threshold):
        self.data = data
        self.buy_signal_days = buy_signal_days
        self.sell_signal_days = sell_signal_days
        self.symbol = symbol
        self.RSI_SELL_THRESHOLD = rsi_sell_threshold
        self.RSI_BUY_THRESHOLD = rsi_buy_threshold
    
    def plot(self):
        plt.figure(figsize=(14, 10))
        scatter_size = 60

        # 株価のグラフ
        plt.subplot(3, 1, 1)
        plt.plot(self.data.index, self.data['Close'], label='Close Price')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['Close'], color='green', label='Buy Signal', marker='^', alpha=1, s=scatter_size)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['Close'], color='red', label='Sell Signal', marker='v', alpha=1, s=scatter_size)
        plt.title(f'{self.symbol} Stock Price and Buy/Sell Signals')
        plt.legend()

        # MACDとシグナルラインのグラフ
        plt.subplot(3, 1, 2)
        plt.plot(self.data.index, self.data['MACD'], label='MACD')
        plt.plot(self.data.index, self.data['SignalLine'], label='Signal Line')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['MACD'], color='green', label='Buy Signal', marker='^', alpha=1, s=scatter_size)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['MACD'], color='red', label='Sell Signal', marker='v', alpha=1, s=scatter_size)
        plt.axhline(0, color='grey', linestyle='--')
        plt.title(f'{self.symbol} MACD and Signal Line')
        plt.legend()

        # RSIのグラフ
        plt.subplot(3, 1, 3)
        plt.plot(self.data.index, self.data['RSI'], label='RSI')
        plt.axhline(self.RSI_SELL_THRESHOLD, color='red', linestyle='--', label='Overbought')
        plt.axhline(self.RSI_BUY_THRESHOLD, color='green', linestyle='--', label='Oversold')
        plt.scatter(self.buy_signal_days.index, self.buy_signal_days['RSI'], color='green', label='Buy Signal', marker='^', alpha=1, s=scatter_size)
        plt.scatter(self.sell_signal_days.index, self.sell_signal_days['RSI'], color='red', label='Sell Signal', marker='v', alpha=1, s=scatter_size)
        plt.title(f'{self.symbol} RSI')
        plt.legend()

        plt.tight_layout()
        st.pyplot(plt)
