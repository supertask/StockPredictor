import argparse
from disclosure_scraper import DisclosureScraper
from pdf_downloader import PdfDownloader
from edinet_report_getter import EdinetReportGetter

def main():
    parser = argparse.ArgumentParser(
        description="Disclosure Scraper and EDINET Report Getter",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("action", choices=["edinet", "tdnet", "pdf", "all"],
        help=(
            "Action to perform:\n"
            "'edinet' - Collect securities reports and quarterly reports from the Financial Services Agency's EDINET and save them as TSV files\n"
            "'tdnet' - Collect timely disclosure PDF links from the stock exchange's TDNet and save them as TSV files\n"
            "'pdf' - Download PDFs based on the TSV collected with the 'tdnet' command\n"
            "'all' - Perform the following actions in sequence:\n"
            "  1. Collect securities reports and quarterly reports from the Financial Services Agency's EDINET and save them as TSV files\n"
            "  2. Collect timely disclosure PDF links from the stock exchange's TDNet and save them as TSV files\n"
            "  3. Download PDFs based on the TSV collected with the 'tdnet' command"
        )
    )
    args = parser.parse_args()

    scraper = DisclosureScraper()
    if args.action == "edinet":
        # 金融庁のEDINETから有価証券報告書や四半期報告書を収集し、TSVファイルで保存
        companies_list = scraper.get_companies_list()
        edinet_getter = EdinetReportGetter()
        edinet_getter.save_securities_reports(companies_list)
    elif args.action == "tdnet":
        # 証券取引所のTDNetから適時開示のPDFリンクを集めてTSVに保存
        scraper.scrape_and_save()
    elif args.action == "pdf":
        # tdnetコマンド実行で収集したTSVを元に、PDFをダウンロード
        tsv_pattern = "output/disclosures_*.tsv"
        downloader = PdfDownloader(tsv_pattern)
        downloader.download_filtered_disclosures()

    elif args.action == "all":
        # 1.金融庁のEDINETから有価証券報告書や四半期報告書を収集し、TSVファイルで保存
        # 2.証券取引所のTDNetから適時開示のPDFリンクを集めてTSVに保存
        # 3.tdnetコマンド実行で収集したTSVを元に、PDFをダウンロード
        companies_list = scraper.get_companies_list()
        edinet_getter = EdinetReportGetter()
        edinet_getter.save_securities_reports(companies_list)
        scraper.scrape_and_save()
        tsv_pattern = "output/disclosures_*.tsv"
        downloader = PdfDownloader(tsv_pattern)
        downloader.download_filtered_disclosures()

if __name__ == "__main__":
    main()