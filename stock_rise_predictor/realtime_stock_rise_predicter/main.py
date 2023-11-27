from title_evaluator import TitleEvaluator
from pdf_downloader import PdfDownloader
from db_manager import DBManager
from financial_disclosure_analyzer import FinancialDisclosureAnalyzer

def main():
    db_manager = DBManager(config.setting['db']['recent'])
    title_evaluator = TitleEvaluator(db_manager)
    title_evaluator.scrape()
    title_evaluator.tag_title_on_disclosure()
    title_evaluator.evaluate_rise_tags()
    title_evaluator.display_top_evaluations()

    downloader = PdfDownloader(db_manager)
    analyzer = FinancialDisclosureAnalyzer()
    try:
        pdf_paths_tags = downloader.download_top_disclosures()
        analyzer.set_paths(pdf_paths_tags)
        analyzer.analyze()
    finally:
        downloader.close()

if __name__ == "__main__":
    main()