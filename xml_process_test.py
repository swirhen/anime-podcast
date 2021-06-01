#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xml処理のスピードをテストする
# import section
import os
import sys
import pathlib
import time
import urllib.request
import xml.etree.ElementTree as elementTree
import subprocess
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil

# arguments section
SCRIPT_DIR = str(current_dir)
SEED_URI = 'https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss'
TEMP_XML = f'{SCRIPT_DIR}/temp.xml'


# ElementTree
def et(xml_string):
    seed_list = []
    print('# ElementTree: process start')
    stime = time.time()
    xml_root = elementTree.fromstring(xml_string)

    for item in xml_root.findall('./channel/item'):
        seed_list.append([item.find('title').text, item.find('link').text])
    
    etime = time.time()
    elapsed = etime - stime
    print(f'# list count: {len(seed_list)}')
    print(f'# ElementTree: process end. process time: {elapsed}')
    return seed_list


# xmllint
def lint():
    seed_list = []
    print('# xmllint: process start')
    stime = time.time()
    feeds = subprocess.run(f'echo "cat /rss/channel/item" | xmllint --shell "{TEMP_XML}" | rg "<title>" -A 1 | sed "s/.*>\(.*\)<.*/\\1/" | rg -v "^-" | sed -z "s/\\nhttp/|http/g"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip().splitlines()
    for feed in feeds:
        seed_info = feed.split('|')
        seed_list.append([seed_info[0], seed_info[1]])

    etime = time.time()
    elapsed = etime - stime
    print(f'# list count: {len(seed_list)}')
    print(f'# xmllint: process end. process time: {elapsed}')
    return seed_list


# ripgrep
def rg():
    seed_list = []
    print('# ripgrep: process start')
    stime = time.time()
    feeds = subprocess.run(f'rg "\t\t\t<title>" -A 1 "{TEMP_XML}" | sed "s/.*>\(.*\)<.*/\\1/" | rg -v "^-" | sed -z "s/\\nhttp/|http/g"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip().splitlines()
    for feed in feeds:
        seed_info = feed.split('|')
        seed_list.append([seed_info[0], seed_info[1]])

    etime = time.time()
    elapsed = etime - stime
    print(f'# list count: {len(seed_list)}')
    print(f'# ripgrep: process end. process time: {elapsed}')
    return seed_list


# main
def main(arg='all'):
    # 準備：ファイルとテキストを取得
    # req = urllib.request.Request(SEED_URI)
    # with urllib.request.urlopen(req) as response:
    #     xml_string = response.read()
    if os.path.exists(TEMP_XML):
        os.remove(TEMP_XML)
    urllib.request.urlretrieve(SEED_URI, TEMP_XML)
    with open(TEMP_XML) as file:
        xml_string = file.read()

    # ElementTree
    if arg == 'all' or arg == 'et':
        et(xml_string)
    elif arg == 'all' or arg == 'lint':
        lint()
    elif arg == 'all' or arg == 'rg':
        rg()
