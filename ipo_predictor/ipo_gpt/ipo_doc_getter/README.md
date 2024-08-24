# IPO Document getter 

## How to run

### 1. 金融庁のEDINETから有価証券報告書や四半期報告書を収集し、TSVファイルで保存

	python3 main.py edinet


### 2. 証券取引所のTDNetから適時開示のPDFリンクを集めてTSVに保存

	python3 main.py tdnet
	
`edinet_report_getter.py` の `self.searching_past_year` を変更すると

### 3. tdnetコマンド実行で収集したTSVを元に、PDFをダウンロード

	python3 main.py pdf

### 4. 1~3を全て実行

	python3 main.py all