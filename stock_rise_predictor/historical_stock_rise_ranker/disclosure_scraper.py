import sys
realtime_module_path = "../realtime_stock_rise_predicter"
sys.path.append(realtime_module_path) #mainのモジュール読み込む

import os
import time
import random
import traceback
import re
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
#from selenium.webdriver.support.ui import WebDriverWait

from title_evaluator import TitleEvaluator
from db_manager import DBManager, DBTable
import config

class DisclosureScraper:
    def __init__(self, db_manager):
        # ブラウザの設定
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        current_db_path = os.path.join(realtime_module_path, "output/timely_disclosure.db")
        past_db_path = "output/past_timely_disclosure.db"       
        self.db_manager = db_manager
        self.db_manager.copy_company_table(current_db_path, past_db_path) #会社情報だけ最新の適時開示DBからコピー
        self.db_manager.change_db(past_db_path) #過去の適時開示DBに切り替え

    def scrape_disclosure_history(self, company_code):
        
        partial_id = 'closeUpKaiJi'
        elements = self.driver.find_elements(By.XPATH, f"//*[contains(@id, '{partial_id}')]")
        if not elements:
            print(f"No elments. company_code = {company_code} ")
        table_pair_ids = self.get_table_pair_ids(elements)
    
        # [決算情報], Table ID 'closeUpKaiJi0_open'
        kessan_info_ids = table_pair_ids[0]
        rows = self.scrape_table(company_code, kessan_info_ids[0], kessan_info_ids[1])
        table_rows = self.get_table_rows(company_code, rows)

        # [決定事実 / 発生事実], Table ID 'closeUpKaiJi117_open'
        kettei_info_ids = table_pair_ids[1]
        rows = self.scrape_table(company_code, kettei_info_ids[0], kettei_info_ids[1])
        table_rows += self.get_table_rows(company_code, rows)
        return table_rows

    def get_table_pair_ids(self, elements):
        #print(element.get_attribute('outerHTML'))
        table_ids = []
        for element in elements:
            id_str = element.get_attribute('id')
            if id_str.endswith("_open"):
                open_id_str = id_str
                close_id_str = id_str.split("_")[0]
                table_ids.append([open_id_str, close_id_str])
        return table_ids


    def go_to_table_page(self, company_code):
        try:
            # JPXウェブサイトへアクセス
            self.driver.get('https://www2.jpx.co.jp/tseHpFront/JJK010010Action.do')

            # 企業コードの入力
            code_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'eqMgrCd')))
            code_input.clear()
            code_input.send_keys(company_code)

            # 検索ボタンをクリック
            search_button = self.driver.find_element(By.NAME, 'searchButton')
            search_button.click()
            time.sleep(random.uniform(0.5, 1))

            # 基本情報ボタンをクリック
            detail_button = self.wait.until(EC.presence_of_element_located((By.NAME, 'detail_button')))
            detail_button.click()
            time.sleep(random.uniform(0.5, 1))

            # 適時開示情報タブをクリック
            disclosure_tab = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '適時開示情報')))
            disclosure_tab.click()
            time.sleep(random.uniform(0.5, 1))
            return True 

        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()
            return False

    def scrape_table(self, company_code, closed_table_id, opened_table_id):
        """ [決算情報]や[決定事実 / 発生事実]のテーブルの行一覧を取得する
        """
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            #body_html = body.get_attribute('innerHTML')

            time.sleep(random.uniform(1, 1.2))

            # [決算情報], Table ID 'closeUpKaiJi0_open'
            info_table = self.wait.until(EC.presence_of_element_located((By.ID, closed_table_id)))

            # 「情報を閲覧する場合はこちら」ボタンを押す
            info_button = info_table.find_element(By.XPATH, ".//input[@type='button'][@value='情報を閲覧する場合はこちら']")
            info_button.click()

            time.sleep(random.uniform(1, 1.2))
			
            # [決算情報]の開かれた後のテーブル
            disclosure_table = self.wait.until(EC.presence_of_element_located((By.ID, opened_table_id)))
        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()

        more_info_button_exists = False
        try:
            # さらに表示ボタンを押す
            more_info_button = disclosure_table.find_element(By.XPATH, ".//input[@type='button'][@value='さらに表示']")
            more_info_button.click()
            time.sleep(random.uniform(1, 2))
            more_info_button_exists = True
            print(f"Finished to click [決算情報]の「さらに表示する」: {company_code}")
        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()
            more_info_button_exists = False

        try:
            rows = disclosure_table.find_elements(By.TAG_NAME, "tr")
            print(f"Finished to get table([決算情報]) rows: {company_code}")
            return rows
        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()
            
    def convert_date_format_revised(self, date_str):
        # 正規表現を用いて日付を YYYY/MM/DD 形式から YYYY-MM-DD 形式に変換
        match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return None


    def get_table_rows(self, company_code, rows):
        # Check if there are enough rows
        if len(rows) < 3:
            print("No disclosure information available.")
            return
        
        table_rows = []
        for row in rows[2:]:  # Skipping header rows
            cols = row.find_elements(By.TAG_NAME, "td")
            
            # Ensure each row has the expected number of columns
            if len(cols) < 4:
                continue

            raw_date = cols[0].text.strip()
            if raw_date == "-":
                break

            link_element = cols[1].find_element(By.TAG_NAME, "a")
            title = link_element.text.strip()
            date = self.convert_date_format_revised(raw_date)
            url = link_element.get_attribute("href").strip()

            # Format data for insertion
            record = [date, '00:00', company_code, title, url]
            table_rows.append(record)
            #print(record)

        return table_rows


    def scrape_and_save(self):
        companies = self.db_manager.fetch_company_codes()

        for index, company in enumerate(companies):
            code, name = company
            if index < 493:
                continue
            #if not (code == '83160' or code == '35630'):
            #    continue            

            print("Scraping: index = %s, code = %s, company name = %s" % (index, code, name) )
            found_results = self.go_to_table_page(code)
            if found_results:
                table_rows = self.scrape_disclosure_history(code)
                if table_rows:
                    #print(table_rows)
                    #self.db_manager.insert_data(DBTable.TimelyDisclosureAll, table_rows)
                    self.db_manager.insert_into_timely_disclosure(table_rows)
            else:
                print(f"Skipping the company. code = {code}, name = {name}. Not found on the web.")


    def close(self):
        self.driver.close()

if __name__ == "__main__":
    db_manager = DBManager(config.setting['db']['past'])
    scraper = DisclosureScraper(db_manager)
    scraper.scrape_and_save()