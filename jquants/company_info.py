import pandas as pd
from dateutil import tz
from datetime import datetime
from dateutil.relativedelta import relativedelta
import jquantsapi
from dataclasses import dataclass

current_date = datetime.now()
REFRESH_TOKEN_FILE_PATH = "./.token/jquantsapi-key.txt"
TSV_PATH = './input/company_codes.tsv'

@dataclass
class CompanyExtra:
    company_code: str
    company_name: str
    pred_datetime: datetime
    pred_high_20: float
    pred_low_20: float
    years_months_since_ipo: str
    ipo_date: datetime
    newest_financial_statement_datetime: datetime
    months_days_since_newest_financial_statement: int
    sector17_code_name: str
    sector33_code_name: str
    
    @classmethod
    def get_header(self):
        return ["会社コード", "会社名", "datetime", "予測高値20", "予測低値20", "IPOからの経過期間", "IPO日", "最新財務諸表日時", "最新財務諸表からの経過月日", "17業種", "33業種"]
    
    def get_info_in_list(self):
        return [
            self.company_code,
            self.company_name,
            self.pred_datetime,
            self.pred_high_20,
            self.pred_low_20,
            self.years_months_since_ipo,
            self.ipo_date,
            self.newest_financial_statement_datetime,
            self.months_days_since_newest_financial_statement,
            self.sector17_code_name,
            self.sector33_code_name,
        ]

class JQuantsExtra:
    def __init__(self):
        self.my_refresh_token = self.get_refresh_token()
        self.client = jquantsapi.Client(refresh_token = self.my_refresh_token)

    def get_refresh_token(self, refresh_token_file_path: str = REFRESH_TOKEN_FILE_PATH):
        with open(refresh_token_file_path, "r") as f:
            refresh_token = f.read().strip()  # rstrip()とlstrip()をstrip()に置き換えて簡潔にしました
        return refresh_token

    def transform_code(self, code):
        """コードが4桁の数字の場合、最後に0を追加します。
        そうでなければ、コードをそのまま返します。 """
        code_str = str(code)
        if len(code_str) == 4 and code_str.isdigit():
            return code_str + "0"
        else:
            return code_str

    def filter_dataframe_with_codes(self, df):
        """ dfから、指定されたコードリストに一致する行のみをフィルタリングして返します。 """
        df_codes = pd.read_csv(TSV_PATH, sep='\t')
        df_codes['code'] = df_codes['code'].apply(self.transform_code)
        unique_codes = df_codes['code'].unique()
        #print(unique_codes)
        return df[df['Code'].isin(unique_codes)]
        
    def get_ipo_and_newest_finance_datetime(self, company_code):
        df = self.client.get_fins_statements(code = company_code)
        df['DisclosedDate'] = pd.to_datetime(df['DisclosedDate'])
        oldest_date = df['DisclosedDate'].min()
        difference = relativedelta(current_date, oldest_date)
        years_months_since_ipo = (f"{difference.years}年{difference.months}ヶ月{difference.days}日")
        ipo_date = oldest_date

        newest_financial_statement_date = df['DisclosedDate'].max()
        newest_financial_statement_time = df[df['DisclosedDate'] == newest_financial_statement_date]['DisclosedTime'].values[0]  # 最新日に一致する行からDisclosedTimeを取得
        newest_financial_statement_datetime = datetime.combine(newest_financial_statement_date, datetime.strptime(newest_financial_statement_time, '%H:%M:%S').time())

        difference = relativedelta(current_date, newest_financial_statement_datetime)
        months_days_since_newest_financial_statement = (f"{difference.years}年{difference.months}ヶ月{difference.days}日")

        company_extra = CompanyExtra(
            company_code = company_code, company_name = "",
            pred_datetime = None, pred_high_20 = 0, pred_low_20 = 0,
            years_months_since_ipo = years_months_since_ipo, ipo_date = ipo_date,
            newest_financial_statement_datetime = newest_financial_statement_datetime,
            months_days_since_newest_financial_statement = months_days_since_newest_financial_statement,
            sector17_code_name = "", sector33_code_name = ""
        )
        
        return company_extra


    def get_companies(self):
        company_scores = pd.read_csv(TSV_PATH, sep='\t')
        company_scores['code'] = company_scores['code'].apply(self.transform_code)
        companies = []
        #df = self.client.get_fins_statements(code = code)
        
        company_df = self.client.get_listed_info()

        for index, company_score in company_scores.iterrows():
            # 追加情報を取得または計算する必要があります
            # 以下はダミーの値で、実際の値を設定する必要があります
            company_code = company_score['code']
            jquants_company_info = company_df[company_df['Code'] == company_code]
            
            company_extra = self.get_ipo_and_newest_finance_datetime(company_code)
            company_extra.pred_datetime = pd.to_datetime(company_score['datetime'])
            company_extra.pred_high_20 = company_score['pred_high_20']
            company_extra.pred_low_20 = company_score['pred_low_20']
            company_extra.company_name = jquants_company_info['CompanyName'].iloc[0]
            company_extra.sector17_code_name = jquants_company_info['Sector17CodeName'].iloc[0]
            company_extra.sector33_code_name = jquants_company_info['Sector33CodeName'].iloc[0]

            
            # TODO: 以下の情報を取得したい
            # https://jpx.gitbook.io/j-quants-ja/api-reference/listed_info
            #"CompanyName": "日本取引所グループ",
            #"Sector17CodeName": "金融（除く銀行）",
            #"Sector33CodeName": "その他金融業",
            # PER
            # ストックビジネスかどうか
            
            companies.append(company_extra)
        return self.sort_companies(companies)

    def sort_companies(self, companies):
        # IPO日が最も新しい順、同じ場合は最後の決算日が最も新しい順にソート
        return sorted(companies, key=lambda x: (x.newest_financial_statement_datetime, x.ipo_date), reverse=True)



def main():
    j_extra = JQuantsExtra()
    #year = j_extra.get_years_from_ipo()
    #print(year)
    companies = j_extra.get_companies()
    company_rows = [CompanyExtra.get_header()]
    for company in companies:
        company_rows.append(company.get_info_in_list())
    tsv_output = "\n".join(["\t".join(map(str, row)) for row in company_rows])

    with open('./output/companies.tsv', 'w') as wf:
        wf.write(tsv_output)

    print(tsv_output)

    
    ## jquantsapiから上場企業情報を取得
    #df_listed_info = client.get_listed_info()
    #print(f"取得したDataFrameのタイプ: {df}")
    
    ## 上場企業情報から、TSVファイルに含まれるコードに一致する行をフィルタリング
    #filtered_df = filter_dataframe_with_codes(df)
    #print(f"フィルタリングされたDataFrame: \n{filtered_df}")
    

    #df = client.get_fins_announcement()
    #df = client.get_fins_statements(code="91660")

    #print(df)
    #unique_code = ["91660"]
    #unique_code = ["83160"]
    #print( df[df['Code'].isin(unique_code)] )

# path_to_your_tsv_file.tsvを実際のファイルパスに置き換えてください。
main()
