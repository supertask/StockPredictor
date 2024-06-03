import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import locale

# 元のTSVファイルを読み込む
input_file = 'data/companies.tsv'
base_url = 'https://www.ipokiso.com'

# 出力ファイル
output_file = 'data/companies_detail.tsv'

# ロケールを設定
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# 文字列を数値に変換する関数
def string_to_float(value):
    try:
        return locale.atof(value)
    except ValueError:
        return None

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

#def is_increasing(trend_data):
#    values = [v for v in trend_data.values() if v is not None]
#    return all(x < y for x, y in zip(values, values[1:]))

#
# tolerance = 0.0 ~ 1.0
#
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
                    row_data[first_col_header][year] = clean_value(cols[i + 1].text.strip())
                is_rising_steadily = is_increasing(row_data[first_col_header])
                #row_data["右肩あがりか"] = rising_steadily

                performance_data.append(row_data)
                if first_col_header == "売上高（百万円）" and is_rising_steadily:
                    indicators.append("売上↗︎")
                if first_col_header == "経常利益（百万円）" and is_rising_steadily:
                    indicators.append("経常利益↗︎")
                if first_col_header == "当期純利益（百万円）" and is_rising_steadily:
                    indicators.append("純利益↗︎")

    # 事業内容
    business_content = ''
    for p_tag in soup.find_all('p'):
        match = re.search(r'事業内容は「(.*?)」で', p_tag.text)
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

    # 株主のCEO比率判定
    for shareholder in shareholders:
        if shareholder["isCEO"] and shareholder["比率"] > 10:
            ceo_stock = "社長株" + str(shareholder["比率"]) + "%"
            indicators.append("\n" + ceo_stock)
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
        "ten_bagger_indicators": "".join(indicators)
    }



# TSVファイルにデータを書き込む
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter='\t')
    
    header = next(reader)
    writer.writerow([
        '買', '企業名', 'コード', 'テンバガー指標', 'PER', '決算',
        'IPO情報URL', 'IR', '事業内容',
        '想定時価総額（億円）', '業種1', '業種2', '会社設立', '上場日','市場', '株主名と比率',
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
                "", company_name, code, data['ten_bagger_indicators'], "", "",
                full_ipo_info_url, "https://irbank.net/" + code + "/ir", data['business_content'],
                data['market_capital'], "", "", data['company_establishment'], data['listing_date'], market_name, data['shareholders'],
                data['performance_data'], data['admin_comment'], data['company_url']
            ])

        #if index > 5: break

# 売上↗︎, 利益↗︎, 純利益↗︎, 社長株30%↑, 時価250億↓, PER40↓

print("データの取得と書き込みが完了しました。")
