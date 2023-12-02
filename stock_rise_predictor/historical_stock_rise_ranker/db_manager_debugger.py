import sys
realtime_module_path = "../realtime_stock_rise_predicter"
sys.path.append(realtime_module_path) #mainのモジュール読み込む

from db_manager import DBManager
from stock_analyzer import StockAnalyzer
import config

class DBManagerDebugger:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def display_tags_for_all_companies_and_dates(self, limit=None):
        # タグがある全ての会社コードと日付の組み合わせを取得（タグの数が多い順）
        all_combinations = self.fetch_all_company_date_combinations(limit)

        # 各組み合わせについてタグを取得して表示
        for code, date, tag_count in all_combinations:
            tags = self.fetch_tags_for_company_and_date(code, date)
            if tags:
                self.display_tags(code, date, tags)

    def fetch_all_company_date_combinations(self, limit=None):
        # すべてのユニークな会社コードと日付の組み合わせを取得（タグの数が多い順）
        query = '''
        SELECT code, date, COUNT(tag) as tag_count
        FROM TimelyDisclosureTags
        GROUP BY code, date
        HAVING COUNT(tag) > 0
        ORDER BY tag_count DESC
        '''
        if limit is not None:
            query += f' LIMIT {limit}'
        cur = self.db_manager.conn.cursor()
        cur.execute(query)
        return cur.fetchall()

    def fetch_tags_for_company_and_date(self, code, date):
        # 特定の会社コードと日付に関連するタグを取得
        cur = self.db_manager.conn.cursor()
        query = '''
        SELECT GROUP_CONCAT(tag, ', ') AS tags
        FROM TimelyDisclosureTags
        WHERE code = ? AND date = ?
        GROUP BY code, date
        '''
        cur.execute(query, (code, date))
        return cur.fetchone()

    def display_tags(self, code, date, tags):
        # タグ情報を整形して表示
        tags_str = tags[0] if tags else "No tags"
        print(f"Code: {code}, Date: {date}, Tags: {tags_str}")
        print("---------------------------------------------------")
        

    def display_stock_rise_and_disclosure_info(self, company_code=None):

        # Fetch data sorted by adj_max_stock_rise in descending order
        data = self.fetch_stock_rise_and_disclosure_info(company_code)
        for index, record in enumerate(data):
            if index > 20: break
            self.display_record(record)


    def display_stock_rise_and_disclosure_info(self, company_code=None):
        data = self.fetch_stock_rise_and_disclosure_info(company_code)
        for record in data:
            self.display_record(record)

    def fetch_stock_rise_and_disclosure_info(self, company_code=None):
        query = '''
        SELECT 
            ue.code, ue.date, ue.adj_max_stock_rise, ue.days_to_adj_max_stock_rise, ue.max_stock_rise, ue.days_to_max_stock_rise, 
            td.title, td.url, ue.rise_tags
        FROM UpwardEvaluation ue
        JOIN TimelyDisclosure td ON ue.code = td.code AND ue.date = td.date
        LEFT JOIN TimelyDisclosureTags tg ON td.date = tg.date AND td.time = tg.time AND td.code = tg.code AND td.title = tg.title
        '''
        params = []
        if company_code:
            query += ' WHERE ue.code = ?'
            params.append(company_code)

        query += ' GROUP BY ue.code, ue.date, ue.adj_max_stock_rise, ue.days_to_adj_max_stock_rise, ue.max_stock_rise, ue.days_to_max_stock_rise, '
        query += ' td.title, td.url '
        query += ' ORDER BY ue.adj_max_stock_rise DESC'
        
        cur = self.db_manager.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def display_record(self, record):
        (code, date, adj_max_stock_rise, days_to_adj_max_stock_rise, max_stock_rise, days_to_max_stock_rise, 
            title, url, tags) = record
        print(f"Code: {code}, Date: {date}, Adj Max Stock Rise: {adj_max_stock_rise}, Days to Adj Max Stock Rise: {days_to_adj_max_stock_rise}, "
            f"Max Stock Rise: {max_stock_rise}, Days to Max Stock Rise: {days_to_max_stock_rise}, "
            f"Title: {title}, URL: {url}, Rise tags: {tags}")
        print("---------------------------------------------------")



if __name__ == "__main__":
    # 使用例
    path = config.setting['db']['past']
    #path = config.setting['db']['recent']
    db_manager = DBManager(path)
    debugger = DBManagerDebugger(db_manager)  # デバッガークラスのインスタンスを作成
    analyzer = StockAnalyzer(db_manager)
    

    #debugger.display_tags_for_all_companies_and_dates(limit=20)  # 最大10件のタグを表示

    code_4_digits = '3563'
    code_5_digits = code_4_digits + '0'

    debugger.display_stock_rise_and_disclosure_info(code_5_digits)

    analyzer.fetch_stock_prices(code_4_digits + '.T')
    analyzer.plot_stock_prices()

