
import sys
import pdfplumber #NOTE: PdfReaderと違いpdfの画像生成したり、テーブル出力できるため

pdf_path = "input/timely_disclosure/" + sys.argv[1]
reader = pdfplumber.open(pdf_path)

raw_text = ""
for i, page in enumerate(reader.pages):
	image = page.to_image(resolution=150)
	image.show()