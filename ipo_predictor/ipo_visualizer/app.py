import streamlit as st
import pandas as pd
from stock_analyzer import StockAnalyzer
from stock_web_plotter import StockWebPlotter

class StockApp:
    def __init__(self):
        self.ipo_companies = {
            #'2516': '東証グロース250',
            '160A': 'アズパートナーズ',
            '5588': 'ファーストアカウンティング',
            '9158': 'シーユーシー',
            '9166': 'ＧＥＮＤＡ',
            '3496': 'アズーム',
            '212A': 'フィットイージー',
            '215A': 'タイミー'
        }
        self.symbol_examples = ', '.join([key + '.T' for key in self.ipo_companies.keys()])
        self.symbols = st.text_input('Enter stock symbols (comma separated)', self.symbol_examples)
        self.start_date = st.date_input('Start Date', pd.to_datetime('2024-01-01'))
        self.end_date = st.date_input('End Date', pd.to_datetime('today'))
        self.RSI_SELL_THRESHOLD = st.slider('RSI Sell Threshold', 50, 100, 65)
        self.RSI_BUY_THRESHOLD = st.slider('RSI Buy Threshold', 0, 50, 35)
        self.DAYS_AFTER_RSI = st.slider('Days After RSI', 1, 30, 15)
        self.columns_option = st.selectbox('Select number of columns', [2, 1])
        self.is_regression_analysis = st.selectbox('Regression analysis by growth stock index', [True, False])
        self.analyzer = StockAnalyzer(self.start_date, self.end_date, self.RSI_SELL_THRESHOLD, self.RSI_BUY_THRESHOLD, self.DAYS_AFTER_RSI, self.is_regression_analysis)

    def analyze_stock(self, symbol):
        self.analyzer.calculate(symbol)
        buy_signal_days, sell_signal_days = self.analyzer.get_signals()
        stock_info = self.analyzer.get_stock_info()
        return buy_signal_days, sell_signal_days, self.analyzer.data, stock_info

    def display_stock(self, company_code, company_name, buy_signal_days, sell_signal_days, data, stock_info):
        with st.container():
            next_earnings_date = stock_info['next_earnings_date']
            per = stock_info['per']
            turnover_rate = stock_info['turnover_rate']  # 売買回転率を取得

            markdown_head_str = f"""
            <div style='border: 2px solid; padding: 10px; margin: 10px;'>
            <span><h3>{company_code} - {company_name}</h3><a href='https://irbank.net/{company_code}/per'>PER: {per}</a>, 売買回転率: {turnover_rate}, 決算予定：{next_earnings_date}</span>"""
            st.markdown(markdown_head_str, unsafe_allow_html=True)
            plotter = StockWebPlotter(data, buy_signal_days, sell_signal_days, company_code, self.RSI_SELL_THRESHOLD, self.RSI_BUY_THRESHOLD, self.is_regression_analysis)
            plotter.plot()
            st.markdown("</div>", unsafe_allow_html=True)

    def run(self):
        if st.button('Analyze'):
            symbols = self.symbols.split(',')
            
            if self.columns_option == 1:
                for symbol in symbols:
                    symbol = symbol.strip()
                    company_code = symbol.split('.')[0]
                    company_name = self.ipo_companies.get(company_code, 'Unknown')
                    buy_signal_days, sell_signal_days, data, stock_info = self.analyze_stock(symbol)
                    self.display_stock(company_code, company_name, buy_signal_days, sell_signal_days, data, stock_info)
            elif self.columns_option == 2:
                col1, col2 = st.columns(2)
                
                for idx, symbol in enumerate(symbols):
                    symbol = symbol.strip()
                    company_code = symbol.split('.')[0]
                    company_name = self.ipo_companies.get(company_code, 'Unknown')
                    buy_signal_days, sell_signal_days, data, stock_info = self.analyze_stock(symbol)
                    
                    if idx % 2 == 0:
                        with col1:
                            self.display_stock(company_code, company_name, buy_signal_days, sell_signal_days, data, stock_info)
                    else:
                        with col2:
                            self.display_stock(company_code, company_name, buy_signal_days, sell_signal_days, data, stock_info)

# Streamlitインターフェース
st.set_page_config(layout="wide")
st.title('Stock Analyzer and Plotter')

app = StockApp()
app.run()
