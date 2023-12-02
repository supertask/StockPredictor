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

from db_manager import DBManager, DBTable
import config

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

class TitleEvaluator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    #def get_datetime_now(self):
    #    jst = pytz.timezone('Asia/Tokyo')
    #    return datetime.now(jst)
        
    def format_date_str(self, datetime_now):
        return datetime_now.strftime('%Y-%m-%d')
        
    def convert_date(self, selected_date_option):
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

    def is_trading_hours(self):
        return 9 <= config.get_datetime_now().hour <= 15

    def get_table_element(self, driver):
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

    def get_disclosure_records_in_page(self, driver, date):

        table = self.get_table_element(driver)
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

    def get_disclosure_records_in_day(self, driver, date):
        # iframeに移動してデータスクレイピング
        iframe = driver.find_element(By.ID, "main_list")
        driver.switch_to.frame(iframe)
        
        kaiji_text_element = driver.find_element(By.ID, "kaiji-text-1")
        if kaiji_text_element.text == "に開示された情報はありません。":
            driver.switch_to.default_content() # フレームから元のページに戻る
            raise Exception("開示された情報がありません。")
        
        company, timely_disclosure = [], []
        c, td = self.get_disclosure_records_in_page(driver, date)
        company.extend(c)
        timely_disclosure.extend(td)
        
        while True:
            try:
                pager_r = driver.find_element(By.CLASS_NAME, "pager-R")
                pager_r.click()
                time.sleep(0.3)
                c, td = self.get_disclosure_records_in_page(driver, date)
                company.extend(c)
                timely_disclosure.extend(td)

            except (NoSuchElementException, ElementNotInteractableException):
                break

        driver.switch_to.default_content() # フレームから元のページに戻る
        return company, timely_disclosure


    def scrape_in_days(self, conn, start_date_index = None, end_date_index = None):
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
            date = self.convert_date(selected_date_option)
            
            date_options[date_index].click()
            time.sleep(random.uniform(0.8, 1.0))

            try:
                company, time_disclosue = self.get_disclosure_records_in_day(driver, date) # 日付ごとのデータ処理
                print(f"Scraping: date = {date}")
            except Exception as e:
                print(f"Skipped: date = {date}")
                continue
            #self.db_manager.insert_data(DBTable.Company, DBTable.Company.All, company)
            #self.db_manager.insert_data(DBTable.TimelyDisclosure, DBTable.TimelyDisclosure.All, time_disclosue)
            self.db_manager.insert_into_company(company)
            self.db_manager.insert_into_timely_disclosure(time_disclosue)
        driver.quit() # ブラウザの終了

    def count_rise_tags(self, search_date, insert_only_rise_tag=True):
        
        search_date_str = self.format_date_str(search_date)
        evaluations = { }
        if insert_only_rise_tag:
            rise_tags = config.get_rise_tags() 
            tag_questions = ', '.join(['?' for _ in range(len(rise_tags))] )
            timely_disclosure_table = self.db_manager.fetch_timely_disclosure(
                condition_line = f"td.date = ? and tg.tag in ({tag_questions})",
                params = [search_date_str] + rise_tags)
        else:
            timely_disclosure_table = self.db_manager.fetch_timely_disclosure(condition_line = f"td.date = ?", params = [search_date_str])

        rise_tags = config.get_rise_tags()
        for date, time, code, title, tag in timely_disclosure_table:
            #print(date, time, code, title)
            if tag in rise_tags:
                # 株上昇タグある銘柄の場合、タグを収集する
                if code in evaluations:
                    evaluations[code]["rise_tags"].add(tag)  # タグを集合(重複なし)に追加
                else:
                    evaluations[code] = {"rise_tags": set()}
                    evaluations[code]["rise_tags"].add(tag)  # タグを集合(重複なし)に追加
            else:
                if code not in evaluations:
                    # 株上昇タグのない銘柄の場合、タグは収取せず、キーだけ入れておく（あとで日付を元に株価の上昇率を計算するため）
                    evaluations[code] = {"rise_tags": set()}

        evaluation_data = [
            (code, self.format_date_str(search_date), len(evaluation["rise_tags"]), ','.join(evaluation["rise_tags"]), False)
            for code, evaluation in evaluations.items()
        ]

        self.db_manager.insert_tags_into_upward_evaluation(evaluation_data)
        

    def scrape_in_day(self):
        start_date_index = 1 if self.is_trading_hours() else 2
        self.scrape_in_days(start_date_index, start_date_index + 1)

    def tag_title_on_disclosure(self):
        timely_disclosure_table = self.db_manager.fetch_timely_disclosure(
            condition_line="tg.tag IS NULL", params=[])

        tag_data = []
        for date, time, code, title, tag in timely_disclosure_table:
            #print(date, time, code, title)
            for search_condition in config.setting["disclosure"]['watch_pdf_tags']:
                found_keywords_in_title = search_condition['condition'](title)
                if found_keywords_in_title:
                    new_tag = search_condition['tag']
                    tag_data.append([date, time, code, title, new_tag])
        self.db_manager.insert_into_timely_disclosure_tags(tag_data)

    def scrape(self):
        skip_scraping = config.setting['scraping']['skip_scraping']
        if not skip_scraping:
            is_on_day = config.setting['scraping']['is_on_day']
            if is_on_day:
                self.scrape_in_day()
            else:
                start_date_index = config.setting['scraping']['start_date_index']
                self.scrape_in_days(start_date_index = start_date_index)

    def evaluate_historical_rise_tags(self):
        """ 現在の適時開示の株上昇タグをカウント（評価値）、タグ付けし、評価する.
            また、株上昇タグ以外の適時開示レコードも保存しておく
        """
        today = config.get_datetime_now()
        end_date = today - timedelta(days = 3 * 30)
        start_date = config.get_datetime(2013, 9, 1)
        current_date = start_date
        while current_date <= end_date:
            self.count_rise_tags(current_date, insert_only_rise_tag=False)
            current_date += timedelta(days=1)

    def evaluate_rise_tags(self):
        """ 現在の適時開示の株上昇タグをカウント（評価値）、タグ付けし、評価する
        """
        end_date = config.setting['evaluate']['end_date']
        days = config.setting['evaluate']['days_before_end_date']
        start_date = end_date - timedelta(days=days)
        #print(start_date, end_date)
        current_date = start_date
        while current_date <= end_date:
            self.count_rise_tags(current_date)
            current_date += timedelta(days=1)

    def display_top_evaluations(self):
        rise_tags_counts = self.db_manager.fetch_top_evaluations(config.setting['evaluate']['top_evaluations_limit'])
        for rise_tags_count in rise_tags_counts:
            print(rise_tags_count)

if __name__ == "__main__":
    evaluator = TitleEvaluator(DBManager(config.setting['db']['recent']))
    evaluator.scrape()
    evaluator.evaluate_rise_tags()
    evaluator.display_top_evaluations()

