#
# 流動性の高い株を調べるツール
#

import yfinance as yf
import pandas as pd

# 調べる期間（例：過去1ヶ月）
period_str = '1mo'

# 調査する銘柄リスト
#ipo_companies = {
#    '1879': '新日本建設',
#    '3496': 'アズーム',
#    '3774': 'インターネットイニシアティブ',
#    '4480': 'メドレー',
#    '5588': 'ファーストアカウンティング',
#    '7071': 'アンビスHD',
#    '7086': 'きずなHD',
#    '7115': 'アルファパーチェス',
#    '7320': '日本リビング保証',
#    '7386': 'ジャパンワランティサポート',
#    '7388': 'FPパートナー',
#    '9158': 'シーユーシー',
#    '9166': 'ＧＥＮＤＡ',
#    '160A': 'アズパートナーズ',
#    '212A': 'フィットイージー',
#}
ipo_companies = {
	'215A': 'タイミー',
}

tickers = [key + '.T' for key in ipo_companies.keys()]

# データフレームを準備
result = []

# 各銘柄の売買回転率を計算
for ticker in tickers:
    data = yf.Ticker(ticker)
    
    # 過去データを取得
    hist = data.history(period=period_str)
    
    # 取引量の合計を計算
    total_volume = hist['Volume'].sum()
    
    # 発行済株式数を取得
    shares_outstanding = data.info.get('sharesOutstanding', None)
    if ticker == '160A.T':
        shares_outstanding = 3559500
    if ticker == '212A.T':
        shares_outstanding = 15840000
    if ticker == '215A.T':
        shares_outstanding = 95139000
    
    if shares_outstanding:
        # 売買回転率を計算
        turnover_rate = total_volume / shares_outstanding
    else:
        turnover_rate = None
    
    result.append({
        'コード': ticker.split('.')[0],
        '会社名': ipo_companies[ticker.split('.')[0]],
        '売買回転率': turnover_rate,
        '取引量の合計': total_volume,
        '発行済株式数': shares_outstanding
    })

# データフレームに変換し、結果を表示
df = pd.DataFrame(result)

# 流動性でソート
df = df.dropna().sort_values(by='売買回転率', ascending=False)

# TSV形式で出力
print(df.to_csv(sep='\t', index=False))