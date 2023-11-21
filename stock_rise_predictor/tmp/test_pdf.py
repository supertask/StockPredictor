
import sys
import pdfplumber #NOTE: PdfReaderと違いpdfの画像生成したり、テーブル出力できるため
from pypdf import PdfReader
import tabula

pdf_path = "./input/timely_disclosure/42020_ダイセル/140120231030574481.pdf"
#pdf_path = "./input/timely_disclosure/22010_森永製菓株式会社/140120231109583676.pdf"


#df = tabula.read_pdf(pdf_path)
#print(df)

#def is_pdf_corrupted(file_path):
#    try:
#        with open(file_path, 'rb') as file:
#            reader = PdfReader(file)
#            print(len(reader.pages))  # 1ページ以上ない場合は破損の可能性
#    except Exception as exc:
#        print("error", exc)
#        #return True
#

#is_pdf_corrupted(pdf_path)


try:
    reader = pdfplumber.open(pdf_path)
    for i, page in enumerate(reader.pages):
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print("row: ", row)

        text = page.extract_text()
        #print("text", text)

        #image = page.to_image(resolution=150)
        #image.show()
except Exception as e:
    print(f"General Error processing {pdf_path}: {e}")
