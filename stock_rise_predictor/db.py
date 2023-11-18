import sqlite3

def create_database():
    conn = sqlite3.connect('output/timely_disclosure.db')
    cur = conn.cursor()

    # Company テーブルの作成
    cur.execute('''CREATE TABLE IF NOT EXISTS Company
                    (code TEXT PRIMARY KEY, name TEXT)''')

    # TimelyDisclosure テーブルの作成
    cur.execute('''CREATE TABLE IF NOT EXISTS TimelyDisclosure
                    (date TEXT, time TEXT, code TEXT, title TEXT,
                    FOREIGN KEY(code) REFERENCES Company(code))''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_code_date ON TimelyDisclosure (code, date)')

    # UpwardEvaluation テーブルの作成
    cur.execute('''CREATE TABLE IF NOT EXISTS UpwardEvaluation
                    (code TEXT, searched_date TEXT, evaluation INTEGER,
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
                cur.execute('INSERT INTO TimelyDisclosure (date, time, code, title) VALUES (?, ?, ?, ?)', record) # 重複がない場合のみ挿入
        #cur.executemany('INSERT INTO TimelyDisclosure (date, time, code, title) VALUES (?, ?, ?, ?)', data)
    elif table == 'UpwardEvaluation':
        cur.executemany('INSERT INTO UpwardEvaluation (code, start_date, end_date, evaluation) VALUES (?, ?, ?, ?)', data)
    elif table == 'Company':
        cur.executemany('INSERT OR IGNORE INTO Company (code, name) VALUES (?, ?)', data)
    conn.commit()
    
def fetch_timely_disclosure(conn, search_date):
    cur = conn.cursor()
    query = 'SELECT date, time, code, title FROM TimelyDisclosure'
    conditions = []
    params = []
    #if start_date:
    #    conditions.append('date >= ?')
    #    params.append(start_date)
    #if end_date:
    #    conditions.append('date <= ?')
    #    params.append(end_date)
    if search_date:
        conditions.append('date = ?')
        params.append(format_datetime_str(search_date))
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    cur.execute(query, params)
    return cur.fetchall()