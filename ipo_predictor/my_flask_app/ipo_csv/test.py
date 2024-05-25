import requests
from bs4 import BeautifulSoup
import csv
import re

# データを取得するURLリスト
urls = [
    'https://www.ipokiso.com/company/2024/logos-holdings.html'
]

def extract_company_data(url):
    # HTTPリクエストを送信してHTMLを取得
    response = requests.get(url)
    html = response.content

    # BeautifulSoupを使ってHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')

    # 会社名
    company_name_tag = soup.find(string=re.compile("会社名"))
    company_name = company_name_tag.find_next().text.strip() if company_name_tag else ''

    # 会社URL
    company_url_tag = soup.find(string=re.compile("会社URL"))
    company_url = company_url_tag.find_next().text.strip() if company_url_tag else ''

    # 会社設立
    company_establishment_tag = soup.find(string=re.compile("会社設立"))
    company_establishment = company_establishment_tag.find_next().text.strip() if company_establishment_tag else ''

    # 上場日
    listing_date_tag = soup.find(string=re.compile("上場日"))
    listing_date = listing_date_tag.find_next().text.strip() if listing_date_tag else ''

    # 株主名と比率
    shareholder_table_tag = soup.find(string=re.compile("株主構成"))
    shareholders = []
    if shareholder_table_tag:
        shareholder_table = shareholder_table_tag.find_next('table')
        for row in shareholder_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].text.strip()
                ratio = cols[1].text.strip()
                shareholders.append(f"{name} {ratio}")

    # 企業業績のデータ（5年分）
    performance_table_tag = soup.find(string=re.compile("企業業績のデータ"))
    performance_data = []
    if performance_table_tag:
        performance_table = performance_table_tag.find_next('table')
        for row in performance_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            year_data = [col.text.strip() for col in cols]
            performance_data.append(year_data)

    return {
        "company_name": company_name,
        "company_url": company_url,
        "company_establishment": company_establishment,
        "listing_date": listing_date,
        "shareholders": "; ".join(shareholders),
        "performance_data": performance_data
    }

# TSVファイルにデータを書き込む
with open('company_data.tsv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['会社名', '会社URL', '会社設立', '上場日', '株主名と比率', '企業業績のデータ（5年分）'])

    for url in urls:
        data = extract_company_data(url)
        performance_data = "; ".join([", ".join(year) for year in data['performance_data']])
        writer.writerow([
            data['company_name'],
            data['company_url'],
            data['company_establishment'],
            data['listing_date'],
            data['shareholders'],
            performance_data
        ])

print("データの取得と書き込みが完了しました。")

