import db
import title_evaluator as title_evaluator
from pdf_downloader import PdfDownloader
from financial_disclosure_analyzer import FinancialDisclosureAnalyzer

def main():
    conn = db.create_database()
    title_evaluator.scrape(conn)
    title_evaluator.evaluate_simply(conn)

    downloader = PdfDownloader()
    analyzer = FinancialDisclosureAnalyzer()
    try:
        pdf_paths_tags = downloader.download_disclosures()
        analyzer.set_paths(pdf_paths_tags)
        analyzer.analyze()
    finally:
        downloader.close()

if __name__ == "__main__":
    main()