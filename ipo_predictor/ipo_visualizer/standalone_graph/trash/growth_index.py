import yfinance as yf

ticker_symbol = "2516.T"
index_data = yf.Ticker(ticker_symbol)
historical_data = index_data.history(period="1y")
print(historical_data)
