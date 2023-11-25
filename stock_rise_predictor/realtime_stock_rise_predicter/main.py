from title_evaluator import TitleEvaluator
from pdf_downloader import PdfDownloader
from financial_disclosure_analyzer import FinancialDisclosureAnalyzer

def main():
    title_evaluator = TitleEvaluator()
    title_evaluator.scrape()
    title_evaluator.evaluate_simply()

    downloader = PdfDownloader()
    analyzer = FinancialDisclosureAnalyzer()
    try:
        pdf_paths_tags = downloader.download_top_disclosures()
        analyzer.set_paths(pdf_paths_tags)
        analyzer.analyze()
    finally:
        downloader.close()

if __name__ == "__main__":
    main()