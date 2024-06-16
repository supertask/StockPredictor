import sys

sys.path.append("../realtime_stock_rise_predicter") #mainのモジュール読み込む

from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from db_manager import DBManager
from title_evaluator import TitleEvaluator
from stock_analyzer import StockAnalyzer
import config


def main():
    db_manager = DBManager(config.setting['db']['past'])

    # TODO: スクレーピンングしたデータがあっているか確認する & 株価上昇率のやつ問題ないかも知っている銘柄でチェック
    #scraper = DisclosureScraper(db_manager)
    #scraper.scrape_and_save()
    #scraper.close()

    title_evaluator = TitleEvaluator(db_manager)
    title_evaluator.tag_title_on_disclosure()
    title_evaluator.evaluate_historical_rise_tags()

    ## TODO: ここで日付を元に上昇率を全ての銘柄で計算し、それを評価テーブルに入れる。
    analyzer = StockAnalyzer(db_manager)
    analyzer.calc_rise_and_fall_rates() #上昇率を全ての銘柄で計算し、それを評価テーブルに入れる

    # TODO: 上昇率が高い順にChatGPT GPTsで（利益率の上昇率, 配当の上昇率など, 上昇率の高いタグも見つける）. 


    downloader = PdfDownloader(db_manager)
    #try:
    #    pdf_paths_and_tags = downloader.download_all_disclosures()
    #    print(pdf_paths_and_tags)
    #finally:
    #    downloader.close()

    db_manager.close()

if __name__ == "__main__":
    main()
