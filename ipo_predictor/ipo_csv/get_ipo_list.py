import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

# 対象とする年のリスト
current_year = datetime.now().year
past_year = 2015
years = range(past_year, current_year + 1)


def get_company_data_from_2018():
    tables = soup.find_all('table')
    company_data = []
    for table in tables:
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                company_info = columns[0].text.strip()
                #print(company_info)
                if company_info:  # 企業名が空でない場合のみ処理する
                    company_name = re.split(r'\n|\（|\）', company_info)[0].strip()
                    company_code = re.search(r'[\(（](.*?)[\)）]', company_info)
                    company_code = company_code.group(1) if company_code else ''
                    company_urls = columns[0].find_all('a')
                    company_url = company_urls[0]['href']
                    company_data.append([company_name, company_code, company_url])
    return company_data

def get_company_data_before_2018():
    tables = soup.find_all('table')
    company_data = []
    for table in tables:
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                company_info = columns[1].text.strip()
                #print(company_info)
                if company_info:  # 企業名が空でない場合のみ処理する
                    company_name = re.split(r'\n|\（|\）', company_info)[0].strip()
                    company_code = re.search(r'[\(（](.*?)[\)）]', company_info)
                    company_code = company_code.group(1) if company_code else ''
                    company_urls = columns[1].find_all('a')
                    company_url = company_urls[0]['href']
                    company_data.append([company_name, company_code, company_url])
                #print("company_name, company_code, company_url = %s, %s, %s" % (company_name, company_code, company_url))
    return company_data

for year in years:
    # 年に対応するURLを生成
    url = 'https://www.ipokiso.com/company/' if year == current_year else f'https://www.ipokiso.com/company/{year}.html' 

    # HTTPリクエストを送信してHTMLを取得
    response = requests.get(url)
    html = response.content

    # BeautifulSoupを使ってHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')

    # 企業名とそのURLを格納するリスト
    if year >= 2018:
        company_data = get_company_data_from_2018()
    else:
        company_data = get_company_data_before_2018()
        

    # TSVファイルにデータを書き込む
    file_name = f'output/urls/companies_{year}.tsv'
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['企業名', 'コード', 'URL'])
        writer.writerows(company_data)

    print(f"{year}年のデータの取得と書き込みが完了しました。")

