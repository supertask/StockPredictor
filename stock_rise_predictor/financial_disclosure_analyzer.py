import base64
import pdfplumber
from openai import OpenAI
import io
import requests
import json
import time

class FinancialDisclosureAnalyzer:
    def __init__(self, pdf_paths):
        self.pdf_paths = pdf_paths
        self.use_table_analyze = True
        self.use_sentense_analyze = True

        # 値段換算
        # 3000文字 -> 10000token -> $0.1
        # $0.1 * 4 [num of pdf] * 10社数 -> $4
        # 1000文字 -> 3000token -> $0.03 
        # $0.03 * 4 [num of pdf] * 10社数 -> $1.2
        # gpt-4-1106-preview: $0.01 / 1K tokens
        self.page_for_table = 2 #Xページ目まで
        self.page_for_sentense = 1 #Yページ目まで
        self.client = OpenAI(api_key = self.get_api_key())
        with open("input/kessan_tanshin_pdf_prompt.txt", 'r') as rf:
            self.instruction = rf.read()

    def extract_text_from_pdf(self):
        table_text = "table(focus to see on this):\n"
        entire_sentence = "sentence(this includes table text. but that can be noise. be careful):\n"
        for pdf_path in self.pdf_paths:
            with pdfplumber.open(pdf_path) as pdf:
                for page_index, page in enumerate(pdf.pages):
                    page_number = page_index
                    if page_number > self.page_for_table:
                        break
                    # ページからテーブルを抽出
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            new_row = []
                            for cell in row:
                                if cell in [None, '']:
                                    cell = "None"
                                cell = cell.replace("\n", "<br>")
                                new_row.append(cell)
                            row_text = '|'.join(new_row)
                            table_text += f'|{row_text}|\n'

                for page_index, page in enumerate(pdf.pages):
                    page_number = page_index + 1
                    if page_number > self.page_for_sentense:
                        break
                    # ページからテキストを抽出
                    page_text = page.extract_text()
                    if page_text:
                        entire_sentence += page_text + "\n"
        if not self.use_table_analyze:
            table_text = ''
        if not self.use_sentense_analyze:
            entire_sentence = ''

        return table_text + "\n===\n" + entire_sentence
        
    def get_api_key(self):
        with open('.tokens/gpt_api_key.txt', 'r') as file:
            return file.read().strip()

    def analyze_pdf_text(self):
        pdf_text = self.extract_text_from_pdf()
        #print(pdf_text)
        #print(len(pdf_text))
        #return

        messages = [
            {
                "role": "assistant",
                "content": self.instruction
            },
            {
                "role": "user",
                "content": pdf_text
            }
        ]
        response = self.client.chat.completions.create(
            model = "gpt-4-1106-preview",
            response_format={ "type": "json_object" },
            messages = messages
        )
        print(response)
        res = response.choices[0].message.content
        print(res)

        return res

    def process_disclosures(self):
        results = self.analyze_pdf_text()
        #results = self.analyze_multiple_pdfs()
        #print(results)
        ## 解析結果をJSON形式で保存
        #with open('results.json', 'w') as f:
        #    json.dump(results, f)

# 使用例
pdf_paths = [
    ['input/timely_disclosure/83160_三井住友銀行/140120231013566890.pdf',"決算短信"], #短信
    ['input/timely_disclosure/43740_Ｇ－ロボペイ/140120231113587641.pdf', "決算短信"], #短信
    #'input/timely_disclosure/22010_森永製菓株式会社/140120231109583676.pdf', #短信
]
analyzer = FinancialDisclosureAnalyzer(pdf_paths)
analyzer.process_disclosures()
