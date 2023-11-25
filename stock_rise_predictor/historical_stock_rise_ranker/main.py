import sys

sys.path.append("../realtime_stock_rise_predicter") #mainのモジュール読み込む

from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader


def main():
    scraper = DisclosureScraper()
    scraper.scrape_disclosure_history('8316')
    scraper.close()

    downloader = PdfDownloader()
    try:
        pdf_paths_and_tags = downloader.download_all_disclosures()
        print(pdf_paths_and_tags)
    finally:
        downloader.close()

if __name__ == "__main__":
    main()
