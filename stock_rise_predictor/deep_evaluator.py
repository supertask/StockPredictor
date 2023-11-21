import os
import subprocess
import db
import config
from financial_disclosure_analyzer import FinancialDisclosureAnalyzer

def download_pdf(url, output_dir, filename):
    output_path = os.path.join(output_dir, filename)
    if not os.path.exists(output_path):
        result = subprocess.run(["wget", "-O", output_path, url], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Download failed for {url}. Error: {result.stderr}")
    #else:
    #    print(f"File already exists: {output_path}")

def analyze_top_disclosure(conn):

    # Fetch data with evaluation 3 or more
    evaluated_disclosures = db.fetch_evaluated_disclosures(conn, evaluation_threshold = 3, tags = config.get_watch_tags())
    #print(evaluated_disclosures)

    tag_pdf_paths = []
    for code, date, url, tag in evaluated_disclosures:
        output_dir = f"output/top_disclosure_pdf/{code}_{date.replace('-', '')}"
        os.makedirs(output_dir, exist_ok=True)

        filename = tag + "_" + os.path.basename(url)
        download_pdf(url, output_dir, filename)
        
        pdf_path = f"{output_dir}/{filename}"
        tag_pdf_paths.append([pdf_path, tag])

    #tag_pdf_paths = [
    #    ['input/timely_disclosure/83160_三井住友銀行/140120231013566890.pdf',"決算短信"], #短信
    #    ['input/timely_disclosure/43740_Ｇ－ロボペイ/140120231113587641.pdf', "決算短信"], #短信
    #    #'input/timely_disclosure/22010_森永製菓株式会社/140120231109583676.pdf', #短信
    #]

    #for pdf_path in tag_pdf_paths:
    #    print(pdf_path)

    analyzer = FinancialDisclosureAnalyzer(tag_pdf_paths)
    analyzer.analyze()


if __name__ == "__main__":
    conn = db.create_database()
    analyze_top_disclosure(conn)
    conn.close()

