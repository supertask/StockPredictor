import os
import requests
import zipfile

# ダウンロードするURL
url = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
# 保存先ディレクトリ
save_dir = "./input/Edinetcode"

# ディレクトリが存在しない場合は作成
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# ZIPファイルのパス
zip_path = os.path.join(save_dir, "Edinetcode.zip")

# ZIPファイルをダウンロード
response = requests.get(url)
with open(zip_path, "wb") as file:
    file.write(response.content)

# ZIPファイルを展開
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(save_dir)

# ZIPファイルを削除（必要に応じて）
os.remove(zip_path)

print(f"ファイルは {save_dir} に展開されました。")

