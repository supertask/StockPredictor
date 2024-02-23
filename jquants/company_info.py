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
    years_months_since_ipo: str
    ipo_date: datetime
    newest_financial_statement_datetime: datetime
    months_days_since_newest_financial_statement: int
    datetime: datetime
    pred_high_20: float
    pred_low_20: float
    

    def __str__(self):
        return (f"会社コード: {self.company_code}, "
                f"会社名: {self.company_name}, "
                f"IPOからの経過期間: {self.years_months_since_ipo}, "
                f"IPO日: {self.ipo_date.strftime('%Y-%m-%d')}, "
                f"最新財務諸表日時: {self.newest_financial_statement_datetime.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"最新財務諸表からの経過月日: {self.months_days_since_newest_financial_statement}, "
                f"予測高値20: {self.pred_high_20}, "
                f"予測低値20: {self.pred_low_20}")

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
        print(unique_codes)
        return df[df['Code'].isin(unique_codes)]
        
    def get_ipo_and_newest_finance_datetime(self, company_code):
        df = self.client.get_fins_statements(code = company_code)
        df['DisclosedDate'] = pd.to_datetime(df['DisclosedDate'])
        oldest_date = df['DisclosedDate'].min()
        difference = relativedelta(current_date, oldest_date)
        years_months_since_ipo = (f"{difference.years}年, {difference.months}ヶ月, {difference.days}日")
        ipo_date = oldest_date

        newest_financial_statement_date = df['DisclosedDate'].max()
        newest_financial_statement_time = df[df['DisclosedDate'] == newest_financial_statement_date]['DisclosedTime'].values[0]  # 最新日に一致する行からDisclosedTimeを取得
        newest_financial_statement_datetime = datetime.combine(newest_financial_statement_date, datetime.strptime(newest_financial_statement_time, '%H:%M:%S').time())

        difference = relativedelta(current_date, newest_financial_statement_datetime)
        months_days_since_newest_financial_statement = (f"{difference.years}年, {difference.months}ヶ月, {difference.days}日")

        company_extra = CompanyExtra(
            company_code = company_code, years_months_since_ipo = years_months_since_ipo, ipo_date = ipo_date,
            newest_financial_statement_datetime = newest_financial_statement_datetime,
            months_days_since_newest_financial_statement = months_days_since_newest_financial_statement,
            datetime = None, pred_high_20 = 0, pred_low_20 = 0, company_name = ""
        )
        
        return company_extra


    def get_companies(self):
        company_scores = pd.read_csv(TSV_PATH, sep='\t')
        company_scores['code'] = company_scores['code'].apply(self.transform_code)
        companies = []
        #df = self.client.get_fins_statements(code = code)

        for index, company_score in company_scores.iterrows():
            # 追加情報を取得または計算する必要があります
            # 以下はダミーの値で、実際の値を設定する必要があります
            company_code = company_score['code']
            
            company_extra = self.get_ipo_and_newest_finance_datetime(company_code)
            company_extra.datetime = pd.to_datetime(company_score['datetime'])
            company_extra.pred_high_20 = company_score['pred_high_20']
            company_extra.pred_low_20 = company_score['pred_low_20']
            company_extra.company_name = ""
            
            companies.append(company_extra)
        return self.sort_companies(companies)

    def sort_companies(self, companies):
        # IPO日が最も新しい順、同じ場合は最後の決算日が最も新しい順にソート
        return sorted(companies, key=lambda x: (x.ipo_date, x.newest_financial_statement_datetime), reverse=True)



def main():
    j_extra = JQuantsExtra()
    #year = j_extra.get_years_from_ipo()
    #print(year)
    companies = j_extra.get_companies()
    for company in companies:
        print(company) 
    
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
