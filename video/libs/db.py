import os
from sqlite3 import Connection, connect, IntegrityError

DB_TABLE_MAP = {
    "translate":"translate_log" # 翻译记录
}



"""连接数据库"""
def connect_db(db_path:str =None)->Connection:
    # 创建数据库连接
    if not db_path:
        db_path = os.getenv('db_path', 'superme.db')
    if not os.path.exists(db_path):
        open(db_path, 'w').close()
    conn = connect(db_path)
    return conn


"""创建翻译表"""
def check_translate_table()->bool:
    conn:Connection = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT UNIQUE, dest TEXT, language TEXT)" % DB_TABLE_MAP['translate']
    cursor = conn.execute(sql)
    cursor.close()
    conn.commit()

"""插入或是更新"""
def installAndUpdateTranslate(source:str, dest:str, language:str)->bool:
    check_translate_table()
    conn:Connection = connect_db()
    print("插入数据: %s -> %s  %s" % (source, dest, language))
    try:
        conn.cursor().execute("INSERT INTO %s (source, dest, language) VALUES (?, ?, ?)" % DB_TABLE_MAP['translate'], (source, dest, language))
    except IntegrityError as e:
        print("插入错误,更新: %s -> %s  %s" % (source, dest, language))
        conn.cursor().execute("UPDATE %s SET dest = '%s', language = '%s' WHERE source = '%s'" % (DB_TABLE_MAP['translate'], dest, language, source))
    finally:
        conn.commit()
        conn.close()
    return True

"""查询数据库"""
def read_translate(source:str)->str:
    check_translate_table()
    conn:Connection = connect_db() 
    sql =  "SELECT source, dest, language FROM  %s WHERE source = '%s'" % (DB_TABLE_MAP['translate'], source)
    cursor = conn.cursor().execute(sql) 
    rows = cursor.fetchall()
    for row in rows:
        print(row)

installAndUpdateTranslate("hello", "你好222", "zh")
read_translate("hello")