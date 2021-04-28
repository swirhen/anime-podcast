#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv auto publish batch
# import section
import os, pathlib, re, sys, shutil, glob, git
import urllib.request

import math
from bs4 import BeautifulSoup
from datetime import datetime as dt
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swutil
import xml.etree.ElementTree as ET

# argments section
SCRIPT_DIR = str(current_dir)
DOWNLOAD_DIR = '/data/share/movie'
LIST_FILE = SCRIPT_DIR + '/checklist.txt'
LIST_TEMP = SCRIPT_DIR + '/checklist.temp'
RSS_TEMP = SCRIPT_DIR + '/rss.temp'
RSS_XML = SCRIPT_DIR + '/rss.xml'
RESULT_FILE = SCRIPT_DIR + '/autodl.result'
TDATETIME = dt.now()
DATETIME = TDATETIME.strftime('%Y/%m/%d-%H:%M:%S')
DATETIME2 = TDATETIME.strftime('%Y%m%d%H%M%S')
SEED_URI = 'https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss'
SYOBOCAL_URI = 'http://cal.syoboi.jp/find?sd=0&kw='
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
def logging(log_str):
    td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
    print(td + ' ' + log_str)
    swutil.writefile_append(LOG_FILE, td + ' ' + log_str)


def slackpost(post_str):
    swutil.slack_post(CHANNEL, post_str)


def slackupload(file_path):
    swutil.slack_upload(CHANNEL, file_path)


# 終了のあとしまつ
def end(exit_code):
    shutil.move(LOG_FILE, LOG_DIR)
    os.remove(FLG_FILE)
    exit(exit_code)


# main section
# running flag file check
if os.path.isfile(FLG_FILE):
    logging('### running flag file exist.')
    print('delete flag file? (y/n)')
    if swutil.askconfirm() == 0:
        os.remove(FLG_FILE)
        logging('### running flag file deleted manually.')
    shutil.move(LOG_FILE, LOG_DIR)
    exit(1)
else:
    flg_file = pathlib.Path(FLG_FILE)
    flg_file.touch()

logging('### auto publish start.')
slackpost('swirhen.tv auto publish start...')

# seed download
req = urllib.request.Request(SEED_URI)
with urllib.request.urlopen(req) as response:
    XmlData = response.read()

# 取得したxmlからリストを作成
seed_list = []
req = urllib.request.Request(SEED_URI)
with urllib.request.urlopen(req) as response:
    xml_string = response.read()

xml_root = ET.fromstring(xml_string)

for item in xml_root.findall('./channel/item'):
    seed_info = [item.find('title').text, item.find('link').text]
    seed_list.append(seed_info)

# チェックリストの取得
# file open
listfile = ''
check_lists = []
try:
    listfile = open(LIST_FILE, 'r', encoding='utf-8')
except Exception:
    logging("open error. not found file: " + str(LIST_FILE))
    end(1)

# make rename list
for line in listfile.readlines():
    if re.search('^Last Update', line):
        continue
    last_update = re.sub(r'^([^ ]+) ([^ ]+) (.*)', r'\1', line).strip()
    episode_number = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\2', line).strip()
    name = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).strip().split("|")[0]
    name_j = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).strip().split("|")[1]
    # last_updates.append(last_update)
    # episode_numbers.append(episode_number)
    # names.append(name)
    # names_j.append(name_j)
    check_list = [last_update, episode_number, name, name_j]
    check_lists.append(check_list)

# リストチェック＆seedダウンロード処理開始：tempリストに日時を出力
swutil.writefile_new(LIST_TEMP, 'Last Update: ' + DATETIME)

# 結果リスト
result = []
downloads = []
end_episodes = []
end_episodes_ngs = []

