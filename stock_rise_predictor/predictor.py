# coding:utf-8
import csv
import time
import pytz
import re
import random
from datetime import datetime
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
#from selenium.webdriver.support.ui import WebDriverWait

# TODO: ニュースや適時開示の情報の中に以下のような株価を押し上げる情報があるかをChatGPTに聞くAPIを作る
# - 新製品やサービスの発表
# - 戦略的提携やパートナーシップ
# - 財務健全性の改善
# - 新たな市場への進出
# - 経営陣の変更
# - 特許取得や技術的な進歩

keywords = [
    (("配当", "修正"), ("増配",)),
    ("株式", "分割"),
    ("自己株式取得",),
    ("上方修正",),
    ("業績予想", "修正")
]

def scrape_one_day(driver, date):
    # Scrape the table data
    table = driver.find_element(By.ID, "main-list-table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            time = cols[0].text
            code = cols[1].text
            company_name = cols[2].text
            title = cols[3].text
            data.append([date, time, code, company_name, title])
    return data
    
    
def convert_date(selected_date_option):
    #
    # datetimeが変換しやすい形式(年-月-日)にする
    #
    date_regex = r"(\d{4})/(\d{1,2})/(\d{1,2})"
    match = re.search(date_regex, selected_date_option)
    if match:
        date = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"  # 年-月-日 形式
    else:
        date = "unknown"  # 日付が見つからない場合のデフォルト値
    return date


def determine_start_date_index():
    jst = pytz.timezone('Asia/Tokyo')
    current_hour_jst = datetime.now(jst).hour
    return 1 if 9 <= current_hour_jst <= 15 else 2


def process_data_for_date(driver, date):
    # iframeに移動してデータスクレイピング
    iframe = driver.find_element(By.ID, "main_list")
    driver.switch_to.frame(iframe)
    
    all_data = []
    data = scrape_one_day(driver, date)
    all_data.extend(data)
    
    while True:
        try:
            pager_r = driver.find_element(By.CLASS_NAME, "pager-R")
            pager_r.click()
            time.sleep(0.3)
            data = scrape_one_day(driver, date)
            all_data.extend(data)
        except (NoSuchElementException, ElementNotInteractableException):
            break

    # フレームから元のページに戻る
    driver.switch_to.default_content()

    return all_data

def main():
    # Setup WebDriver
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=chrome_options)

    # Open the webpage
    start_date_index = determine_start_date_index()
    driver.get("https://www.release.tdnet.info/inbs/I_main_00.html")  # Replace with the actual URL
    
    #time.sleep(1)  # 初期のロード時間
    time.sleep(random.uniform(0.7, 1.0))

    # 日付オプションの取得
    date_options = driver.find_element(By.ID, "day-selector").find_elements(By.TAG_NAME, "option")

    all_collected_data = []

    #for date_index in range(start_date_index, len(date_options)):
    for date_index in range(start_date_index, start_date_index + 1):
        date_options = driver.find_element(By.ID, "day-selector").find_elements(By.TAG_NAME, "option")  # ページ再読み込み後に再取得
        selected_date_option = date_options[date_index].text
        date = convert_date(selected_date_option)
        print(selected_date_option, date)
        
        date_options[date_index].click()
        time.sleep(random.uniform(0.4, 0.65))

        # 日付ごとのデータ処理
        data_for_date = process_data_for_date(driver, date)
        all_collected_data.extend(data_for_date)

    # ブラウザの終了
    driver.quit()

    # Save data to CSV
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Time", "Code", "CompanyName", "Title"])
        writer.writerows(all_collected_data)

    # タイトルからキーワードを検索してカウント
    company_count = Counter()
    for date, _, code, _, title in all_collected_data:
        for keyword_group in keywords:
            if isinstance(keyword_group[0], tuple):
                # 複数のキーワードグループのいずれかが含まれているかチェック
                if any(all(keyword in title for keyword in group) for group in keyword_group):
                    company_count[code] += 1
                    break  # 一致したらその他のキーワードグループはチェック不要
            else:
                # すべてのキーワードが含まれている必要がある
                if all(keyword in title for keyword in keyword_group):
                    company_count[code] += 1
                    break  # 一致したらその他のキーワードグループはチェック不要

    # 上位5社をランキング化
    top_companies = company_count.most_common(5)
    
    # ランキングの表示
    print("Top 5 Companies:")
    for i, (code, count) in enumerate(top_companies, start=1):
        print(f"{i}. Code: {code}, Count: {count}")

main()