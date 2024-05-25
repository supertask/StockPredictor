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

def clean_value(value):
    value = value.replace(",", "")
    if value == "-":
        return None
    elif value.startswith("△"):
        return -float(value[1:])
    elif value.startswith("（") and value.endswith("）"):
        value = value[1:-1]
        if value.startswith("△"):
            return -float(value[1:])
        else:
            return float(value)
    else:
        return float(value)


def clean_shareholder_ratio(shareholders):
    for shareholder in shareholders:
        ratio_str = shareholder["比率"]
        if ratio_str.endswith("％"):
            ratio_str = ratio_str[:-1]  # Remove the "％" character
        shareholder["比率"] = float(ratio_str)
        shareholder["isCEO"] = "社長" in shareholder["株主名"]
    return shareholders

def is_increasing(trend_data):
    values = [v for v in trend_data.values() if v is not None]
    return all(x < y for x, y in zip(values, values[1:]))

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
    listing_date = ''
    listing_date_tag = soup.find(string=re.compile("上場日"))
    if listing_date_tag:
        listing_date = listing_date_tag.find_next('td').text.strip()

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

    shareholders = clean_shareholder_ratio(shareholders)


    # 企業業績のデータ（5年分）
    performance_table_tags = soup.find_all('table', class_='kobetudate04')
    performance_data = []
    if len(performance_table_tags) >= 2:
        performance_table = performance_table_tags[1]
        years = [td.text.strip() for td in performance_table.find('tr').find_all('td')[1:]]
        for row in performance_table.find_all('tr')[1:]:
            first_col = row.find_all('th')[0]
            cols = row.find_all('td')
            if len(cols) > 1:
                first_col_header = first_col.text.strip()
                row_data = {first_col_header: {}}
                for i, year in enumerate(years):
                    year = year.replace("\r\n", "")
                    row_data[first_col_header][year] = clean_value(cols[i + 1].text.strip())
                row_data["右肩あがりか"] = is_increasing(row_data[first_col_header])
                performance_data.append(row_data)


    # 事業内容
    business_content = ''
    for p_tag in soup.find_all('p'):
        match = re.search(r'事業内容は「(.*?)」', p_tag.text)
        if match:
            business_content = match.group(1)
            break

    # 管理人からのコメント
    admin_comment = ''
    admin_comment_tag = soup.find('h2', string='管理人からのコメント')
    if admin_comment_tag:
        next_p_tag = admin_comment_tag.find_next('p')
        if next_p_tag:
            admin_comment = next_p_tag.text.strip()

    # 想定時価総額
    market_capital = ''
    for p_tagclean_value in soup.find_all('p'):
        match = re.search(r'想定時価総額(\d+\.\d+)(億|万)円', p_tag.text)
        if match:
            market_capital = match.group(1) + match.group(2) + '円'
            break


    return {
        "company_name": company_name,
        "company_url": company_url,
        "company_establishment": company_establishment,
        "market_capital": market_capital,
        "listing_date": listing_date,
        "shareholders": json.dumps(shareholders, ensure_ascii=False),
        "performance_data": json.dumps(performance_data, ensure_ascii=False),
        "business_content": business_content,
        "admin_comment": admin_comment
    }


# TSVファイルにデータを書き込む
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter='\t')
    
    header = next(reader)
    writer.writerow([
        '企業名', 'コード', '市場', '想定時価総額', '会社設立', '上場日',
        '株主名と比率', '企業業績のデータ（5年分）', '事業内容', '管理人からのコメント',
        '会社URL', 'IPO情報URL'
    ])

    market_name_re = r'【([^】]+)】'


    for index, row in enumerate(reader):
        if len(row) == 3:
            relative_url = row[2]
            data = extract_company_data(relative_url)

            match_market_name = re.search(market_name_re, data['company_name'])
            market_name = match_market_name.group(1) if match_market_name else ""

            company_name, code, ipo_info_url = row

            writer.writerow([
                company_name, code, market_name, data['market_capital'], data['company_establishment'], data['listing_date'],
                data['shareholders'],data['performance_data'], data['business_content'], data['admin_comment'],
                data['company_url'], ipo_info_url,
            ])

        if index > 5: break

print("データの取得と書き込みが完了しました。")
