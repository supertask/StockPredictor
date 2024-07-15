import streamlit as st
import plotly.graph_objs as go
import plotly.express as px

# グラフをプロット
class StockWebPlotter:
    
    def __init__(self, data, buy_signal_days, sell_signal_days, symbol, rsi_sell_threshold, rsi_buy_threshold):
        self.data = data
        self.buy_signal_days = buy_signal_days
        self.sell_signal_days = sell_signal_days
        self.symbol = symbol
        self.RSI_SELL_THRESHOLD = rsi_sell_threshold
        self.RSI_BUY_THRESHOLD = rsi_buy_threshold
    
    def add_custom_css(self):
        st.markdown(
            """
            <style>
            .element-container {
                margin-bottom: 0.0rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    def plot(self):
        self.add_custom_css()
        
        scatter_size = 10
        green_hex = '#00FF00'
        margin = dict(t=0, b=0)
        height = 200  # 各グラフの高さを300に設定

        
        # 株価のグラフ
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=self.data.index, y=self.data['Close'], mode='lines', name='Close Price'))
        fig1.add_trace(go.Scatter(x=self.buy_signal_days.index, y=self.buy_signal_days['Close'], mode='markers', name='Buy Signal', marker=dict(color=green_hex, symbol='triangle-up', size=scatter_size)))
        fig1.add_trace(go.Scatter(x=self.sell_signal_days.index, y=self.sell_signal_days['Close'], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=scatter_size)))
        #fig1.update_layout(title=f'{self.symbol} Stock Price and Buy/Sell Signals', xaxis_title='Date', yaxis_title='Price', margin=dict(t=20, b=20))
        fig1.update_layout(yaxis_title='Price', margin=margin, height=height)

        st.plotly_chart(fig1)

        # MACDとシグナルラインのグラフ
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=self.data.index, y=self.data['MACD'], mode='lines', name='MACD'))
        fig2.add_trace(go.Scatter(x=self.data.index, y=self.data['SignalLine'], mode='lines', name='Signal Line'))
        fig2.add_trace(go.Scatter(x=self.buy_signal_days.index, y=self.buy_signal_days['MACD'], mode='markers', name='Buy Signal', marker=dict(color=green_hex, symbol='triangle-up', size=scatter_size)))
        fig2.add_trace(go.Scatter(x=self.sell_signal_days.index, y=self.sell_signal_days['MACD'], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=scatter_size)))
        fig2.add_hline(y=0, line=dict(color='grey', dash='dash'))
        #fig2.update_layout(title=f'{self.symbol} MACD and Signal Line', xaxis_title='Date', yaxis_title='MACD & Signal value', margin=dict(t=20, b=20))
        fig2.update_layout(yaxis_title='MACD & Signal value', margin=margin, height=height)

        st.plotly_chart(fig2)

        # RSIのグラフ
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=self.data.index, y=self.data['RSI'], mode='lines', name='RSI'))
        fig3.add_hline(y=self.RSI_SELL_THRESHOLD, line=dict(color='red', dash='dash'), name='Overbought')
        fig3.add_hline(y=self.RSI_BUY_THRESHOLD, line=dict(color=green_hex, dash='dash'), name='Oversold')
        fig3.add_trace(go.Scatter(x=self.buy_signal_days.index, y=self.buy_signal_days['RSI'], mode='markers', name='Buy Signal', marker=dict(color=green_hex, symbol='triangle-up', size=scatter_size)))
        fig3.add_trace(go.Scatter(x=self.sell_signal_days.index, y=self.sell_signal_days['RSI'], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=scatter_size)))
        #fig3.update_layout(title=f'{self.symbol} RSI', xaxis_title='Date', yaxis_title='RSI', margin=dict(t=20, b=20))
        fig3.update_layout(yaxis_title='RSI', margin=margin, height=height)

        st.plotly_chart(fig3)
