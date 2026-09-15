#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# torrentsearch DBを利用するbot向け処理
# import section
import os
import sqlite3
import urllib.request
from datetime import datetime as dt, timedelta

# argument section
FEED_DB = '/home/swirhen/sh/checker/torrentsearch/nyaatorrent_feed.db'
DOWNLOAD_DIR_ROOT = '/data/share/temp/torrentsearch'


# ダウンロードファイル名の安全化
# パス区切り・引用符等を除去して長さを制限
def sanitize_filename(title):
    title = title.translate(str.maketrans('/;!"\'', '_____'))
    while len(title.encode('utf-8')) > 247:
        title = title[:-1]
    return title


# nyaa データベース検索(n日以内のリスト)
def search_seed_resent(category, offset_days):
    fromdate = (dt.now() - timedelta(days=int(offset_days))).strftime('%Y-%m-%d')
    with sqlite3.connect(FEED_DB) as conn:
        cur = conn.cursor()
        select_sql = 'select title, link, pubdate' \
                     ' from feed_data f' \
                    f' where category = "{category}"' \
                    f' and pubdate > "{fromdate}"'
        return list(cur.execute(select_sql))


# nyaa データベース検索・ダウンロード
def search_seed(download_flg, category, keyword, last_check_date='', ignore_word_list=[]):
    date_str = dt.now().strftime('%Y%m%d')
    download_dir = f'{DOWNLOAD_DIR_ROOT}/{date_str}'

    with sqlite3.connect(FEED_DB) as conn:
        cur = conn.cursor()
        select_sql = 'select category, title, link, download_dir' \
                     ' from feed_data'
        if category != 'all':
            select_sql += f' where category = "{category}"' \
                          f' and title like "%{keyword}%"'
        else:
            select_sql += f' where title like "%{keyword}%"'
        if last_check_date != '':
            select_sql += f' and created_at > "{last_check_date}"'
        if download_flg:
            select_sql += ' and download_dir is Null'
        search_result = list(cur.execute(select_sql))

    hit_result = []
    link_values = []
    for search_item in search_result:
        item_category, item_title, item_link, item_download_dir = search_item
        if any(word in item_title for word in ignore_word_list):
            continue
        if download_flg:
            hit_result.append([item_category, item_title, keyword, item_link])
            os.makedirs(download_dir, exist_ok=True)
            filename = sanitize_filename(item_title)
            try:
                data = urllib.request.urlopen(item_link).read()
            except Exception as e:
                print(e)
            else:
                with open(f'{download_dir}/{filename}.torrent', mode='wb') as file:
                    file.write(data)
                link_values.append(item_link)
        else:
            hit_result.append([item_category, item_title, keyword, item_link, item_download_dir])

    if download_flg and link_values:
        with sqlite3.connect(FEED_DB) as conn:
            cur = conn.cursor()
            str_link_value = '", "'.join(link_values)
            update_sql = f'update feed_data set download_dir = "{download_dir}" where link in ("{str_link_value}")'
            cur.execute(update_sql)

    return hit_result


# nyaa データベース検索(外部利用版)
def search_seed_ext(category, keyword):
    with sqlite3.connect(FEED_DB) as conn:
        cur = conn.cursor()
        select_sql = 'select category, title, link, download_dir' \
                     ' from feed_data'
        if category != 'all':
            select_sql += f' where category = "{category}"' \
                          f' and title like "%{keyword}%"'
        else:
            select_sql += f' where title like "%{keyword}%"'
        return list(cur.execute(select_sql))
