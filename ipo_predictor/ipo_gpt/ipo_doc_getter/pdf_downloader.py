import os
import subprocess
import csv
import glob

class PdfDownloader:
    def __init__(self, tsv_pattern):
        self.tsv_pattern = tsv_pattern
        self.output_base_dir = "output/top_disclosure_pdf"  # デフォルトのダウンロードパス

    def set_download_path(self, new_path):
        """ ダウンロードパスを変更する """
        self.output_base_dir = new_path

    def read_tsv_and_filter(self, tsv_file):
        """ TSVファイルを読み込み、条件に合う行をフィルタリング """
        filtered_disclosures = []
        with open(tsv_file, newline='', encoding='utf-8') as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in reader:
                date, time, company_name, company_code, title, url = row
                if "説明資料" in title or "事業計画及び成長可能性" in title:
                    filtered_disclosures.append((company_name, company_code, date, url, title))
        return filtered_disclosures

    def download(self, disclosures):
        """ Download PDF and fetch tags """
        for company_name, company_code, date, url, title in disclosures:
            output_dir = os.path.join(self.output_base_dir, f"{company_code}_{company_name}")
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{date}_{title.replace(' ', '_')}.pdf"
            self.download_pdf(url, output_dir, filename)

    def download_pdf(self, url, output_dir, filename):
        output_path = os.path.join(output_dir, filename)
        if not os.path.exists(output_path):
            result = subprocess.run(["wget", "-O", output_path, url], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Download failed for {url}. Error: {result.stderr}")

    def download_filtered_disclosures(self):
        tsv_files = glob.glob(self.tsv_pattern)
        for tsv_file in tsv_files:
            disclosures = self.read_tsv_and_filter(tsv_file)
            self.download(disclosures)

if __name__ == "__main__":
    tsv_pattern = "output/disclosures_*.tsv"
    downloader = PdfDownloader(tsv_pattern)
    downloader.download_filtered_disclosures()
