import requests
import os
import csv
import re
import json
import locale
import datetime
import time
import random
import yfinance as yf
from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.exceptions import HTTPError

current_year = datetime.datetime.now().year
past_year = 2015
years = range(past_year, current_year + 1)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
base_url = 'https://www.ipokiso.com'

sector_dict = {
    "Consumer Defensive": "消費者防衛",
    "Consumer Cyclical": "消費者循環",
    "Real Estate": "不動産",
    "Communication Services": "通信サービス",
    "Technology": "技術",
    "Healthcare": "ヘルスケア",
    "Industrials": "産業",
    "Financial Services": "金融サービス",
    "Basic Materials": "基礎材料",
    "Energy": "エネルギー"
}

industry_dict = {
    "Consumer Defensive": "消費者防衛",
    "Consumer Cyclical": "消費者循環",
    "Real Estate": "不動産",
    "Communication Services": "通信サービス",
    "Technology": "技術",
    "Healthcare": "ヘルスケア",
    "Industrials": "産業",
    "Financial Services": "金融サービス",
    "Basic Materials": "基礎材料",
    "Energy": "エネルギー",
    "Household & Personal Products": "家庭用品・個人用品",
    "Personal Services": "個人サービス",
    "Real Estate Services": "不動産サービス",
    "Entertainment": "娯楽",
    "Advertising Agencies": "広告代理店",
    "Electronic Gaming & Multimedia": "電子ゲーム・マルチメディア",
    "Telecom Services": "電気通信サービス",
    "Software - Infrastructure": "ソフトウェア - インフラストラクチャ",
    "Leisure": "レジャー",
    "Drug Manufacturers - Specialty & Generic": "医薬品メーカー - 専門・ジェネリック",
    "Internet Content & Information": "インターネットコンテンツ・情報",
    "Tools & Accessories": "ツール・アクセサリー",
    "Information Technology Services": "情報技術サービス",
    "REIT - Hotel & Motel": "REIT - ホテル・モーテル",
    "Software - Application": "ソフトウェア - アプリケーション",
    "Specialty Business Services": "専門ビジネスサービス",
    "Credit Services": "信用サービス",
    "Banks - Regional": "銀行 - 地域",
    "Insurance - Life": "保険 - 生命",
    "Restaurants": "レストラン",
    "Biotechnology": "バイオテクノロジー",
    "Publishing": "出版",
    "Internet Retail": "インターネット小売",
    "Engineering & Construction": "工学・建設",
    "Apparel Retail": "衣料品小売",
    "Building Materials": "建材",
    "Packaged Foods": "包装食品",
    "REIT - Residential": "REIT - 住宅",
    "Oil & Gas Refining & Marketing": "石油・ガス精製・販売",
    "Medical Instruments & Supplies": "医療機器・用品",
    "Specialty Industrial Machinery": "特殊産業機械",
    "Electronic Components": "電子部品",
    "Staffing & Employment Services": "人材派遣・雇用サービス",
    "REIT - Diversified": "REIT - 多様化",
    "Resorts & Casinos": "リゾート・カジノ",
    "Electronic Components": "電子部品",
    "Electronics & Computer Distribution": "電子機器・コンピュータ流通",
    "Residential Construction": "住宅建設",
    "Semiconductors": "半導体",
    "REIT - Healthcare Facilities": "REIT - 医療施設",
    "Farm Products": "農産物",
    "Asset Management": "資産運用",
    "Specialty Chemicals": "特殊化学品"
}

def get_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.readline().strip()
        return token
    except Exception as e:
        print(f"Error reading token from file: {e}")
        return None

refresh_token = get_token_from_file(".token/jquants_refresh_token")

# 文字列を数値に変換する関数
def string_to_float(value):
    try:
        return locale.atof(value)
    except ValueError:
        return None

def clean_value(value, company_name, relative_url):
    try:
        if value == "-" or value == "(-)" or value == "（-）":
            return None
        else:
            value = value.strip('()（）%％')
            value = value.replace(",", "").replace('△', '-')
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

#def get_id_token(refresh_token):
#    r_post = requests.post(
#        f"https://api.jquants.com/v1/token/auth_refresh?refreshtoken={refresh_token}"
#    )
#    id_token = r_post.json()['idToken']
#    return id_token
#
#def get_jquants_company_info(code, id_token):
#    try:
#        url = f"https://api.jquants.com/v1/listed/info?code={code}"
#        headers = {
#            "Authorization": f"Bearer {id_token}"
#        }
#        response = requests.get(url, headers=headers)
#        response.raise_for_status()
#        
#        json_response = response.json()
#        print(json_response)
#
#        info = json_response.get("info", [])
#        if info and len(info) > 0:
#            company_info = info[0]
#            return [company_info.get("Sector17CodeName"), company_info.get("Sector33CodeName")]
#        else:
#            return ['None3', 'None3']
#    
#    except requests.exceptions.RequestException as e:
#        print(f"Error getting company info for code {code}: {e}")
#        return ['None4', 'None4']

