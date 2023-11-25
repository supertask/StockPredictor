import sqlite3
from enum import Enum, auto

class DBManager:
    class Table(Enum):
        TimelyDisclosure = auto()
        UpwardEvaluation = auto()
        Company = auto()
        TimelyDisclosureTags = auto()    

    def __init__(self, db_path):
        #'output/timely_disclosure.db'
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def change_db(self, new_path):
        """ データベースのパスを変更し、新しいパスで接続を開始する """
        self.conn.close()  # 現在の接続を閉じる
        self.db_path = new_path
        self.conn = sqlite3.connect(self.db_path)  # 新しいパスで接続
        self.create_tables()  # 必要に応じてテーブルを再作成

    def create_tables(self):
        cur = self.conn.cursor()

        # Company: 会社情報を保存するテーブル
        # code: 会社のコード（主キー）
        # name: 会社名
        cur.execute('''CREATE TABLE IF NOT EXISTS Company (
                        code TEXT PRIMARY KEY,
                        name TEXT)''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_code_company ON Company (code)')

        # TimelyDisclosure: 適時開示情報を保存するテーブル
        # date: 開示日,
        # time: 開示時間,
        # code: 会社コード（Companyテーブルのcodeに対応）,
        # title: 開示情報のタイトル,
        # FOREIGN KEY(code): 外部キーとしてCompanyテーブルのcodeを参照
        cur.execute('''CREATE TABLE IF NOT EXISTS TimelyDisclosure (
                        date TEXT,
                        time TEXT,
                        code TEXT,
                        title TEXT,
                        url TEXT,
                        PRIMARY KEY (date, time, code, title),
                        FOREIGN KEY(code) REFERENCES Company(code))''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date_disclosure ON TimelyDisclosure (date, code)')

        # TimelyDisclosureTags: タグ情報を保存するテーブル
        # - date, time, code, title: TimelyDisclosureテーブルの各レコードに対応するキー
        # - tag: タグの内容
        # - FOREIGN KEY(date, time, code, title): TimelyDisclosureテーブルとの関連付け
        cur.execute('''CREATE TABLE IF NOT EXISTS TimelyDisclosureTags (
                date TEXT,
                time TEXT,
                code TEXT,
                title TEXT,
                tag TEXT,
                FOREIGN KEY (date, time, code, title) REFERENCES TimelyDisclosure(date, time, code, title)
            )''')

        # TimelyDisclosureTags テーブルに関するインデックスを作成（必要に応じて）
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_tags_fk ON TimelyDisclosureTags (date, time, code, title)''') # - TimelyDisclosureテーブルのキーに対するインデックス
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_tags_tag ON TimelyDisclosureTags (tag)''') # - タグ内容に対するインデックス

        # UpwardEvaluation: 各会社の評価情報を保存するテーブル
        # code: 会社コード（Companyテーブルのcodeに対応）
        # date: 評価日
        # evaluation: 評価値
        # FOREIGN KEY(code): 外部キーとしてCompanyテーブルのcodeを参照
        #cur.execute('DROP TABLE IF EXISTS UpwardEvaluation')
        cur.execute('''CREATE TABLE IF NOT EXISTS UpwardEvaluation (
                        code TEXT,
                        date TEXT,
                        evaluation INTEGER,
                        tags TEXT,
                        analyzed_performance BOOLEAN,
                        PRIMARY KEY (code, date),
                        FOREIGN KEY(code) REFERENCES Company(code))''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date_evaluation ON UpwardEvaluation (code,date)')
        self.conn.commit()

        # StockPerformance: 会社の業績情報を保存するテーブル
        # code: 会社コード
        # date: 日付
        # その他の財務情報カラム...
        #cur.execute('DROP TABLE IF EXISTS StockPerformance')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS StockPerformance (
                code TEXT,
                date TEXT,
                sales_current_period INTEGER,
                sales_current_period_yoy_growth_rate REAL,
                sales_previous_period INTEGER,
                sales_previous_period_yoy_growth_rate REAL,
                operating_profit_current_period INTEGER,
                operating_profit_current_period_yoy_growth_rate REAL,
                operating_profit_previous_period INTEGER,
                operating_profit_previous_period_yoy_growth_rate REAL,
                ordinary_profit_current_period INTEGER,
                ordinary_profit_current_period_yoy_growth_rate REAL,
                ordinary_profit_previous_period INTEGER,
                ordinary_profit_previous_period_yoy_growth_rate REAL,
                analysis_comments TEXT,
                PRIMARY KEY (code, date),
                FOREIGN KEY(code) REFERENCES Company(code)
            )''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date_performance ON StockPerformance (code,date)')
        self.conn.commit()
        return self.conn

    def insert_data(self, table, data):
        # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
        cur = self.conn.cursor()
        if table == DBManager.Table.TimelyDisclosure:
            cur.executemany('INSERT OR REPLACE INTO TimelyDisclosure (date, time, code, title, url) VALUES (?, ?, ?, ?, ?)', data)
        elif table == DBManager.Table.UpwardEvaluation:
            cur.executemany('INSERT OR IGNORE INTO UpwardEvaluation (code, date, evaluation, tags) VALUES (?, ?, ?, ?)', data)
        elif table == DBManager.Table.Company:
            cur.executemany('INSERT OR IGNORE INTO Company (code, name) VALUES (?, ?)', data)
        elif table == DBManager.Table.TimelyDisclosureTags:
            cur.executemany('INSERT OR IGNORE INTO TimelyDisclosureTags (date, time, code, title, tag) VALUES (?, ?, ?, ?, ?)', data)
        self.conn.commit()

    def update_tag_on_disclosure_table(self, data):
        # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
        cur = self.conn.cursor()
        cur.executemany("UPDATE TimelyDisclosure SET tag = ? WHERE date = ? AND time = ? AND code = ? AND title = ?", data)
        self.conn.commit()

    def fetch_timely_disclosure(self, condition_line = "", params = []):
        cur = self.conn.cursor()
        query = '''SELECT td.date, td.time, td.code, td.title, tg.tag FROM TimelyDisclosure td
                    LEFT JOIN TimelyDisclosureTags tg
                    ON td.date = tg.date AND td.time = tg.time AND td.code = tg.code AND td.title = tg.title'''
        if condition_line:
            query += ' WHERE ' + condition_line
        cur.execute(query, params)
        return cur.fetchall()

    def fetch_top_evaluations(self, top_evaluations_limit):
        cur = self.conn.cursor()
        query = f'''
        SELECT date, code, evaluation
        FROM (
            SELECT date, code, evaluation,
                ROW_NUMBER() OVER (PARTITION BY date ORDER BY evaluation DESC) AS rn
            FROM UpwardEvaluation
        ) WHERE rn <= {top_evaluations_limit}
        ORDER BY date, rn;
        '''
        cur.execute(query)
        return cur.fetchall()

    def fetch_top_disclosures(self, evaluation_threshold, tags):
        cur = self.conn.cursor()
        tags_placeholder = ','.join('?' for _ in tags)  # SQLクエリ用のプレースホルダー文字列を作成

        query = f'''
        SELECT ue.code, ue.date, td.url, tg.tag 
        FROM UpwardEvaluation ue
        JOIN TimelyDisclosure td ON ue.code = td.code AND ue.date = td.date
        JOIN TimelyDisclosureTags tg ON td.date = tg.date AND td.time = tg.time AND td.code = tg.code AND td.title = tg.title
        WHERE ue.evaluation >= ? AND tg.tag IN ({tags_placeholder})
        '''
        cur.execute(query, (evaluation_threshold, *tags))
        return cur.fetchall()

    def fetch_company_codes(self):
        """会社コードの一覧を取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT code, name FROM Company")  # 'Company' テーブルから会社コードを取得
        return cursor.fetchall()

    def copy_table(self, src_db_path, dst_db_path, table):
        """ あるデータベースから別のデータベースへテーブルをコピーする """
        # まず元のデータベースからデータを読み込む
        self.change_db(src_db_path)
        src_cursor = self.conn.cursor()
        table_name = table.name
        src_cursor.execute(f"SELECT * FROM {table_name}")
        data = src_cursor.fetchall()
        src_cursor.close()

        # 次に新しいデータベースにデータを挿入する
        self.change_db(dst_db_path)
        self.create_tables()  # 必要なテーブルを確実に作成する
        dst_cursor = self.conn.cursor()

        self.insert_data(table, data) # データ挿入

        self.conn.commit()
        dst_cursor.close()


    def close(self):
        self.conn.close()