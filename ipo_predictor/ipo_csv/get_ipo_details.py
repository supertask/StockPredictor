import requests
from bs4 import BeautifulSoup
import os
import csv
import re
import json
import locale
import datetime

current_year = datetime.datetime.now().year
past_year = 2020
years = range(past_year, current_year + 1)


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
base_url = 'https://www.ipokiso.com'

# 文字列を数値に変換する関数
def string_to_float(value):
    try:
        return locale.atof(value)
    except ValueError:
        return None

def clean_value(value, company_name, relative_url):
    try:
        value = value.replace(",", "")
        if value == "-" or value == "(-)" or "（-）":
            return None
        elif value.startswith("△"):
            return -float(value[1:])
        elif (value.startswith("（") and value.endswith("）")) or (value.startswith("(") and value.endswith(")")):
            value = value[1:-1]
            if value.startswith("△"):
                return -float(value[1:])
            else:
                return float(value)
        else:
            return float(value)
    except ValueError as e:
        print(f"ValueError for {company_name} at {base_url}{relative_url}: {e}")
        return None
        


def clean_shareholder_ratio(shareholders, relative_url):
    try:
        for shareholder in shareholders:
            ratio_str = shareholder["比率"].replace(",", ".")  # サイト上の表記が間違えている時があるため、カンマをピリオドに置換
            if ratio_str.endswith("％") or ratio_str.endswith("%"):
                ratio_str = ratio_str[:-1]  # Remove the "％" character
            
            shareholder["比率"] = float(ratio_str)
            shareholder["isCEO"] = "社長" in shareholder["株主名"]
        return shareholders
    except ValueError as e:
        print(f"Error cleaning shareholder ratio for {base_url}{relative_url}: {e}")
        return []

def is_increasing(data, normalized_tolerance = 0.2):
    prev_value = None
    
    for key, value in data.items():
        if value is None:
            continue
        
        if prev_value is not None:
            tolerance_value = prev_value * normalized_tolerance
            if value < prev_value - tolerance_value:
                return False
        
        prev_value = value
    
    return True

def extract_company_data(relative_url):
    url = f'{base_url}{relative_url}'
    
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    company_name_tag = soup.find(string=re.compile("会社名"))
    company_name = company_name_tag.find_next().text.strip() if company_name_tag else ''

    company_url_tag = soup.find(string=re.compile("会社URL"))
    company_url = company_url_tag.find_next().text.strip() if company_url_tag else ''

    company_establishment_tag = soup.find(string=re.compile("会社設立"))
    company_establishment = company_establishment_tag.find_next().text.strip() if company_establishment_tag else ''

    listing_date = ''
    listing_date_tag = soup.find(string=re.compile("上場日"))
    if (listing_date_tag):
        listing_date = listing_date_tag.find_next('td').text.strip()

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

    shareholders = clean_shareholder_ratio(shareholders, relative_url)

    performance_table_tags = soup.find_all('table', class_='kobetudate04')
    performance_data = []
    indicators = []
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
                    row_data[first_col_header][year] = clean_value(cols[i + 1].text.strip(), company_name, relative_url)

                is_rising_steadily = is_increasing(row_data[first_col_header])
                performance_data.append(row_data)
                if first_col_header == "売上高（百万円）" and is_rising_steadily:
                    indicators.append("売上↗︎")
                if first_col_header == "経常利益（百万円）" and is_rising_steadily:
                    indicators.append("経常利益↗︎")
                if first_col_header == "当期純利益（百万円）" and is_rising_steadily:
                    indicators.append("純利益↗︎")

    business_content = ''
    for p_tag in soup.find_all('p'):
        match = re.search(r'事業内容は「(.*?)」で', p_tag.text)
        if match:
            business_content = match.group(1)
            break

    admin_comment = ''
    admin_comment_tag = soup.find('h2', string='管理人からのコメント')
    if admin_comment_tag:
        next_p_tag = admin_comment_tag.find_next('p')
        if next_p_tag:
            admin_comment = next_p_tag.text.strip()

    captial_threshold = 250
    market_capital = ''
    for p_tag in soup.find_all('p'):
        match = re.search(r'想定時価総額([\d,]+\.\d+)億円', p_tag.text)
        if match:
            market_capital_value = string_to_float(match.group(1))
            market_capital = market_capital_value

            if market_capital_value and market_capital_value <= captial_threshold:
                indicators.append("\n時価%s億↓" % captial_threshold)
            break

    for shareholder in shareholders:
        if shareholder["isCEO"] and shareholder["比率"] > 10:
            ceo_stock = "社長株" + str(shareholder["比率"]) + "%"
            indicators.append("\n" + ceo_stock)
            break

    securities_report_url = ''
    for a_tag in soup.find_all('a', href=True):
        if 'https://disclosure2dl.edinet-fsa.go.jp/searchdocument/' in a_tag['href']:
            securities_report_url = a_tag['href']
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
        "admin_comment": admin_comment,
        "ten_bagger_indicators": "".join(indicators),
        "securities_report_url": securities_report_url
    }

for year in years:
    input_file = f'data/companies_{year}.tsv'
    output_file = f'data/companies_{year}_detail.tsv'
    
    if os.path.exists(output_file):
        print(f"{year}年の出力ファイルが既に存在するため、処理をスキップします。")
        continue

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        
        header = next(reader)
        writer.writerow([
            '買', '企業名', 'コード', 'ビジネスモデル', '17業種', '33業種',
            'テンバガー指標', 'ノーバガー指標', 'PER', '何倍株か', '決算', '決算伸び率%',
            'IPO情報URL', '有価証券報告書', 'IR', '事業内容',
            '想定時価総額（億円）', '会社設立', '上場日','市場', '株主名と比率',
            '企業業績のデータ（5年分）', '管理人からのコメント', '会社URL'
        ])
        
        market_name_re = r'【([^】]+)】'

        for index, row in enumerate(reader):
            if len(row) == 3:
                relative_url = row[2]
                data = extract_company_data(relative_url)

                match_market_name = re.search(market_name_re, data['company_name'])
                market_name = match_market_name.group(1) if match_market_name else ""

                company_name, code, ipo_info_url = row
                full_ipo_info_url = f'{base_url}{ipo_info_url}'

                writer.writerow([
                    "", company_name, code, "", "", "",
                    "", "", "", "", "", "",
                    full_ipo_info_url, data['securities_report_url'], "https://irbank.net/" + code + "/ir", data['business_content'],
                    data['market_capital'], data['company_establishment'], data['listing_date'], market_name, data['shareholders'],
                    data['performance_data'], data['admin_comment'], data['company_url']
                ])

    print(f"{year}データの取得と書き込みが完了しました。")
