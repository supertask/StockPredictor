import base64
import pdfplumber
from openai import OpenAI
import config
import io
import requests
import json
import time

class FinancialDisclosureAnalyzer:
    def __init__(self, pdf_tag_paths):
        self.pdf_tag_paths = pdf_tag_paths
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
        self.tag_prompt_path_dict = config.get_tag_prompt_path_dict()
        #with open("input/kessan_tanshin_pdf_prompt.txt", 'r') as rf:
        #    self.instruction = rf.read()

    def get_api_key(self):
        with open('.tokens/gpt_api_key.txt', 'r') as file:
            return file.read().strip()

    def extract_from(self, pdf_path):
        table_text = "table(focus to see on this):\n"
        entire_sentence = "sentence(this includes table text. but that can be noise. be careful):\n"
        try:
            #NOTE: Data-loss while decompressing corrupted dataのエラーの時はextract_tables, extract_textともに空
            with pdfplumber.open(pdf_path) as pdf_file:
                table_text = self.extract_tables(pdf_file) if self.use_table_analyze else ''
                entire_sentence = self.extract_text(pdf_file) if self.use_sentense_analyze else ''
                if table_text or entire_sentence:
                    return table_text + "\n===\n" + entire_sentence
                else:
                    return None
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return None
            
    def extract_tables(self, pdf_file):
        table_text = "table(focus to see on this):\n"
        for page_index, page in enumerate(pdf_file.pages):
            if page_index > self.page_for_table:
                break
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    row_text = '|'.join([cell.replace("\n", "<br>") if cell else "None" for cell in row])
                    table_text += f'|{row_text}|\n'
        return table_text

    def extract_text(self, pdf_file):
        entire_sentence = "sentence(this includes table text. but that can be noise. be careful):\n"
        for page_index, page in enumerate(pdf_file.pages):
            if page_index + 1 > self.page_for_sentense:
                break
            page_text = page.extract_text()
            if page_text:
                entire_sentence += page_text + "\n"
        return entire_sentence


        #with pdfplumber.open(pdf_path) as pdf_file:
        #    for page_index, page in enumerate(pdf_file.pages):
        #        page_number = page_index
        #        if page_number > self.page_for_table:
        #            break
        #        # ページからテーブルを抽出
        #        tables = page.extract_tables()
        #        for table in tables:
        #            for row in table:
        #                new_row = []
        #                for cell in row:
        #                    if cell in [None, '']:
        #                        cell = "None"
        #                    cell = cell.replace("\n", "<br>")
        #                    new_row.append(cell)
        #                row_text = '|'.join(new_row)
        #                table_text += f'|{row_text}|\n'

        #    for page_index, page in enumerate(pdf_file.pages):
        #        page_number = page_index + 1
        #        if page_number > self.page_for_sentense:
        #            break
        #        # ページからテキストを抽出
        #        page_text = page.extract_text()
        #        if page_text:
        #            entire_sentence += page_text + "\n"
        #if not self.use_table_analyze:
        #    table_text = ''
        #if not self.use_sentense_analyze:
        #    entire_sentence = ''
        #return table_text + "\n===\n" + entire_sentence

    def analyze_pdf_text(self, pdf_text, tag):
        #print(pdf_text)
        print(len(pdf_text))

        prompt_path = self.tag_prompt_path_dict[tag]
        prompt = ""
        with open(prompt_path, 'r') as rf:
            prompt = rf.read()
        #print(prompt)

        return

        messages = [
            {
                "role": "assistant",
                "content": prompt
            },
            {
                "role": "user",
                "content": pdf_text
            }
        ]
        response = self.client.chat.completions.create(
            model = "gpt-3.5-turbo-1106",
            #model = "gpt-4-1106-preview",
            response_format={ "type": "json_object" },
            messages = messages
        )
        print(response)
        res = response.choices[0].message.content

        print(res)

        return res

    def analyze_pdfs(self):
        for index, pdf_tag_path in enumerate(self.pdf_tag_paths):
            
            # DEBUG!!!!!!!!!!!!!!!!!!!!!
            if index > 5:
                break

            pdf_path, tag = pdf_tag_path
            print(pdf_path, tag)
            pdf_text = self.extract_from(pdf_path)
            if pdf_text:
                self.analyze_pdf_text(pdf_text, tag)

    def analyze(self):
        results = self.analyze_pdfs()
        #results = self.analyze_multiple_pdfs()
        #print(results)
        ## 解析結果をJSON形式で保存
        #with open('results.json', 'w') as f:
        #    json.dump(results, f)
