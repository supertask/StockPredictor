


## 評価関数

株が上がりそうな要素が3つ以上あれば、その企業をOpenAIのキーで探索する

## 適時開示の過去の情報
	https://www2.jpx.co.jp/tseHpFront/JJK010010Action.do?Show=Show
	
## TODO:

ニュースや適時開示の情報の中に以下のような株価を押し上げる情報があるかをChatGPTに聞くAPIを作る

 - 新製品やサービスの発表
 - 戦略的提携やパートナーシップ
 - 財務健全性の改善
 - 新たな市場への進出
 - 経営陣の変更
 - 特許取得や技術的な進歩

 テンバガーの人がみている適時開示情報

-「決算短信」
-「中期経営計画」
-「業績予想の修正」
-「受注」（大型受注, 大口受注は強そう, 訂正は注意）
-「月次情報」


それぞれの項目をAPIで投げるようにする。
	決算短信 -> in:image -> 
	配当 -> in:image -> output:json,tableで見れるように
	自己株式取得 -> in: -> output:comment: サイトから見れるように
	上方修正 -> 
	株式分割 -> in
	業績予想の修正 -> in -> output:json,tableで見れるように

リンクをサイトに送る
	決算資料
	
	
## Idea

### 日経平均株価を説明変数とする回帰モデルの作成

	X = sm.add_constant(nikkei_average)  # 定数項（バイアス）を追加
	model = sm.OLS(stock_prices, X).fit()

https://chat.openai.com/share/72932f83-a77b-4d5f-96bc-699450d5eeea
