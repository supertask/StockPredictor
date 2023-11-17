import time
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

## オプションを設定してページ読み込み戦略を 'eager' にする
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'


def fetch_and_save_data(table_id, url, csv_file_name):

    with webdriver.Chrome(options=chrome_options) as driver:
        # 対象のウェブページを開く
        driver.get(url)
        time.sleep(5)  # 初期のロード時間

        # 指定された要素が見つかる限りクリックし続ける
        while True:
            promoteSignUpPopUpExists = False
            try:
                element = driver.find_element(By.ID, "PromoteSignUpPopUp")
                display = element.value_of_css_property("display")
                promoteSignUpPopUpExists = (display != "none")
            except NoSuchElementException:
                promoteSignUpPopUpExists = False
                print("No #PromoteSignUpPopUp's element.")

            if promoteSignUpPopUpExists:
                driver.execute_script("arguments[0].style.display = 'none';", element)
                print("Disabled PromoteSignUpPopUp.")
                time.sleep(10)

            else:
                showMoreHistoryExists = False
                try:
                    element = driver.find_element(By.ID, "showMoreHistory" + table_id)
                    display = element.value_of_css_property("display")
                    showMoreHistoryExists = (display != "none")
                except Exception:
                    print("No showMoreHistory's element.")
                    break

                if showMoreHistoryExists:
                    element.click()
                    time.sleep(0.05)
                else:
                    break

        print(f"finished browsing.")

        # テーブルを見つける
        table = driver.find_element(By.ID, "eventHistoryTable" + table_id)

        # テーブルのヘッダーとデータを取得
        headers = table.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "th")
        header_data = [header.text for header in headers]
        rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        csv_data = [header_data] + [[col.text for col in row.find_elements(By.TAG_NAME, "td")] for row in rows]

    # CSV ファイルに書き出し
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    print(f"CSVファイルが '{csv_file_name}' に保存されました。")


# データを取得して保存するURL, CSVファイル名
urls_and_files = [
    #("227", "https://jp.investing.com/economic-calendar/nonfarm-payrolls-227", "nonfarm_payrolls.csv"), #米国 失業率, 重要度: ⭐️⭐⭐
    #("300", "https://jp.investing.com/economic-calendar/unemployment-rate-300", "unemployment_rate.csv"), #米国 非農業部門雇用者数, 重要度: ⭐️⭐⭐
    #("256", "https://jp.investing.com/economic-calendar/retail-sales-256", "retail_sales.csv"), #米国 小売売上高, 重要度: ⭐️⭐⭐

    #("294", "https://jp.investing.com/economic-calendar/initial-jobless-claims-294", "initial_jobless_claims.csv"), #米国 失業保険申請件数, 重要度: ⭐️⭐⭐️
    #("59", "https://jp.investing.com/economic-calendar/core-durable-goods-orders-59", "core_durable_goods_orders.csv"), #米国 コア耐久財受注, 重要度: ⭐️⭐⭐️
    #("48", "https://jp.investing.com/economic-calendar/cb-consumer-confidence-48", "cb_consumer_confidence.csv"), #米国 消費者信頼感指数, 重要度: ⭐️⭐⭐️
    #("173", "https://jp.investing.com/economic-calendar/ism-manufacturing-pmi-173", "ism_manufacturing_pmi.csv"), #米国 ISM製造業購買担当者景気指数, 重要度: ⭐️⭐⭐️
    #("56", "https://jp.investing.com/economic-calendar/core-cpi-56", "core_cpi.csv"), #米国 コア消費者物価指数（CPI）,  重要度: ⭐️⭐⭐️

    ("161", "https://jp.investing.com/economic-calendar/industrial-production-161", "industrial_production.csv"), #米国 米国 鉱工業生産, 重要度: ⭐️⭐
    ("320", "https://jp.investing.com/economic-calendar/michigan-consumer-sentiment-320", "michigan-consumer-sentiment.csv"), # 米国 ミシガン大学消費者信頼感指数, 重要度: ⭐️⭐
    ("235", "https://jp.investing.com/economic-calendar/personal-spending-235", "personal_spending.csv"), #米国 個人支出, 重要度: ⭐️⭐️（FRBは重要視）
]

# 各URLに対して関数を実行
for table_id, url, file_name in urls_and_files:
    fetch_and_save_data(table_id, url, file_name)