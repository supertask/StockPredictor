import sys

sys.path.append("../realtime_stock_rise_predicter") #mainのモジュール読み込む

from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from db_manager import DBManager
from title_evaluator import TitleEvaluator
import config


def main():
    db_manager = DBManager(config.setting['db']['past'])
    scraper = DisclosureScraper(db_manager)
    scraper.scrape_and_save()
    scraper.close()

    title_evaluator = TitleEvaluator(db_manager)
    title_evaluator.tag_title_on_disclosure()
    title_evaluator.evaluate_longly() #機能してない（dbのfetchがうまくいかない）

    downloader = PdfDownloader(db_manager)
    #try:
    #    pdf_paths_and_tags = downloader.download_all_disclosures()
    #    print(pdf_paths_and_tags)
    #finally:
    #    downloader.close()

    db_manager.close()

if __name__ == "__main__":
    main()