# チェックリストの行ごとにループ
for check_list in check_lists:
    last_update = check_list[0]
    episode_number = check_list[1]
    name = check_list[2]
    name_j = check_list[3]
    hit_flag = 0
    diff_over_flag = 0

    title = ''
    seed_episode_number = ''
    # シードリストループ
    for seed_info in seed_list:
        title = seed_info[0]
        link = seed_info[1]
        # titleと一致するかどうかチェック
        if re.search(name, title):
            # 一致した場合、titleから話数の数値を取得
            seed_episode_number = re.sub(r'^.*' + name + r'.* ([0-9.]{2,5}) .*', r'\1', title)
            # 新話数 - 旧話数の差分が1のとき、新規エピソードとする
            # 話数には.5などが存在するため、整数で丸めてから計算する(旧話数は切り捨て、新話数は切り上げ)
            episode_number_diff = math.ceil(float(seed_episode_number)) - math.floor(float(episode_number))
            if episode_number_diff == 1:
                hit_flag = 1
            elif episode_number_diff > 1:
                # 差分が2以上のときは差分をフラグに入れる
                hit_flag = episode_number_diff
                diff_over_flag = 1

            if hit_flag > 0:
                logging('new episode: ' + seed_episode_number + ' local: ' + episode_number)
                if hit_flag > 1:
                    logging(title + '    ↑前回との差分が1話以上検出されています。差分話数: ' + hit_flag)
                    result.append(title + '\n↑前回との差分が1話以上検出されています。差分話数: ' + hit_flag)
                else:
                    result.append(title)
                downloads.append(link)

                # titleに「END」が含まれるときは終了作品チェックを行う
                if re.search('END', title):
                    filepath = glob.glob(DOWNLOAD_DIR + '/*' + name_j)[0]
                    filelist = list(pathlib.Path(filepath).glob(name_j + ' 第*.mp4'))
                    filelist_ignore_inteval_episodes = sorted([p.name for p in filelist if not re.search(r'\.5', str(p))])
                    filecount = len(filelist_ignore_inteval_episodes) + 1

                    logging('終了とみられるエピソード: ' + title)
                    if filecount == int(seed_episode_number):
                        logging('    抜けチェック:OK 既存エピソードファイル数(.5話を除く): ' + str(filecount) + ' / 最終エピソード番号: ' + seed_episode_number)
                        end_episodes.append(name_j)
                    else:
                        logging('    抜けチェック:NG 既存エピソードファイル数(.5話を除く): ' + str(filecount) + ' / 最終エピソード番号: ' + seed_episode_number)
                        end_episodes_ngs.append(name_j)

                break

    # 新規エピソードがある場合、最新話数と最終取得日時を更新して、tempリストへ追加
    # 無い場合は元のリストの行をそのまま追加
    with open(LIST_TEMP, 'a') as listfile_temp:
        if hit_flag > 0:
            listfile_temp.write('{} {} {}|{}'.format(DATETIME, seed_episode_number, name, name_j))
        else:
            listfile_temp.write('{} {} {}|{}'.format(last_update, episode_number, name, name_j))

# 新番組1話対応
new_hit_flag = 0
new_hit_flag_ng = 0
new_result = []
new_result_ng = []
# シードリストループ
for seed_info in seed_list:
    title = seed_info[0]
    if re.search(' - 01 ', title):
        title_en = re.sub(r'\[.*] (.*) - 01 .*', r'\1', title)

        # 重複を避けるため、new_program.txtを検索
        if swutil.grep_file(NEW_PROGRAM_FILE, title_en) != "":
            title_ja = get_jp_title(title_en)

            if title_ja != '':
                # 日本語タイトルが取得できていたら、新番組取得済リストへ追加
                # チェックリスト(tempと実体両方)に次回取得のためのレコードを追加
                new_hit_flag = 1
                swutil.writefile_append(LIST_FILE, '{} {} {}|{}'.format(DATETIME, '0', title_en, title_ja))
                swutil.writefile_append(LIST_TEMP, '{} {} {}|{}'.format(DATETIME, '0', title_en, title_ja))
                swutil.writefile_append(NEW_PROGRAM_FILE, title_en)
                new_result.append(title_en)
                os.makedirs(DOWNLOAD_DIR + '/' + title_ja)
            else:
                # 日本語タイトルが取得できなかった1話は何もしないが報告だけする
                new_hit_flag_ng = 1
                swutil.writefile_append(NEW_RESULT_FILE_NG, title_en)

if new_hit_flag == 1:
    post_msg='@here 新番組検知！\n' + \
                'リストに追加されたので、次回ダウンロード対象となります\n' + \
                '対象外にする場合は、リストから削除、保存ディレクトリを削除してください\n' + \
                '```' + '\n'.join(new_result) + '```'
    slackpost(post_msg)

if new_hit_flag_ng == 1:
    post_msg='@here 新番組検知！\n' + \
             '検知しましたが、日本語タイトルが検索で取得できなかったので、何もしませんでした\n' + \
             '手動追加を検討してください\n' + \
             '```' + '\n'.join(new_result_ng) + '```'
    slackpost(post_msg)

# 何らかのエラーで途中で処理が途切れたりして、チェックリスト実体とtempに行数の差が出てしまった場合、警告



