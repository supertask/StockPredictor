import time
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
#from selenium.webdriver.support.ui import WebDriverWait

class DisclosureScraper:
    def __init__(self):
        # ブラウザの設定
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_disclosure_history(self, company_code):
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
            time.sleep(random.uniform(0.7, 1.0))

            # 基本情報ボタンをクリック
            detail_button = self.wait.until(EC.presence_of_element_located((By.NAME, 'detail_button')))
            detail_button.click()
            time.sleep(random.uniform(0.7, 1.0))

            # 適時開示情報タブをクリック
            disclosure_tab = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '適時開示情報')))
            disclosure_tab.click()
            time.sleep(random.uniform(0.7, 1.0))
            
            
            # Find the table by its ID 'closeUpKaiJi0_open'
            info_table = self.wait.until(EC.presence_of_element_located((By.ID, 'closeUpKaiJi0_open')))

            # 「情報を閲覧する場合はこちら」ボタンを押す
            info_button = info_table.find_element(By.XPATH, ".//input[@type='button'][@value='情報を閲覧する場合はこちら']")
            info_button.click()

            time.sleep(random.uniform(0.2, 0.3))
			
            # Find the table with disclosure information
            disclosure_table = self.wait.until(EC.presence_of_element_located((By.ID, 'closeUpKaiJi0')))
            
            # さらに表示ボタンを押す
            more_info_button = disclosure_table.find_element(By.XPATH, ".//input[@type='button'][@value='さらに表示']")
            more_info_button.click()
            time.sleep(random.uniform(0.2, 0.3))

            rows = disclosure_table.find_elements(By.TAG_NAME, "tr")

            # Check if there are enough rows
            if len(rows) < 3:
                print("No disclosure information available.")
                return
			
            data = []
            for row in rows[2:]:  # Skipping header rows
                cols = row.find_elements(By.TAG_NAME, "td")
                
                # Ensure each row has the expected number of columns
                if len(cols) < 4:
                    continue

                # Debugging: print the text of each column
                #for col in cols:
                #    print(col.text)

                link_element = cols[1].find_element(By.TAG_NAME, "a")

                date = cols[0].text.strip()
                title = link_element.text.strip()
                url = link_element.get_attribute("href").strip()

                # Format data for insertion
                record = [date, '00:00', company_code, title, url]
                data.append(record)
                print(record)

            # Insert data into the database
            # Here you would need to have an existing connection to your SQLite database
            #insert_data(your_connection, 'TimelyDisclosure', data)			


            # ここで必要な情報を取得する処理を追加

        except NoSuchElementException as e:
            print(f"エレメントが見つかりません: {e}")
        except ElementNotInteractableException as e:
            print(f"エレメントが操作できません: {e}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

    def close(self):
        self.driver.quit()


getter = DisclosureScraper()
getter.scrape_disclosure_history('8316')
getter.close()
