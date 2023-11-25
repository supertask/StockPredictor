import os
import subprocess
import db
import config

class PdfDownloader:
    def __init__(self):
        self.conn = db.create_database()


    def download_disclosures(self):
        """ Download PDF and fetch tags
        Returns downloaded pdf and tags
        """
        evaluated_disclosures = db.fetch_evaluated_disclosures(self.conn, evaluation_threshold=3, tags=config.get_watch_tags())
        tag_pdf_paths = []
        for code, date, url, tag in evaluated_disclosures:
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
        self.conn.close()


if __name__ == "__main__":
    downloader = PdfDownloader()
    try:
        pdf_paths_and_tags = downloader.download_disclosures()
        print(pdf_paths_and_tags)
    finally:
        downloader.close()

