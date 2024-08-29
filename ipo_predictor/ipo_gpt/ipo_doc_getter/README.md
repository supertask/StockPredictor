# IPO Document getter 

## How to run

### 1. 金融庁のEDINETから有価証券報告書や四半期報告書を収集し、TSVファイルで保存

	python3 main.py edinet


### 2. 証券取引所のTDNetから適時開示のPDFリンクを集めてTSVに保存

	python3 main.py tdnet
	
指定したIPOの会社コードと企業名の入った `../ipo_csv/input/companies_<year>.tsv` のファイル群を `input/companies_<year>.tsv` に入れ、TDNetを実行すると入力の企業の適時開示を収集してくれる

`edinet_report_getter.py` の `self.searching_past_year` を変更すると


### 3. tdnetコマンド実行で収集したTSVを元に、PDFをダウンロード

	python3 main.py pdf

TDNetの適時開示のサイトからダウンロードしたい適時開示は `input/downloading_pdf_codes.tsv` で指定する。会社コード一覧を入力する。


### 4. 1~3を全て実行

	python3 main.py all
	
	

