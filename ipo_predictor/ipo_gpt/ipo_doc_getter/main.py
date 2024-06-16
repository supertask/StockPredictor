import argparse
from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from edinet_report_getter import EdinetReportGetter

def main():
    parser = argparse.ArgumentParser(description="Disclosure Scraper and EDINET Report Getter")
    parser.add_argument("action", choices=["edinet", "tdnet", "pdf", "all"], help="Action to perform: 'edinet', 'tdnet', 'pdf', 'all'")
    args = parser.parse_args()

    scraper = DisclosureScraper()
    if args.action == "edinet":
        # 金融庁のEDINETから有価証券報告書や四半期報告書を収集し、TSVファイルで保存
        company_dict = scraper.get_company_dict()
        edinet_getter = EdinetReportGetter()
        edinet_getter.save_securities_reports(company_dict)
    elif args.action == "tdnet":
        # 証券取引所のTDNetから適時開示のPDFリンクを集めてTSVに保存
        scraper.scrape_and_save()
    elif args.action == "pdf":
        # tdnetコマンド実行で収集したTSVを元に、PDFをダウンロード
        tsv_pattern = "output/disclosures_*.tsv"
        downloader = PdfDownloader(tsv_pattern)
        downloader.download_filtered_disclosures()

    elif args.action == "all":
        company_dict = scraper.get_company_dict()
        edinet_getter = EdinetReportGetter()
        edinet_getter.save_securities_reports(company_dict)
        scraper.scrape_and_save()
        tsv_pattern = "output/disclosures_*.tsv"
        downloader = PdfDownloader(tsv_pattern)
        downloader.download_filtered_disclosures()


if __name__ == "__main__":
    main()