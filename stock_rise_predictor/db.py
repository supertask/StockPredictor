import sqlite3

def format_datetime_str(datetime_now):
    return datetime_now.strftime('%Y-%m-%d')

def create_database():
    conn = sqlite3.connect('output/timely_disclosure.db')
    cur = conn.cursor()

    # Company: 会社情報を保存するテーブル
    # code: 会社のコード（主キー）
    # name: 会社名
    cur.execute('''CREATE TABLE IF NOT EXISTS Company
                    (code TEXT PRIMARY KEY, name TEXT)''')

    # TimelyDisclosure: 適時開示情報を保存するテーブル
    # date: 開示日,
    # time: 開示時間,
    # code: 会社コード（Companyテーブルのcodeに対応）,
    # title: 開示情報のタイトル,
    # FOREIGN KEY(code): 外部キーとしてCompanyテーブルのcodeを参照
    cur.execute('''CREATE TABLE IF NOT EXISTS TimelyDisclosure
                    (date TEXT, time TEXT, code TEXT, title TEXT, url TEXT,
                    FOREIGN KEY(code) REFERENCES Company(code))''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date ON TimelyDisclosure (code, date)')

    # UpwardEvaluation: 各会社の評価情報を保存するテーブル
    # code: 会社コード（Companyテーブルのcodeに対応）
    # date: 評価日
    # evaluation: 評価値
    # FOREIGN KEY(code): 外部キーとしてCompanyテーブルのcodeを参照
    cur.execute('DROP TABLE IF EXISTS UpwardEvaluation')
    cur.execute('''CREATE TABLE IF NOT EXISTS UpwardEvaluation
                    (code TEXT, date TEXT, evaluation INTEGER, tags TEXT,
                    FOREIGN KEY(code) REFERENCES Company(code))''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_code ON UpwardEvaluation (code)')
    conn.commit()
    return conn

def insert_data(conn, table, data):
    # TimelyDisclosure = 適時開示テーブル, UpwardEvaluation = 上昇評価値, Company = 会社情報
    cur = conn.cursor()
    if table == 'TimelyDisclosure':
        for record in data:
            # 各レコードに対して、重複チェックを行います
            cur.execute('SELECT * FROM TimelyDisclosure WHERE date=? AND time=? AND code=? AND title=?', record[:4])
            if not cur.fetchone():
                cur.execute('INSERT INTO TimelyDisclosure (date, time, code, title, url) VALUES (?, ?, ?, ?, ?)', record) # 重複がない場合のみ挿入
        #cur.executemany('INSERT INTO TimelyDisclosure (date, time, code, title) VALUES (?, ?, ?, ?)', data)
    elif table == 'UpwardEvaluation':
        cur.executemany('INSERT INTO UpwardEvaluation (code, date, evaluation, tags) VALUES (?, ?, ?, ?)', data)
    elif table == 'Company':
        cur.executemany('INSERT OR IGNORE INTO Company (code, name) VALUES (?, ?)', data)
    conn.commit()
    
def fetch_timely_disclosure(conn, search_date):
    cur = conn.cursor()
    query = 'SELECT date, time, code, title FROM TimelyDisclosure'
    conditions = []
    params = []
    if search_date:
        conditions.append('date = ?')
        params.append(format_datetime_str(search_date))
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
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
