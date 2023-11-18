# coding:utf-8
import csv
import time
import pytz
import re
import random
import sqlite3
import json
from datetime import datetime, timedelta
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
#from selenium.webdriver.support.ui import WebDriverWait

import db
from config import config

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

def get_datetime_now():
    jst = pytz.timezone('Asia/Tokyo')
    return datetime.now(jst)
    
def format_datetime_str(datetime_now):
    return datetime_now.strftime('%Y-%m-%d')
    
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

def is_trading_hours():
    return 9 <= get_datetime_now().hour <= 15

def get_table_element(driver):
    try:
        table = driver.find_element(By.ID, "main-list-table")
    except NoSuchElementException as e:
        # エラーメッセージの出力
        print(f"Error: {e}")

        # bodyタグの内容を出力
        body_content = driver.find_element(By.TAG_NAME, "body").get_attribute('innerHTML')
        print("Page Body Content:")
        print(body_content)

        # または、エラーが発生した時点でのスクリーンショットを取ることもできます
        #driver.save_screenshot("log/error_screenshot.png")

        # 必要に応じて処理を終了する
        driver.quit()
        raise
    return table

def get_disclosure_records_in_page(driver, date):
    # Scrape the table data
    table = get_table_element(driver)
    rows = table.find_elements(By.TAG_NAME, "tr")
    timely_disclosure, company = [], []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            time = cols[0].text
            code = cols[1].text
            company_name = cols[2].text
            title = cols[3].text
            company.append([code, company_name])
            timely_disclosure.append([date, time, code, title])
    return company, timely_disclosure

def get_disclosure_records_in_day(driver, date):
    # iframeに移動してデータスクレイピング
    iframe = driver.find_element(By.ID, "main_list")
    driver.switch_to.frame(iframe)
    
    company, timely_disclosure = [], []
    c, td = get_disclosure_records_in_page(driver, date)
    company.extend(c)
    timely_disclosure.extend(td)
    
    while True:
        try:
            pager_r = driver.find_element(By.CLASS_NAME, "pager-R")
            pager_r.click()
            time.sleep(0.3)
            c, td = get_disclosure_records_in_page(driver, date)
            company.extend(c)
            timely_disclosure.extend(td)

        except (NoSuchElementException, ElementNotInteractableException):
            break

    # フレームから元のページに戻る
    driver.switch_to.default_content()
    return company, timely_disclosure


def scrape_in_days(conn, start_date_index = None, end_date_index = None):
    # Setup WebDriver
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.release.tdnet.info/inbs/I_main_00.html")  # Replace with the actual URL
    
    time.sleep(random.uniform(0.7, 1.0))

    # 日付オプションの取得
    date_options = driver.find_element(By.ID, "day-selector").find_elements(By.TAG_NAME, "option")
    if not start_date_index:
        start_date_index = 1 if is_trading_hours() else 2
    if not end_date_index:
        end_date_index = len(date_options)

    for date_index in range(start_date_index, end_date_index):
        date_options = driver.find_element(By.ID, "day-selector").find_elements(By.TAG_NAME, "option")  # ページ再読み込み後に再取得
        selected_date_option = date_options[date_index].text
        date = convert_date(selected_date_option)
        print(selected_date_option, date)
        
        date_options[date_index].click()
        time.sleep(random.uniform(0.8, 1.0))

        # 日付ごとのデータ処理
        company, time_disclosue = get_disclosure_records_in_day(driver, date)
        insert_data(conn, "Company", company)
        insert_data(conn, "TimelyDisclosure", time_disclosue)
    driver.quit() # ブラウザの終了
    
def evaluate(conn, search_date):
    timely_disclosure_table = fetch_timely_disclosure(conn, search_date)
    company_count = Counter()
    for date, _, code, title in timely_disclosure_table:
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
    evaluation_data = [(code, format_datetime_str(search_date), count) for code, count in company_count.items()]
    insert_data(conn, "UpwardEvaluation", evaluation_data)
    return company_count

def scrape_in_day():
    start_date_index = 1 if is_trading_hours() else 2
    scrape_in_days(start_date_index, start_date_index + 1)

def scrape():
    conn = create_database()

    skip_scraping = config['scraping']['skip_scraping']
    if not skip_scraping:
        is_on_day = config['scraping']['is_on_day']
        if is_on_day:
            scrape_in_day(conn)
        else:
            start_date_index = config['scraping']['start_date_index']
            scrape_in_days(conn, start_date_index = start_date_index)

    # タイトルからキーワードを検索してカウント
    #current_datetime = get_datetime_now()
    #yesterday_datetime = current_datetime - timedelta(days=1)
    #target_datetime = current_datetime if is_trading_hours() else yesterday_datetime
    
    search_date = config['evaluate']['search_date']
    for i in range(1, 10):
        saerch_date = search_date - timedelta(days=i)
        evaluate(conn, saerch_date)

    # 上位5社をランキング化
    top_companies = company_count.most_common(5)
    
    # ランキングの表示
    print("Top 5 Companies:")
    for i, (code, count) in enumerate(top_companies, start=1):
        print(f"{i}. Code: {code}, Count: {count}")

    conn.close()


if __name__ == "__main__":
    scrape()
