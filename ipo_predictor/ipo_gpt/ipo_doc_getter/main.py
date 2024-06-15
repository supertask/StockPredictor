from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from edinet_report_getter import EdinetReportGetter

def main():
    #scraper = DisclosureScraper()
    #scraper.scrape_and_save()
    tsv_pattern = "output/disclosures_*.tsv"
    downloader = PdfDownloader(tsv_pattern)
    downloader.download_filtered_disclosures()

    # 有価証券報告書をjsonで取得
    #company_dict = scraper.get_company_dict()
    #edinet_getter = EdinetReportGetter()
    #edinet_getter.save_securities_reports(company_dict)


if __name__ == "__main__":
    main()