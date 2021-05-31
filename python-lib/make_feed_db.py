#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhentv make feed list
# import section
import pathlib
import re
import sys
from time import time
import xml.etree.ElementTree as elementTree
from tinydb import TinyDB, Query, queries
current_dir = pathlib.Path(__file__).resolve().parent
import swirhentv_util as swiutil

SCRIPT_DIR = str(current_dir)
DB_FILENAME = f'{SCRIPT_DIR}/swirhentv_feed_db.json'
FEED_XML_DIR = f'{SCRIPT_DIR}/../../98 PSP用'
FEED_DB = TinyDB(DB_FILENAME)


# make feed list
def make_feed_list():
    FEED_DB.drop_table('xml_list')
    table_xml = FEED_DB.table('xml_list')
    xml_files = sorted(list(pathlib.Path(FEED_XML_DIR).glob('*.xml')))
    xml_names = []
    xml_titles = []
    xml_infos = []
    for xml_file in xml_files:
        with open(xml_file) as file:
            xml_root = elementTree.fromstring(file.read())
            xml_title = xml_root.find('./channel/title').text.strip()
        xml_names.append(xml_file.name.replace('.xml', ''))
        xml_titles.append(xml_title)
        xml_infos.append([xml_file.name.replace('.xml', ''), xml_title])
    table_xml.insert({'id': 'xml_names', 'data': xml_names})
    table_xml.insert({'id': 'xml_titles', 'data': xml_titles})
    table_xml.insert({'id': 'xml_infos', 'data': xml_infos})


def make_feed_data(feedname=''):
    table_xml = FEED_DB.table('xml_list')
    query = Query()
    table_feed = FEED_DB.table('feed_data')
    feed_names = table_xml.search(query.id == 'xml_names')[0]['data']
    for feed_name in feed_names:
        if feedname == '' or feedname == feed_name:
            xml_file = f'{FEED_XML_DIR}/{feed_name}.xml'
            title_list = []
            with open(xml_file) as file:
                xml_root = elementTree.fromstring(file.read())
            for item in xml_root.findall('./channel/item/title'):
                title_list.append(item.text.strip())
            if table_feed.search(query.id == feed_name):
                table_feed.update({'data': title_list}, query.id == feed_name)
            else:
                table_feed.insert({'id': feed_name, 'data': title_list})


# main section
if __name__ == '__main__':
    args = sys.argv
    arg = ''
    if len(args) > 1:
        arg = args[1]

    if arg == '':
        make_feed_list()
        make_feed_data()
    elif arg == 'xml':
        make_feed_list()
    else:
        make_feed_data(arg)

