
#!
import sys
import pdfplumber #NOTE: PdfReaderと違いpdfの画像生成したり、テーブル出力できるため
from pypdf import PdfReader
import tabula

pdf_path = "./bbb.pdf"
#pdf_path = "./input/timely_disclosure/22010_森永製菓株式会社/140120231109583676.pdf"


#df = tabula.read_pdf(pdf_path)
#print(df)

def is_pdf_corrupted(file_path):
    try:
        reader = PdfReader(pdf_path)
        print(len(reader.pages))  # 1ページ以上ない場合は破損の可能性
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"Page {i+1}:\n{text}\n")

    except Exception as exc:
        print("error", exc)
        #return True


is_pdf_corrupted(pdf_path)


#try:
#    reader = pdfplumber.open(pdf_path)
#    for i, page in enumerate(reader.pages):
#        text = page.extract_text()
#        print(f"Page {i+1}:\n{text}\n")
#
#
#        #image = page.to_image(resolution=150)
#        #image.show()
#except Exception as e:
#    print(f"General Error processing {pdf_path}: {e}")
#