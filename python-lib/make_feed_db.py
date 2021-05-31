#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhentv make feed list
# import section
import pathlib
import re
import sys
import xml.etree.ElementTree as elementTree
from tinydb import TinyDB, Query
import tinydb
current_dir = pathlib.Path(__file__).resolve().parent
import swirhentv_util as swiutil

SCRIPT_DIR = str(current_dir)
DB_FILENAME = f'{SCRIPT_DIR}/swirhentv_feed_db.json'
FEED_XML_DIR = f'{SCRIPT_DIR}/../../98 PSP用'
FEED_DB = tinydb(DB_FILENAME)


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
    table_xml.insert({'xml_names': xml_names})
    table_xml.insert({'xml_titles': xml_titles})
    table_xml.insert({'xml_infos': xml_infos})


# main section
if __name__ == '__main__':
    args = sys.argv
    index = ''
    if len(args) > 1:
        index = args[1]

    if index == '':
        make_feed_list()