#
# セクター、産業、上場しているかを返す
#
def get_company_info(code):
    symbol = code + ".T"
    try:
        ticker = yf.Ticker(symbol)
        ticker_info = ticker.info
        if not ticker_info:
            return ["None1", "None1", False]
        hist = ticker.history(period="1d")
        if hist.empty:
            #sector, industry = get_jquants_company_info(code, id_token)
            return ["上場廃止", "上場廃止", False]
    except Exception as e:
        print(f"Error retrieving data for {symbol}: {e}")
        return ["None2", "None2", False]
    
    sector = ticker_info.get('sector', f'{symbol}のセクター情報が見つかりませんでした')
    industry = ticker_info.get('industry', f'{symbol}の業界情報が見つかりませんでした')
    
    sector = sector_dict.get(sector, sector)
    industry = industry_dict.get(industry, industry)
    
    return [sector, industry, True]

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
        performance_table = performance_table_tags[-1]
        #print(performance_table)

        years = [td.text.strip() for td in performance_table.find('tr').find_all('td')[1:]]

        for row in performance_table.find_all('tr')[1:]:
            header_columns = row.find_all('th')
            columns = row.find_all('td')
            if len(header_columns) == 0:
                first_column = columns[0]
                #print("No header_columns: %s, row: %s, URL: %s. " % (first_column, row, url) )
            else:
                first_column = header_columns[0]
            if len(columns) > 1:
                first_col_header = first_column.text.strip()
                row_data = {first_col_header: {}}
                for i, year in enumerate(years):
                    year = year.replace("\r\n", "")
                    cell = columns[i + 1].text.strip()
                    cleaned_cell = clean_value(cell, company_name, relative_url)
                    #print("before: %s, after: %s" % (cell, cleaned_cell))
                    row_data[first_col_header][year] = cleaned_cell
                performance_data.append(row_data)

                #is_rising_steadily = is_increasing(row_data[first_col_header])
                #if first_col_header == "売上高（百万円）" and is_rising_steadily:
                #    indicators.append("売上↗︎")
                #if first_col_header == "経常利益（百万円）" and is_rising_steadily:
                #    indicators.append("経常利益↗︎")
                #if first_col_header == "当期純利益（百万円）" and is_rising_steadily:
                #    indicators.append("純利益↗︎")

        #print(performance_data)

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
    # DEBUG: 特定の年をデバッグする用
    if year != 2015: continue

    input_file = f'output/urls/companies_{year}.tsv'
    output_file = f'output/companies_{year}_detail.tsv'
    
    if os.path.exists(output_file):
        print(f"{year}年の出力ファイルが既に存在するため、処理をスキップします。")
        continue

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        
        header = next(reader)
        writer.writerow([
            '買', '企業名', 'コード', 'ビジネスモデル', 'テンバガー指標', 'ノーバガー指標',
            'PER', '何倍株か', 'Sector', 'Industry',
            'IPO情報URL', 'IR', '事業内容', '上場1年以内での最低時価総額', '有価証券報告書', 
            '決算', '決算伸び率%', '想定時価総額（億円）', '会社設立', '上場日','市場', '株主名と比率',
            '企業業績のデータ（5年分）', '管理人からのコメント', '会社URL'
        ])
        
        market_name_re = r'【([^】]+)】'
        #id_token = get_id_token(refresh_token)

        rows = list(reader)
        for index, row in enumerate(tqdm(rows, desc="Processing")):
            if len(row) == 3:
                relative_url = row[2]
                data = extract_company_data(relative_url)

                match_market_name = re.search(market_name_re, data['company_name'])
                market_name = match_market_name.group(1) if match_market_name else ""

                company_name, code, ipo_info_url = row
                full_ipo_info_url = f'{base_url}{ipo_info_url}'
                ir_url = "https://irbank.net/" + code + "/ir"
                sector, industry, is_listed = get_company_info(code)

                writer.writerow([
                    "", company_name, code, "", "", "",
                    "", "", sector, industry,
                    full_ipo_info_url, ir_url, data['business_content'], "", data['securities_report_url'],
                    "", "", data['market_capital'], data['company_establishment'], data['listing_date'], market_name, data['shareholders'],
                    data['performance_data'], data['admin_comment'], data['company_url']
                ])

                #time.sleep(random.uniform(0.02, 0.1))
            

    print(f"{year}データの取得と書き込みが完了しました。")
