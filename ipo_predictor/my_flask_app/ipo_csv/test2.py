import requests
from bs4 import BeautifulSoup
import csv
import re
import json

# 元のTSVファイルを読み込む
input_file = 'data/companies.tsv'
base_url = 'https://www.ipokiso.com'

# 出力ファイル
output_file = 'data/companies_detail.tsv'

def extract_company_data(relative_url):
    # フルURLを作成
    url = f'{base_url}{relative_url}'
    
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
    shareholder_table = soup.find('table', class_='kobetudate05')
    shareholders = []
    if shareholder_table:
        for row in shareholder_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].text.strip()
                ratio = cols[1].text.strip()
                lockup = cols[2].text.strip()
                shareholders.append({"株主名": name, "比率": ratio, "ロックアップ": lockup})

    # 企業業績のデータ（5年分）
    performance_table_tags = soup.find_all('table', class_='kobetudate04')
    performance_data = {}
    if len(performance_table_tags) >= 2:
        performance_table = performance_table_tags[1]
        headers = [th.text.strip() for th in performance_table.find_all('th')]
        for row in performance_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == len(headers):
                for i, header in enumerate(headers):
                    year_data = performance_data.get(header, [])
                    year_data.append([cols[0].text.strip(), cols[i].text.strip()])
                    performance_data[header] = year_data

    return {
        "company_name": company_name,
        "company_url": company_url,
        "company_establishment": company_establishment,
        "listing_date": listing_date,
        "shareholders": json.dumps(shareholders, ensure_ascii=False),
        "performance_data": json.dumps(performance_data, ensure_ascii=False)
    }

# TSVファイルにデータを書き込む
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter='\t')
    
    header = next(reader)
    writer.writerow(['企業名', 'コード', 'URL', '会社名', '会社URL', '会社設立', '上場日', '株主名と比率', '企業業績のデータ（5年分）'])
    
    for row in reader:
        if len(row) == 3:
            relative_url = row[2]
            data = extract_company_data(relative_url)
            writer.writerow(row + [
                data['company_name'],
                data['company_url'],
                data['company_establishment'],
                data['listing_date'],
                data['shareholders'],
                data['performance_data']
            ])

print("データの取得と書き込みが完了しました。")
