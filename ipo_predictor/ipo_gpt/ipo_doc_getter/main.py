from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader

def main():
    scraper = DisclosureScraper()
    scraper.scrape_and_save()

    tsv_pattern = "output/disclosures_*.tsv"
    downloader = PdfDownloader(tsv_pattern)
    downloader.download_filtered_disclosures()

if __name__ == "__main__":
    main()