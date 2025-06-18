#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re,pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil
import sqlite3

FEED_DB = f'/home/swirhen/sh/checker/torrentsearch/nyaatorrent_feed.db'

# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        category = args[1]
    else:
        category = 'av'
    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()
    select_sql = 'select title, link' \
                 ' from feed_data ' \
                 f' where category = "{category}"'
    delete_record_sql = 'delete from feed_data where link'
    search_result = list(cur.execute(select_sql))
    conn.close()

    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()

    for search_item in search_result:
        item_title = search_item[0]
        item_link = search_item[1]
        if swiutil.is_zh(item_title):
            #print(item_title)
            print(''.join(set(item_title) - set(item_title.encode('sjis','ignore').decode('sjis'))))
            delete_sql = f'{delete_record_sql} = "{item_link}"'
            # cur.execute(delete_sql)

    conn.commit()
    conn.close()


