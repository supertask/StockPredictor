
import sys
from pypdf import PdfReader

reader = PdfReader("input/timelyDisclosure/" + sys.argv[1])

raw_text = ""
for i, page in enumerate(reader.pages):
	text = page.extract_text()
	if text:
		raw_text += text
	print(raw_text)
