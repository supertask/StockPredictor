import streamlit as st
import pandas as pd
from stock_analyzer import StockAnalyzer
from stock_standalone_plotter import StockStandalonePlotter as StockPlotter

def analyze_stock(symbol, start_date, end_date, rsi_sell_threshold, rsi_buy_threshold, days_after_rsi):
    analyzer = StockAnalyzer(symbol, start_date, end_date, rsi_sell_threshold, rsi_buy_threshold, days_after_rsi)
    analyzer.download_data()
    analyzer.calculate_macd()
    analyzer.calculate_rsi()
    analyzer.identify_signals()
    buy_signal_days, sell_signal_days = analyzer.get_signals()
    return buy_signal_days, sell_signal_days, analyzer.data

def display_stock(symbol, buy_signal_days, sell_signal_days, data, rsi_sell_threshold, rsi_buy_threshold):
    with st.container():
        st.markdown(f"<div><h2>{symbol}</h2>", unsafe_allow_html=True)
        plotter = StockPlotter(data, buy_signal_days, sell_signal_days, symbol, rsi_sell_threshold, rsi_buy_threshold)
        plotter.plot()
        st.markdown("</div>", unsafe_allow_html=True)

# Streamlitインターフェース
st.set_page_config(layout="wide")
st.title('Stock Analyzer and Plotter')

symbols = st.text_input('Enter stock symbols (comma separated)', '2516.T, 160A.T, 5588.T, 9158.T, 9166.T, 3496.T')
start_date = st.date_input('Start Date', pd.to_datetime('2023-01-01'))
end_date = st.date_input('End Date', pd.to_datetime('2024-07-12'))
RSI_SELL_THRESHOLD = st.slider('RSI Sell Threshold', 50, 100, 65)
RSI_BUY_THRESHOLD = st.slider('RSI Buy Threshold', 0, 50, 35)
DAYS_AFTER_RSI = st.slider('Days After RSI', 1, 30, 15)

# 列数を選択するセレクトボックスを追加
columns_option = st.selectbox('Select number of columns', [2, 1])

if st.button('Analyze'):
    symbols = symbols.split(',')

    if columns_option == 1:
        for symbol in symbols:
            symbol = symbol.strip()
            buy_signal_days, sell_signal_days, data = analyze_stock(symbol, start_date, end_date, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD, DAYS_AFTER_RSI)
            display_stock(symbol, buy_signal_days, sell_signal_days, data, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD)
    elif columns_option == 2:
        col1, col2 = st.columns(2)
        
        for idx, symbol in enumerate(symbols):
            symbol = symbol.strip()
            buy_signal_days, sell_signal_days, data = analyze_stock(symbol, start_date, end_date, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD, DAYS_AFTER_RSI)
            
            if idx % 2 == 0:
                with col1:
                    display_stock(symbol, buy_signal_days, sell_signal_days, data, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD)
            else:
                with col2:
                    display_stock(symbol, buy_signal_days, sell_signal_days, data, RSI_SELL_THRESHOLD, RSI_BUY_THRESHOLD)