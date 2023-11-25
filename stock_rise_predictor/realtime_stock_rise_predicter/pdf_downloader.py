import os
import subprocess
import db_manager
import config
from db_manager import DBManager

class PdfDownloader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PdfDownloader, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        self.db_manager = DBManager()

    def download_all_disclosures(self):
        # TODO: あとでfetch_top_disclosuresを修正
        evaluated_disclosures = self.db_manager.fetch_top_disclosures(evaluation_threshold=3, tags=config.get_watch_tags())
        return self.download(evaluated_disclosures)
        
    def download_top_disclosures(self):
        evaluated_disclosures = self.db_manager.fetch_top_disclosures(evaluation_threshold=3, tags=config.get_watch_tags())
        return self.download(evaluated_disclosures)

    def download(self, disclosures):
        """ Download PDF and fetch tags
        Returns downloaded pdf and tags
        """
        tag_pdf_paths = []
        for code, date, url, tag in disclosures:
            output_dir = f"output/top_disclosure_pdf/{code}_{date.replace('-', '')}"
            os.makedirs(output_dir, exist_ok=True)
            filename = tag + "_" + os.path.basename(url)
            self.download_pdf(url, output_dir, filename)
            pdf_path = f"{output_dir}/{filename}"
            tag_pdf_paths.append([pdf_path, tag])
        #for pdf_path in tag_pdf_paths:
        #    print(pdf_path)

        return tag_pdf_paths

    def download_pdf(self, url, output_dir, filename):
        output_path = os.path.join(output_dir, filename)
        if not os.path.exists(output_path):
            result = subprocess.run(["wget", "-O", output_path, url], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Download failed for {url}. Error: {result.stderr}")
        #else:
        #    print(f"File already exists: {output_path}")

    def close(self):
        self.db_manager.close()


if __name__ == "__main__":
    downloader = PdfDownloader()
    try:
        pdf_paths_and_tags = downloader.download_top_disclosures()
        print(pdf_paths_and_tags)
    finally:
        downloader.close()

