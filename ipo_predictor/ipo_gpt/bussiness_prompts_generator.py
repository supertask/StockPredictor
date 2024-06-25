import os
import pandas as pd
import re


prompt_template = """
==========
コード	会社名	事業の内容
%s

==========
上記の会社に関して事業内容の項目を参考に、以下のTSVファイルをください。

ビジネスモデル名    ビジネスモデルの詳細
会社名1    <多店舗展開ビジネス, サブスクビジネス, 営業人員依存型ビジネス, 保証ビジネス, その他, のいずれか>    ***
会社名2    <多店舗展開ビジネス, サブスクビジネス, 営業人員依存型ビジネス, 保証ビジネス, その他, のいずれか>    ***
会社名3    <多店舗展開ビジネス, サブスクビジネス, 営業人員依存型ビジネス, 保証ビジネス, その他, のいずれか>    ***
...

==========
# 前提知識1

## ビジネスモデル

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
"""

# フォルダパスの設定
input_folder = './ipo_doc_getter/input'
reports_folder = './ipo_doc_getter/output/ipo_reports'
output_folder = './output_prompts'

# ファイルのリストを取得
input_files = [f for f in os.listdir(input_folder) if f.startswith('ipo_companies_') and f.endswith('.tsv')]

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

# 各ファイルを処理
for input_file in input_files:
    input_path = os.path.join(input_folder, input_file)
    # TSVファイルを読み込み
    df = pd.read_csv(input_path, sep='\t')
    
    results = []
    
    # 各行を処理
    for _, row in df.iterrows():
        code = row['コード']
        company_name = row['企業名']
        
        # 該当するレポートファイルを見つける
        report_path = find_report_file(code)
        
        if report_path:
            # レポートファイルを読み込み
            report_df = pd.read_csv(report_path, sep='\t')
            # 事業内容を抽出
            business_content = report_df.loc[report_df['項目'] == '事業の内容', '値'].values[0]
            # 結果を保存
            results.append([code, company_name, business_content])
        else:
            results.append([code, company_name, ''])
            print(f"Report file not found for code: {code}")
    
    # 出力ファイルの設定
    output_file_base = f'business_{input_file.split("_")[-1].split(".")[0]}'
    output_dir = os.path.join(output_folder, output_file_base)
    os.makedirs(output_dir, exist_ok=True)
    
    # 結果を10行毎に分割して保存
    results_df = pd.DataFrame(results, columns=['コード', '企業名', '事業内容'])
    num_chunks = (len(results_df) // 10) + (1 if len(results_df) % 10 != 0 else 0)
    
    for i in range(num_chunks):
        chunk_df = results_df.iloc[i*10:(i+1)*10]
        business_list = chunk_df.to_csv(sep='\t', index=False, header=False)
        prompt_text = prompt_template % business_list

        chunk_output_path = os.path.join(output_dir, f'{output_file_base}_part_{i+1}.txt')
        with open(chunk_output_path, 'w', encoding='utf-8') as f:
            f.write(prompt_text)

print("Processing complete.")