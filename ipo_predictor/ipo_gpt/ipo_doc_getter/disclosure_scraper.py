import sys
import time
import random
import traceback
import os
import re
import glob
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

class DisclosureScraper:
    def __init__(self):
        self.init_driver()
        #self.ipo_year = 2024
        #self.companies = self.read_companies("input/ipo_companies_%s.tsv" % self.ipo_year)
        #output_dir = "output"
        #if not os.path.exists(output_dir):
        #    os.makedirs(output_dir)
        #self.disclosure_tsv_path = os.path.join(output_dir, "disclosures_%s.tsv" % self.ipo_year)
        self.ipo_years = self.get_ipo_years()
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def init_driver(self):
        # ブラウザの設定
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        self.referers = [
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.google.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.yahoo.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.yahoo.co.jp'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.bing.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.facebook.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.twitter.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.reddit.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.wikipedia.org'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.instagram.com'; }});",
            "Object.defineProperty(document, 'referrer', {get : function(){ return 'https://www.linkedin.com'; }});"
        ]
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Mozilla/5.0 (Android 10; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0",
            "Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1"
        ]

        random_user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f"user-agent={random_user_agent}")
        self.driver = webdriver.Chrome(options=chrome_options)

        self.wait = WebDriverWait(self.driver, 10)

    def get_ipo_years(self):
        tsv_files = glob.glob("input/ipo_companies_*.tsv")
        ipo_years = [re.search(r'ipo_companies_(\d{4})\.tsv', file).group(1) for file in tsv_files]
        return ipo_years

    def scrape_disclosure_history(self, company_code):
        
        partial_id = 'closeUpKaiJi'
        elements = self.driver.find_elements(By.XPATH, f"//*[contains(@id, '{partial_id}')]")
        if not elements:
            print(f"No elements. company_code = {company_code}")
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
            self.driver.delete_all_cookies()  # 全てのクッキーを削除
            random_referer = random.choice(self.referers)
            self.driver.execute_script(random_referer)
            self.driver.get('https://www2.jpx.co.jp/tseHpFront/JJK010010Action.do')

            time.sleep(random.uniform(2.0, 2.5))

            code_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'eqMgrCd')))
            code_input.clear()
            code_input.send_keys(company_code)
            time.sleep(random.uniform(0.2, 0.3))

            search_button = self.driver.find_element(By.NAME, 'searchButton')
            search_button.click()
            time.sleep(random.uniform(2.0, 2.4))

            detail_button = self.wait.until(EC.presence_of_element_located((By.NAME, 'detail_button')))
            detail_button.click()
            time.sleep(random.uniform(0.6, 0.8))

            disclosure_tab = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '適時開示情報')))
            disclosure_tab.click()
            time.sleep(random.uniform(0.6, 0.8))
            return True 

        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()
            return False

    def scrape_table(self, company_code, closed_table_id, opened_table_id):
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')

            time.sleep(random.uniform(1.6, 2))

            info_table = self.wait.until(EC.presence_of_element_located((By.ID, closed_table_id)))

            info_button = info_table.find_element(By.XPATH, ".//input[@type='button'][@value='情報を閲覧する場合はこちら']")
            info_button.click()

            time.sleep(random.uniform(1.6, 2))
            
            disclosure_table = self.wait.until(EC.presence_of_element_located((By.ID, opened_table_id)))
        except Exception as e:
            print(f"ERROR OCCURED: {e}")
            traceback.print_exc()

        more_info_button_exists = False
        try:
            more_info_button = disclosure_table.find_element(By.XPATH, ".//input[@type='button'][@value='さらに表示']")
            more_info_button.click()
            time.sleep(random.uniform(1.6, 2))
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
        match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return None


    def get_table_rows(self, company_code, rows):
        if len(rows) < 3:
            print("No disclosure information available.")
            return []
        
        table_rows = []
        for row in rows[2:]:  # Skipping header rows
            cols = row.find_elements(By.TAG_NAME, "td")
            
            if len(cols) < 4:
                continue

            raw_date = cols[0].text.strip()
            if raw_date == "-":
                break

            link_element = cols[1].find_element(By.TAG_NAME, "a")
            title = link_element.text.strip()
            date = self.convert_date_format_revised(raw_date)
            url = link_element.get_attribute("href").strip()

            record = [date, '00:00', company_code, title, url]
            table_rows.append(record)

        return table_rows

    def scrape_and_save(self):
        for ipo_year in self.ipo_years:
            companies = self.read_companies(f"input/ipo_companies_{ipo_year}.tsv")
            self.disclosure_tsv_path = os.path.join("output", f"disclosures_{ipo_year}.tsv")

            # ファイルが既に存在する場合はスキップ
            if os.path.exists(self.disclosure_tsv_path):
                print(f"{self.disclosure_tsv_path} already exists. Skipping...")
                continue

            for index, company in enumerate(companies):
                name, code = company
                self.init_driver()

                try:
                    print(f"Scraping: index = {index}, code = {code}, company name = {name}")
                    found_results = self.go_to_table_page(code)
                    if found_results:
                        table_rows = self.scrape_disclosure_history(code)
                        if table_rows:
                            for row in table_rows:
                                row.insert(2, name)  # 会社名をコードの後に挿入
                            self.save_disclosures(table_rows)  # 都度保存
                except Exception as e:
                    if "503" in str(e):
                        print(f"HTTP 503 Error encountered at index {index}. Exiting.")
                        self.save_last_index(index)
                        sys.exit(1)
                    else:
                        print(f"Error: {e}")
                finally:
                    self.close_driver()

    def read_companies(self, filepath):
        companies = []
        with open(filepath, "r", encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    name, code = line.strip().split("\t")
                    companies.append((name, code))
        return companies

    def save_disclosures(self, disclosures):
        with open(self.disclosure_tsv_path, "a", encoding='utf-8') as file:
            for disclosure in disclosures:
                file.write("\t".join(disclosure) + "\n")

    def save_last_index(self, index):
        with open("tmp/last_index.txt", "w") as file:
            file.write(str(index))

    def close_driver(self):
        self.driver.close()

    def close(self):
        self.close_driver()

if __name__ == "__main__":
    scraper = DisclosureScraper()
    scraper.scrape_and_save()