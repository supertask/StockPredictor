import os
import subprocess
import glob
import pandas as pd
class PdfDownloader:
    def __init__(self, tsv_pattern):
        self.tsv_pattern = tsv_pattern
        self.output_base_dir = "output/ipo_reports"  # デフォルトのダウンロードパス

    def set_download_path(self, new_path):
        """ ダウンロードパスを変更する """
        self.output_base_dir = new_path

    #def read_tsv_and_filter(self, tsv_file):
    #    """ TSVファイルを読み込み、条件に合う行をフィルタリング """
    #    filtered_disclosures = []
    #    with open(tsv_file, newline='', encoding='utf-8') as tsvfile:
    #        reader = csv.reader(tsvfile, delimiter='\t')
    #        for row in reader:
    #            date, time, company_name, company_code, title, url = row
    #            if "説明資料" in title or "事業計画及び成長可能性" in title:
    #                filtered_disclosures.append((company_name, company_code, date, url, title))
    #    return filtered_disclosures
        
    def read_tsv_and_filter(self, tsv_file):
        """ TSVファイルを読み込み、条件に合う行をフィルタリング """
        df = pd.read_csv(tsv_file, delimiter='\t', header=None,
                        names=['date', 'time', 'company_name', 'company_code', 'title', 'url'])
        # 古い順にソート
        df = df.sort_values(by=['company_code', 'date'])
        
        filtered_disclosures = []
        grouped = df.groupby('company_code')

        for company_code, group in grouped:
            #print(company_code)
            # 条件に合うものをフィルタリング
            filtered_group = group[group['title'].str.contains("説明資料|事業計画及び成長可能性", regex=True)]
            # 古い順に5つだけ取得
            top_disclosures = filtered_group.head(5)
            filtered_disclosures.extend(top_disclosures.to_dict('records'))
        return filtered_disclosures
    

    def download(self, disclosures):
        """ Download PDF and fetch tags """
        for disclosure in disclosures:
            #print(disclosure)
            company_name = disclosure['company_name']
            company_code = disclosure['company_code']
            date = disclosure['date']
            url = disclosure['url']
            title = disclosure['title']
            
            output_dir = os.path.join(self.output_base_dir, f"{company_code}_{company_name}")
            os.makedirs(output_dir, exist_ok=True)
            title = title.replace(' ', '_').replace("/", "_") 
            filename = f"{date}_{title}.pdf"
            self.check_and_download_pdf(url, output_dir, filename)
            #break

    def get_file_size(self, url):
        result = subprocess.run(["wget", "--spider", url], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to get file size for {url}. Error: {result.stderr}")
        for line in result.stderr.splitlines():
            if 'Length:' in line:
                size_str = line.split()[1]
                if size_str.isdigit():
                    return int(size_str)
        return 0

    def check_and_download_pdf(self, url, output_dir, filename):
        output_path = os.path.join(output_dir, filename)
        if os.path.exists(output_path):
            print(f"Skip downloading PDF, {output_path}")
            return
        file_size = self.get_file_size(url)
        if file_size > 50 * 1024 * 1024:  # 100MB
            print(f"\033[91mWARNING: Skipping download for {url}, file size is {file_size / (1024 * 1024):.2f} MB\033[0m")
        else:
            self.download_pdf(url, output_path)

    def download_pdf(self, url, output_path):
        result = subprocess.run(["wget", "-O", output_path, url], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Downloaded PDF, {output_path}")
        else:
            raise Exception(f"Download failed for {url}. Error: {result.stderr}")

    def download_filtered_disclosures(self):
        tsv_files = glob.glob(self.tsv_pattern)
        for tsv_file in tsv_files:
            disclosures = self.read_tsv_and_filter(tsv_file)
            self.download(disclosures)
        print('Finished')

if __name__ == "__main__":
    tsv_pattern = "output/disclosures_*.tsv"
    downloader = PdfDownloader(tsv_pattern)
    downloader.download_filtered_disclosures()
