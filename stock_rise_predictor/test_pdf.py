
from pypdf import PdfReader
reader = PdfReader('140120231113587073.pdf')

for i, page in enumerate(reader.pages):
	text = page.extract_text()
	if text:
		raw_text += text
	raw_text