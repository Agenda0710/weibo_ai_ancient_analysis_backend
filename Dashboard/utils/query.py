from pymysql import *

conn = connect(host='localhost', port=3306, user='root', passwd='xusong986514', database='weibo')
cursor = conn.cursor()

def query(sql, params):
    params = tuple(params)
    cursor.execute(sql, params)
    conn.ping(reconnect=True)
    data_list = cursor.fetchall()
    conn.commit()
    return data_list
