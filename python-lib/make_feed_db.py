#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhentv make feed list
# import section
import pathlib
import subprocess
import sys
import sqlite3
import swirhentv_util as swiutil

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
FEED_XML_DIR = f'{SCRIPT_DIR}/../../98 PSP用'
FEED_DB = f'{SCRIPT_DIR}/swirhentv_feed.db'

# フィードのタイトルとファイル名のリストを作成する
def make_feed_list_data():
    xml_infos = swiutil.get_feed_xml_list()
    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()
    drop_table_sql = 'drop table if exists feed'
    create_table_sql = 'create table if not exists feed(' \
                        ' name string primary key,' \
                        ' title string,' \
                        ' path string,' \
                        ' created_on string)'
    cur.execute(drop_table_sql)
    cur.execute(create_table_sql)
    values = []
    for xml_info in xml_infos:
        values.append(f'("{xml_info[0]}", "{xml_info[1]}", "{xml_info[2]}", CURRENT_TIMESTAMP)')
    values_str = ', '.join(values)
    insert_sql = f'insert into feed values{values_str}'
    cur.execute(insert_sql)
    conn.commit()
    conn.close()


# フィード内のタイトルリストを作成する(引数あった場合は特定のフィードのみ)
def make_feed_data(argument=''):
    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()
    drop_table_sql = 'drop table if exists feed_data'
    create_table_sql = 'create table if not exists feed_data(' \
                        ' name string,' \
                        ' title string,' \
                        ' created_on string)'
    delete_record_sql = 'delete from feed_data where name'
    if argument != '':
        xml_file = f'"{FEED_XML_DIR}/{argument}.xml"'
        cur.execute(f'{delete_record_sql} = "{argument}"')
    else:
        xml_file = f'"{FEED_XML_DIR}/"*.xml'
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)

    feeds = subprocess.run(f'rg -H "      <title>" {xml_file} | sed "s/^\/.*\/\(.*\)\.xml.*>\(.*\)<.*/\\1|\\2/"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip().splitlines()
    values = []
    for feed in feeds:
        feed_info = feed.split('|')
        values.append(f'("{feed_info[0]}", "{feed_info[1]}", CURRENT_TIMESTAMP)')
    values_str = ', '.join(values)
    insert_sql = f'insert into feed_data values{values_str}'
    cur.execute(insert_sql)
    conn.commit()
    conn.close()


# main section
if __name__ == '__main__':
    args = sys.argv
    arg = ''
    if len(args) > 1:
        arg = args[1]

    if arg == '':
        make_feed_list_data()
        make_feed_data()
    elif arg == 'xml':
        make_feed_list_data()
    else:
        make_feed_data(arg)

