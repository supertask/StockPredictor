import fitz  # PyMuPDFのインポート

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    all_text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        all_text += page.get_text()
    return all_text

pdf_path = "/mnt/data/aaa.pdf"  # アップロードされたPDFファイルのパスを指定
extracted_text = extract_text_from_pdf(pdf_path)

# 抽出されたテキストをファイルに保存
with open("/mnt/data/extracted_text.txt", "w", encoding="utf-8") as text_file:
    text_file.write(extracted_text)

print("テキストの抽出が完了しました。抽出されたテキストは 'extracted_text.txt' ファイルに保存されました。")
