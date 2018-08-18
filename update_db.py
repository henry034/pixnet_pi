import json
import mysql.connector
import os
import requests
import shutil

store_id = int(os.environ.get('STORE_ID'))
if store_id is None:
    raise ValueError('Must provide websocket')

def connect_db():
    conn = mysql.connector.connect(
            user='joe83830',
            password='123123',
            host='140.113.144.78',
            database='DJH')
    cur = conn.cursor()
    return conn, cur


def clear_hot_file_local():
    a=1
def download_mp3(path, rank, week_tag = False):
    base = os.path.basename(path)
    path = path[2:]
    url='http://140.113.144.78:5000/getfile/{}'.format(path)
    print(url)
    response =requests.get(url,stream=True)
    
    if week_tag is False:
        fname_sv = './audio/hot_web/{}_{}'.format(rank,base)
        with open(fname_sv, 'wb')as fd:
            shutil.copyfileobj(response.raw, fd)


def get_hot_file_path_db(cur):
    sql_cmd = ('SELECT * FROM store_list '
               'WHERE storeID={}').format(store_id)
    cur.execute(sql_cmd)
    for id, name in cur:
        store_name = name
    
    sql_cmd = ('SELECT path, rank FROM {} ORDER BY rank').format(store_name)
    cur.execute(sql_cmd)

    
    for path, rank in cur:
        if rank > 0:
            download_mp3(path, rank, week_tag = False)
            print(path, rank)
def main():
    conn, cur = connect_db()
    get_hot_file_path_db(cur)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
