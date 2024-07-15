
テクニカル指標の使用:

	RSI（相対力指数）(RSI.py):
		RSIが30以下になると、株価が売られすぎていると判断され、反発の可能性が高まる。
		レンジ相場に強く、トレンド相場に弱いRSIの弱点克服, https://www.gaitameonline.com/academy_chart14.jsp

	MACD（移動平均収束拡散法）(MACD.py):
		MACDラインがシグナルラインを下から上にクロスする際に買いシグナルとなる。

	ボリンジャーバンド(bollinger_bands.py):
		株価がボリンジャーバンドの下限に達し、その後バンド内に戻る動きは反発のサインとなる。

	RSI, MACDの組み合わせ
		https://www.sevendata.co.jp/shihyou/mix/macdrsi.html
		https://www.gaitame.com/beginner/market/technical/rsi.html

		

結論的に言えば、MACDは必要ない。RSIはあってもいいかもしれないなと思ったので、試しに使用してみて有効性を検証してみようと思います。????



取引量の分析(trading_volume.py):
	株価が下落している際に取引量が急増し、その後取引量が減少する動きは底打ちの兆候とされる。

