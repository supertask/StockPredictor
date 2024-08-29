import yfinance as yf
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('JQUANTS_API_KEY')

def fetch_stock_data(ticker):
    stock_data = yf.download(ticker, start='2020-01-01', end='2023-01-01')
    data = []
    for index, row in stock_data.iterrows():
        data.append({'date': index.strftime('%Y-%m-%d'), 'adjusted_price': row['Adj Close']})
    return data

def fetch_disclosure_data():
    url = f'https://api.jquants.com/v1/disclosures?apikey={API_KEY}&start_date=2020-01-01&end_date=2023-01-01'
    response = requests.get(url)
    disclosures = response.json()
    data = []
    for disclosure in disclosures:
        date = datetime.strptime(disclosure['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
        data.append({'date': date, 'title': disclosure['title'], 'link': disclosure['link']})
    return data
