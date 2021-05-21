# swirhen.tv bot utility
# slackbot と discord botから呼び出す共通処理
# import section
import os
import re
import sys
import pathlib
import shutil
import subprocess
from datetime import datetime
import time
import git
import urllib.request
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argment section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
GIT_ROOT_DIR = '/home/swirhen/sh'


def get_seed_directory(past_days):
    result = ''
    paths = sorted(list(pathlib.Path(SEED_DOWNLOAD_DIR).glob('2*')), reverse=True)
    get_paths = paths[:past_days]
    seed_info = dict()
    for get_path in get_paths:
        if not get_path.name in seed_info:
            seed_info[get_path.name] = []

        seed_list = list(pathlib.Path(get_path).glob('*'))
        for seed in seed_list:
            seed_info[get_path.name].append(seed.name)

    for path in seed_info:
        result += f'directory {path} in seeds:\n'
        for seed in seed_info[path]:
            result += f'    {seed}\n'

    return result


def seed_search(keyword, target_category):
    tdatetime = datetime.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'{SEED_DOWNLOAD_DIR}/{date}'
    seed_list = trsc.get_seed_list(target_category)

    hit_flag = 0
    hit_result = []
    for seed_item in seed_list:
        item_category = seed_item[0]
        item_title = seed_item[1]
        item_link = seed_item[2]

        if re.search(keyword, item_title) and \
                len(swiutil.grep_file(DL_URL_LIST_FILE, item_link)) == 0:
            hit_flag = 1
            if not os.path.isdir(today_download_dir):
                os.mkdir(today_download_dir)
            item_title = swiutil.truncate(item_title.translate(str.maketrans('/;!','___')), 247)
            hit_result.append([item_category, item_title, keyword])
            urllib.request.urlretrieve(item_link, f'{today_download_dir}/{item_title}.torrent')
            swiutil.writefile_append(DL_URL_LIST_FILE, item_link)

    if hit_flag == 1:
        post_str = f'みつかったよ\n```# 結果\n'
        for result_item in hit_result:
            post_str += f'カテゴリ: {result_item[0]} キーワード: {result_item[2]} タイトル: {result_item[1]}\n'

        post_str += f'# ダウンロードしたseedファイル ({today_download_dir})\n'
        for result_item in hit_result:
            post_str += f'{result_item[1]}.torrent\n'

        post_str += '```'

        repo = git.Repo(GIT_ROOT_DIR)
        repo.git.commit(DL_URL_LIST_FILE, message='download_url.txt update')
        repo.git.pull()
        repo.git.push()

        return post_str
    else:
        return 'なかったよ(´･ω･`)'
