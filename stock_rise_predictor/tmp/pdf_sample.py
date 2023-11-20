# coding: utf-8
import pdfplumber
import requests
import json
from openai import OpenAI
import time

class PdfSample:
    def __init__(self, pdf_paths):
        self.pdf_paths = pdf_paths
        self.client = OpenAI(api_key = self.get_api_key())
        with open("input/disclosure_pdf_prompt.txt", 'r') as rf:
            self.instruction = rf.read()

    def get_api_key(self):
        with open('.tokens/gpt_api_key.txt', 'r') as file:
            return file.read().strip()

    def analyze_multiple_pdfs(self):
        """
        複数のPDFファイルを処理し、それらに関連する質問やリクエストに応じて回答を生成する関数
        :param pdf_paths: PDFファイルへのパスのリスト
        :param prompt: PDFに関する質問やリクエスト
        :return: AIによる回答
        """
        try:
            file_ids = []

            #file_list_response = self.client.files.list()
            #for file in file_list_response.data:
            #    print(file.id)
            #    print(file.filename)

            # 各PDFファイルをアップロード
            for pdf_path in self.pdf_paths:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                pdf_upload_response = self.client.files.create(file=pdf_data, purpose='assistants')
                print(pdf_upload_response)
                print(pdf_upload_response.id)
                file_ids.append(pdf_upload_response.id)

            # NOTE: 2023/11/20時点でcode interpreterしかPDF入力は使えず. またcode interpereterだとレスポンスが失敗する
            # GPT-4に質問を送信
            assistant = self.client.beta.assistants.create(
                name = "Timely disclosure Analyzer",
                model = "gpt-4-1106-preview", #model = "gpt-4-vision-preview",
                instructions=self.instruction,
                tools=[{"type": "code_interpreter"}],
                file_ids = file_ids
            )
            print(assistant)

            thread = self.client.beta.threads.create()
            print(thread)
            
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
                #instructions="Pxhh."
            )
            print("run_id:", run.id)

            completed = False
            while not completed:
                run = self.client.beta.threads.runs.retrieve(thread_id = thread.id, run_id = run.id)
                print("run.status:", run.status)
                if run.status == 'completed':
                    completed = True
                else:
                    time.sleep(5)

            if completed:
                thread_message = self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="複数の適時開示のPDFを読み込みその入力をもとにインストラクションにあるJSONを返して",
                    file_ids=file_ids  # 必要に応じてファイルIDを指定
                )
                print(thread_message)

                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                for message in messages:
                    message_content = message.content[0].text
                    print(message_content)
            
            return


            #file_ids = file_ids
            print(assistant)
            print(assistant.choices[0].message.content)

            return response.choices[0].message.content
            #return response['answers'][0]
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None
