#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhentv make feed list
# import section
import pathlib
import sys
import sqlite3
import swirhentv_util as swiutil
current_dir = pathlib.Path(__file__).resolve().parent


# argment section
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
                        ' path string)'
    cur.execute(drop_table_sql)
    cur.execute(create_table_sql)
    values = []
    for xml_info in xml_infos:
        values.append(f'("{xml_info[0]}", "{xml_info[1]}", "{xml_info[2]}")')
    values_str = ', '.join(values)
    insert_sql = f'insert into feed values{values}'
    cur.execute(insert_sql)
    conn.commit()
    conn.close()


# def make_feed_data(feedname=''):
#     table_xml = FEED_DB.table('xml_list')
#     table_feed = FEED_DB.table('feed_data')
#     query = Query()
#     feed_names = table_xml.search(query.id == 'xml_names')[0]['data']
#     for feed_name in feed_names:
#         if feedname == '' or feedname == feed_name:
#             xml_file = f'{FEED_XML_DIR}/{feed_name}.xml'
#             title_list = []
#             with open(xml_file) as file:
#                 xml_root = elementTree.fromstring(file.read())
#             for item in xml_root.findall('./channel/item/title'):
#                 title_list.append(item.text.strip())
#             if table_feed.search(query.id == feed_name):
#                 table_feed.update({'data': title_list}, query.id == feed_name)
#             else:
#                 table_feed.insert({'id': feed_name, 'data': title_list})


# main section
if __name__ == '__main__':
    args = sys.argv
    arg = ''
    if len(args) > 1:
        arg = args[1]

    if arg == '':
        make_feed_list_data()
        # make_feed_data()
    elif arg == 'xml':
        make_feed_list_data()
    # else:
    #     make_feed_data(arg)

