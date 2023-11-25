import sqlite3
from enum import Enum, auto

class DBManager:
    
    class Table(Enum):
        TIMELY_DISCLOSURE = auto()
        UPWARD_EVALUATION = auto()
        COMPANY = auto()
        TIMELY_DISCLOSURE_TAGS = auto()    

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        self.conn = sqlite3.connect('output/timely_disclosure.db')
        self.create_tables()

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
        if table == DBManager.Table.TIMELY_DISCLOSURE:
            cur.executemany('INSERT OR REPLACE INTO TimelyDisclosure (date, time, code, title, url) VALUES (?, ?, ?, ?, ?)', data)
        elif table == DBManager.Table.UPWARD_EVALUATION:
            cur.executemany('INSERT OR IGNORE INTO UpwardEvaluation (code, date, evaluation, tags) VALUES (?, ?, ?, ?)', data)
        elif table == DBManager.Table.COMPANY:
            cur.executemany('INSERT OR IGNORE INTO Company (code, name) VALUES (?, ?)', data)
        elif table == DBManager.Table.TIMELY_DISCLOSURE_TAGS:
            cur.executemany('INSERT OR IGNORE INTO TimelyDisclosureTags (date, time, code, title, tag) VALUES (?, ?, ?, ?, ?)', data)
        self.conn.commit()

    def update_tag_on_disclosure_table(self, data):
        # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
        cur = self.conn.cursor()
        cur.executemany("UPDATE TimelyDisclosure SET tag = ? WHERE date = ? AND time = ? AND code = ? AND title = ?", data)
        self.conn.commit()

    #def fetch_timely_disclosure(self, condition_line = "", params = []):
    #    cur = self.conn.cursor()
    #    query = 'SELECT date, time, code, title, tag FROM TimelyDisclosure'
    #    if condition_line:
    #        query += ' WHERE ' + condition_line
    #    cur.execute(query, params)
    #    return cur.fetchall()

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

    #def fetch_top_disclosures(self, evaluation_threshold, tags):
    #    cur = self.conn.cursor()
    #    tags_placeholder = ','.join('?' for _ in tags)  # Create a placeholder string for the SQL query
    #    query = f'''
    #    SELECT ue.code, ue.date, td.url, td.tag 
    #    FROM UpwardEvaluation ue
    #    JOIN TimelyDisclosure td ON ue.code = td.code AND ue.date = td.date
    #    WHERE ue.evaluation >= ? AND td.tag IN ({tags_placeholder})
    #    '''
    #    cur.execute(query, (evaluation_threshold, *tags))
    #    return cur.fetchall()
        
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

    def close(self):
        self.conn.close()