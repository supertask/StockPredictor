import os
import pandas as pd
import re
import sys

input_folder = './ipo_doc_getter/input'
reports_folder = './ipo_doc_getter/output/ipo_reports'
output_folder = './output_prompts'

summary_prompt_template = """
# 前提知識1

## ビジネスモデル

以下のビジネスの内、「その他」以外はストック型ビジネスと定義します。
ストック型ビジネスでは、解約数が低くARRが高かったり、施設や店舗などの稼働率が高い状態を維持しながら施設や店舗が順調に増えたり、
する仕組みがあり、それにより契約数や店舗数などが上がるにつれて順調に売上や利益が上がっていくことがある程度保証されるため、テンバガーになりやすいです。

### 多店舗展開ビジネス
店舗や視点などの営業拠点がどんどん増えていくことで、売上や利益が伸びていくビジネスモデル。
必ずしも物理的な店舗を従わないビジネスでも、営業エリアを拡大していれば構いません。
アパレル、小売、飲食業はここから除外してください。

### サブスクビジネス
商品やサービスを売って終わりではなく、毎月あるいは毎年料金を払い続けてもらうことで、定期的かつ継続的に収益を得られるビジネスモデル
業者を乗り換えるハードルが高いビジネスや解約率が低いビジネスであると良い

### 営業人員依存型ビジネス
人材を増やしていくことで収益を増やせるビジネスモデル。
必要条件は、採用数と連動して業績を伸ばせていることと、人材は定期的に働き続けてくれる正社員であること、です。
経験や実績よりもポテンシャルを見極めて採用する力と短期間で戦力化できる育成力があると良いです。

### 保証ビジネス
賃貸不動産の家賃保証ビジネス。賃貸不動産の家賃保証ビジネスであれば、入居者から保証料を受け取って、万一滞納が発生した場合はオーナーに立て替え払いをするようなビジネス。
補償する物件が増えるほど補償料が積み上がる上、賃貸契約の更新や新しい入居者に入れ替わるたびに保証料収入が入り、売上と利益が伸びていくことになる。
また、保証ビジネスは家賃だけでなく、医療や住居設備の保守運用など様々な分野が当てはまります。

例：住宅・事業用家賃保証を主なビジネスとするジェイリース（7187）、住宅ローンの保証を行う全国保証（7164）など

### その他
その他のビジネス。上記のビジネスのような月ごとに継続的に収益が得られるビジネスモデルでない場合、これに該当する。
また、上記のビジネスに該当している場合でも、アパレル、小売、飲食業は継続的に収益が得られにくいため、これに該当します。

ユーザが解約する可能性が高いサービスや商品などもこれに該当する。

# 前提知識2

## 参入障壁の高い企業とは

- トップシェア or オンリーワン企業
- ニッチな市場でビジネスを展開し、覇権を握っている企業
- 大手が狙わないような小さな市場でポジションを持つ企業
- 同業他社がほぼいないような企業
- 簡単に新規参入できないビジネスで成長している企業
- 業界初の商品を保有している企業
- 法律的、ビジネス的、技術的な参入障壁が組み合わさっている企業
- ミッキーマウスの例のように、ブランド力やキャラクターの独占性を持つ企業

など、中・長期的に利益を上げ続けられる参入障壁のある何かを持っている企業のこと。他の会社が真似できない状態であるほど、顧客を獲得しやすいため、ビジネスが継続しやすくなります。
==========================

# 分析
これから、有価証券報告書や会社の説明資料などを与えます。

プロの投資家目線でこれらの書類読んでもらい、以下を教えて

# 1. ビジネスモデル
1.1. ビジネスモデルがストック型であるか否か
1.2. どの点でストック型であると言えるか
1.3. ストック型の場合は以下の子項目を調べて埋めてください。ストック型でない場合は不要です。
1.3.1.「年ごとの契約数や店舗数など（どのくらい推移年ごとに増えていきそうか計算して） 」
1.3.2.「1契約や1店舗で得られる売上や利益」
1.3.3. 年平均成長率がわかれば教えて

2. 参入障壁
	
2.1. 他の競合他社WEB上で調べ、ビジネスの詳細を教えて
2.2. 参入障壁が保たれているか確認するため、2.1での競合と比べて差別化できているのか、また将来その差別化ができなくなる可能性があるか、なるべく具体的に教えて
2.3. トップシェア or オンリーワン企業と言える点があるか否か

3. 課題と解決法

3.1. 解決しようとしている課題は何か
3.2. 3.1の課題をどのように解決しようとするか
3.3. 課題の解決がどのくらい大変か

4. 引用
最後に上記に関して有価証券報告書などの資料のどこを引用したのか、それぞれ最初の30~100文字を引用して記してほしいです。

===========================
有価証券報告書↓
%s
"""

def find_report_file(code):
    # codeに該当するフォルダを見つける
    code_folder_pattern = f"{code}_.*"
    code_folders = [f for f in os.listdir(reports_folder) if os.path.isdir(os.path.join(reports_folder, f)) and re.match(code_folder_pattern, f)]
    
    for folder in code_folders:
        securities_path = os.path.join(reports_folder, folder, 'securities_registration_statement')
        annual_path = os.path.join(reports_folder, folder, 'annual_securities_reports')
        
        # securities_registration_statementフォルダをチェック
        if os.path.exists(securities_path):
            for file in os.listdir(securities_path):
                if file.endswith('.tsv'):
                    return os.path.join(securities_path, file)
        
        # annual_securities_reportsフォルダをチェック
        if os.path.exists(annual_path):
            for file in os.listdir(annual_path):
                if file.endswith('.tsv'):
                    return os.path.join(annual_path, file)
    
    return None


#code = '160A'
#code = '212A'
#code = '2928'
#code = '7092'
#if len(sys.argv) < 2:
#     print('Input company code argument')
#code = sys.argv[1]

code = input()

report_path = find_report_file(code)
if report_path:
	# レポートファイルを読み込み
	report_df = pd.read_csv(report_path, sep='\t')
	
	business_content = report_df.loc[report_df['項目'] == '事業の内容', '値'].values[0]
	business_content = '事業の内容: %s\n' % business_content

	management_pollicy = report_df.loc[report_df['項目'] == '経営方針、経営環境及び対処すべき課題等', '値'].values[0]
	management_pollicy = '経営方針、経営環境及び対処すべき課題等: %s\n' % management_pollicy

	business_risk = report_df.loc[report_df['項目'] == '事業等のリスク', '値'].values[0]
	business_risk = '事業等のリスク: %s\n' % business_risk

	research = report_df.loc[report_df['項目'] == '研究開発活動', '値'].values[0]
	research = '研究開発活動: %s\n' % research

	yukashoken = business_content + management_pollicy + business_risk + research
	summary_prompt = summary_prompt_template % yukashoken
	print(summary_prompt)
else:
	#results.append([code, company_name, ''])
	print(f"Report file not found for code: {code}")