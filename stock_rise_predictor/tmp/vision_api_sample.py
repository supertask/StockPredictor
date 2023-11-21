# coding: utf-8
import pdfplumber
import requests
import json
from openai import OpenAI
import time
import base64

class VisionApiSample:
    def __init__(self, pdf_paths):
        self.pdf_paths = pdf_paths
        self.client = OpenAI(api_key = self.get_api_key())
        with open("input/disclosure_pdf_prompt.txt", 'r') as rf:
            self.instruction = rf.read()

    def get_api_key(self):
        with open('.tokens/gpt_api_key.txt', 'r') as file:
            return file.read().strip()
            
    def extract_images_from_pdf(self):
        images = []
        for pdf_path in self.pdf_paths:
            with pdfplumber.open(pdf_path) as pdf:
                for page_number, page in enumerate(pdf.pages):
                    # 最初の3ページのみ処理する
                    if page_number < 3:
                        images.append(page.to_image(width = 2480 / 2))
                    else:
                        break
        return images

    def analyze_images(self):
        images = self.extract_images_from_pdf()

        image_messages = []
        for image in images:
            # 画像をBase64エンコード
            buffered = io.BytesIO()
            #image.show()
            #return
            image.save(buffered, format="PNG")
            base64_image_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_msg = {
                "role": "user", 
                "content": f"data:image/png;base64,{base64_image_string}"
            }
            image_messages.append(image_msg)

        messages = [
            {
                "role": "user",
                "content": self.instruction
            }
        ]
        messages += image_messages

        # 解析リクエストを送信
        response = self.client.chat.completions.create(
            model = "gpt-4-vision-preview",  # 適切なモデルを指定
            messages = messages
        )
        res = response.choices[0]['context']
        print(res)

        return res