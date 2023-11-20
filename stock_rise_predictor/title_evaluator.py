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

# TODO:
# ニュースや適時開示の情報の中に以下のような株価を押し上げる情報があるかをChatGPTに聞くAPIを作る
# - 新製品やサービスの発表
# - 戦略的提携やパートナーシップ
# - 財務健全性の改善
# - 新たな市場への進出
# - 経営陣の変更
# - 特許取得や技術的な進歩
#
# テンバガーの人がみている適時開示情報
#「決算短信」
#「中期経営計画」
#「業績予想の修正」
#「受注」
#「月次情報」


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

    table = get_table_element(driver)
    rows = table.find_elements(By.TAG_NAME, "tr")
    timely_disclosure, company = [], []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            time = cols[0].text
            code = cols[1].text
            company_name = cols[2].text
            title_element = cols[3].find_element(By.TAG_NAME, "a")
            title = title_element.text
            url = title_element.get_attribute('href')
            company.append([code, company_name])
            timely_disclosure.append([date, time, code, title, url])
    return company, timely_disclosure

def get_disclosure_records_in_day(driver, date):
    # iframeに移動してデータスクレイピング
    iframe = driver.find_element(By.ID, "main_list")
    driver.switch_to.frame(iframe)
    
    kaiji_text_element = driver.find_element(By.ID, "kaiji-text-1")
    if kaiji_text_element.text == "に開示された情報はありません。":
        driver.switch_to.default_content() # フレームから元のページに戻る
        raise Exception("開示された情報がありません。")
    
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

    driver.switch_to.default_content() # フレームから元のページに戻る
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
    #tart_date_index = 1
    #if not start_date_index:
    #    start_date_index = 1 if is_trading_hours() else 2
    if not end_date_index:
        end_date_index = len(date_options)

    for date_index in range(start_date_index, end_date_index):
        print("date_index: ", date_index)
        date_options = driver.find_element(By.ID, "day-selector").find_elements(By.TAG_NAME, "option")  # ページ再読み込み後に再取得
        selected_date_option = date_options[date_index].text
        date = convert_date(selected_date_option)
        
        date_options[date_index].click()
        time.sleep(random.uniform(0.8, 1.0))

        try:
            company, time_disclosue = get_disclosure_records_in_day(driver, date) # 日付ごとのデータ処理
            print(f"Scraping: date = {date}")
        except Exception as e:
            print(f"Skipped: date = {date}")
            continue


        db.insert_data(conn, "Company", company)
        db.insert_data(conn, "TimelyDisclosure", time_disclosue)
    driver.quit() # ブラウザの終了
    
def evaluate(conn, search_date):
    timely_disclosure_table = db.fetch_timely_disclosure(conn, search_date)
    #company_count = Counter()

    evaluations = { }
    for date, _, code, title in timely_disclosure_table:
        for search_condition in config["disclosure"]['rise_tags']:

            found_keywords_in_title = search_condition['condition'](title)
            if found_keywords_in_title:
                #if code == "83160":
                #    print(title, found_keywords_in_title, search_condition['tag'])

                tag = search_condition['tag']
                if code in evaluations:
                    evaluations[code]["evaluated_value"] += 1
                    evaluations[code]["tags"] = evaluations[code]["tags"] + ',' + tag
                else:
                    evaluations[code] = {
                        "evaluated_value": 1,
                        "tags": tag
                    }
                #company_count[code] += 1
                break
    evaluation_data = [
        (code, format_datetime_str(search_date), evaluation["evaluated_value"], evaluation["tags"])
        for code, evaluation in evaluations.items()
    ]
    db.insert_data(conn, "UpwardEvaluation", evaluation_data)

def scrape_in_day():
    start_date_index = 1 if is_trading_hours() else 2
    scrape_in_days(start_date_index, start_date_index + 1)

def scrape():
    conn = db.create_database()

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
    
    end_date = config['evaluate']['end_date']
    days = config['evaluate']['days_before_end_date']
    for i in range(1, days):
        evaluate_date = end_date - timedelta(days=i)
        evaluate(conn, evaluate_date)

    top_evaluations = db.fetch_top_evaluations(conn, config['evaluate']['top_evaluations_limit'])
    for evaluation in top_evaluations:
        print(evaluation)

    conn.close()


if __name__ == "__main__":
    scrape()
