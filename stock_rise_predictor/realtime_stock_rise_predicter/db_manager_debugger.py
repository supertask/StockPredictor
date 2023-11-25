from db_manager import DBManager
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

# 使用例
path = config.setting['db']['past']
#path = config.setting['db']['recent']
db_manager = DBManager(path)
debugger = DBManagerDebugger(db_manager)  # デバッガークラスのインスタンスを作成
debugger.display_tags_for_all_companies_and_dates(limit=20)  # 最大10件のタグを表示
