#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nyaatorrent make feed db(movie-raw)
# import section
import sys
import pathlib
from datetime import datetime as dt
import urllib.request
import sqlite3
import xml.etree.ElementTree as elementTree
sys.path.append('/data/share/movie/sh/python-lib/')
import swirhentv_util as swiutil

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
URL_LIST_FILE = f'{SCRIPT_DIR}/urllist.txt'
FEED_DB = f'{SCRIPT_DIR}/nyaa_movie_feed.db'
FEED_URI = 'https://nyaa.si/?f=0&c=1_4&q=New-raws%7CKoi-Raws&page=rss'

# フィード取得(URLから)
def get_seed_list_proc():
    seed_list = []
    req = urllib.request.Request(FEED_URI)
    try:
        with urllib.request.urlopen(req) as response:
            xml_string = response.read()
    except Exception as e:
        print(e)
    else:
        xml_root = elementTree.fromstring(xml_string)

        for item in xml_root.findall('./channel/item'):
            seed_info = [item.find('title').text.translate(str.maketrans('"\'','__')), item.find('link').text, item.find('pubDate').text[:-6]]
            seed_list.append(seed_info)
        seed_list.reverse()

    return seed_list


def make_nyaa_data():
    # UURLから最新フィードを取得
    # title,link,pubDateを配列に入れる
    all_seed_list = get_seed_list_proc()

    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()
    # 参考SQL
    drop_table_sql = 'drop table if exists feed_data'
    create_table_sql = 'create table if not exists feed_data(' \
                        ' title string,' \
                        ' link string unique,' \
                        ' pubdate timestamp,' \
                        ' download_flag boolean,' \
                        ' created_at timestamp default (datetime(\'now\', \'localtime\')))'

    values = []
    for seed_item in all_seed_list:
        item_title = seed_item[0]
        item_link = seed_item[1]
        item_pubdate =  dt.strptime(seed_item[2], '%a, %d %b %Y %H:%M:%S')
        values.append(f'("{item_title}", "{item_link}", "{item_pubdate}")')

    values_str = ', '.join(values)
    insert_sql = 'insert into feed_data(title, link, pubdate)' \
                f' values{values_str}' \
                ' on conflict(link) do nothing'
    try:
        cur.execute(insert_sql)
    except Exception as e:
        swiutil.multi_post('torrent-search', f'@channel sql insert error: {e}')
    else:
        conn.commit()
    conn.close()


# main section
if __name__ == '__main__':
    make_nyaa_data()
