#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv auto publish batch
# import section
import os, pathlib, re, sys, shutil
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime as dt
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swutil

# argments section
SCRIPT_DIR = str(current_dir)
DOWNLOAD_DIR = SCRIPT_DIR + '/data/share/movie'
LIST_FILE = SCRIPT_DIR + '/checklist.txt'
LIST_FILE2 = SCRIPT_DIR + '/sub_checklist.txt'
LIST_TEMP = SCRIPT_DIR + '/checklist.temp'
RSS_TEMP = SCRIPT_DIR + '/rss.temp'
RSS_XML = SCRIPT_DIR + '/rss.xml'
RSS_TEMP2 = SCRIPT_DIR + '/rss2.temp'
RSS_XML2 = SCRIPT_DIR + '/rss2.xml'
RESULT_FILE = SCRIPT_DIR + '/autodl.result'
TDATETIME = dt.now()
DATETIME = TDATETIME.strftime('%Y/%m/%d-%H:%M:%S')
DATETIME2 = TDATETIME.strftime('%Y%m%d%H%M%S')
SEED_URI = 'https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss'
SYOBOCAL_URI = 'http://cal.syoboi.jp/find?sd=0&kw='
# PYTHON_PATH = 'python3'
CHANNEL = 'bot-open'
POST_FLG = 1
LOG_FILE = SCRIPT_DIR + '/autopub_' + DATETIME2 + '.log'
LOG_DIR = SCRIPT_DIR + '/logs'
FLG_FILE = SCRIPT_DIR + '/autopub_running'
LEOPARD_INDEX = SCRIPT_DIR + '/leopard_index.html'
INDEX_GET = 0
NEW_RESULT_FILE = SCRIPT_DIR + '/new_program_result.txt'
NEW_RESULT_FILE_NG = SCRIPT_DIR + '/new_program_result_ng.txt'
NEW_PROGRAM_FILE = SCRIPT_DIR + '/new_program.txt'


# 新番組日本語名取得
def get_jp_title(title_en):
    # 取得した英語タイトルの "-" をスペースに変換、"："、"."、"!" を削除、3ワード分を取得
    search_word = re.sub(r'([^ ]*) ([^ ]*) ([^ ]*) .*', r'\1 \2 \3', title_en.translate(str.maketrans('-', ' ', '!：:.,'))).replace(' ', '+')
    # 2ワード分のもの
    search_word2 = re.sub(r'(.*)\+.*', r'\1', search_word)

    result1 = syobocal_search(search_word)
    if result1 != '':
        return result1
    else:
        return syobocal_search(search_word2)


# しょぼいカレンダー検索
def syobocal_search(search_word):
    html = urllib.request.urlopen(SYOBOCAL_URI + search_word)
    soup = BeautifulSoup(html, "html.parser")

    result = []
    for a in soup.find_all('a'):
        if re.search(r'tid', str(a)):
            result += a

    if len(result) > 0:
        return result[0].translate(str.maketrans({';': '；', '!': '！', ':': '：', '/': '／'}))
    else:
        return ''


# ログ書き込み
def logging(logstr):
    td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
    print(td + ' ' + logstr)
    with open(LOG_FILE, 'a') as logfile:
        logfile.write(td + ' ' + logstr + '\n')


# 終了のあとしまつ
def end(exit_code):
    shutil.move(LOG_FILE, LOG_DIR)
    os.remove(FLG_FILE)
    exit(exit_code)


# main section
# running flag file check
if os.path.isfile(FLG_FILE):
    logging('### running flag file exist. delete flag file? (y/n)')
    if swutil.askconfirm() == 0:
        os.remove(FLG_FILE)
    shutil.move(LOG_FILE, LOG_DIR)
    exit(1)
else:
    flg_file = pathlib.Path(FLG_FILE)
    flg_file.touch()
    print('OK')
