import sqlite3


def create_database():
    conn = sqlite3.connect('output/timely_disclosure.db')
    cur = conn.cursor()

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
                    tag TEXT,
                    PRIMARY KEY (date, time, code, title),
                    FOREIGN KEY(code) REFERENCES Company(code))''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date_disclosure ON TimelyDisclosure (date, code)')

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
    conn.commit()

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
    conn.commit()
    return conn

def insert_data(conn, table, data):
    # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
    cur = conn.cursor()
    if table == 'TimelyDisclosure':
        #for record in data:
        #    # 各レコードに対して、重複チェックを行います
        #    cur.execute('SELECT * FROM TimelyDisclosure WHERE date=? AND time=? AND code=? AND title=?', record[:4])
        #    if not cur.fetchone():
        #        cur.execute('INSERT INTO TimelyDisclosure (date, time, code, title, url) VALUES (?, ?, ?, ?, ?)', record) # 重複がない場合のみ挿入
        cur.executemany('INSERT OR REPLACE INTO TimelyDisclosure (date, time, code, title, url) VALUES (?, ?, ?, ?, ?)', data)
    elif table == 'UpwardEvaluation':
        #cur.executemany('INSERT INTO UpwardEvaluation (code, date, evaluation, tags) VALUES (?, ?, ?, ?)', data)
        cur.executemany('INSERT OR REPLACE INTO UpwardEvaluation (code, date, evaluation, tags) VALUES (?, ?, ?, ?)', data)
    elif table == 'Company':
        cur.executemany('INSERT OR IGNORE INTO Company (code, name) VALUES (?, ?)', data)
    conn.commit()

def update_tag_on_disclosure_table(conn, data):
    # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
    cur = conn.cursor()
    cur.executemany("UPDATE TimelyDisclosure SET tag = ? WHERE date = ? AND time = ? AND code = ? AND title = ?", data)
    conn.commit()

def fetch_timely_disclosure(conn, condition_line = "", params = []):
    cur = conn.cursor()
    query = 'SELECT date, time, code, title, tag FROM TimelyDisclosure'
    if condition_line:
        query += ' WHERE ' + condition_line
    cur.execute(query, params)
    return cur.fetchall()


def fetch_top_evaluations(conn, top_evaluations_limit):
    cur = conn.cursor()
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
