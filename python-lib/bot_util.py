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


# ダウンロードした種情報の取得
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


# 種検索＆ダウンロード
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
        post_str = f'みつかったよ(｀･ω･´)\n```# 結果\n'
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


# 移動先ディレクトリ判定
def choose_target_dir(target_dir):
    if target_dir == 'd':
        target_dir = sorted(list(pathlib.Path(SHARE_TEMP_DIR).glob('d2*/')), reverse=True)[0]
    elif target_dir == 'm':
        target_dir =  sorted(list(pathlib.Path(SHARE_TEMP_DIR).glob('c2*/')), reverse=True)[0]
    elif target_dir == 'c':
        target_dir =  list(pathlib.Path(SHARE_TEMP_DIR).glob('01*/'))[0]
    elif target_dir == 'cm':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER CINDERELLA GIRLS').glob('music'))[0]
    elif target_dir == 'cl':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER CINDERELLA GIRLS').glob('livedvd'))[0]
    elif target_dir == 'mm':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER MILLION LIVE').glob('music'))[0]
    elif target_dir == 'ml':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER MILLION LIVE').glob('livedvd'))[0]
    elif target_dir == 'sm':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER Shiny Colors').glob('music'))[0]
    elif target_dir == 'sl':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER Shiny Colors').glob('livedvd'))[0]
    elif target_dir == 'hm':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/hololive IDOL PROJECT').glob('music'))[0]
    elif target_dir == 'hl':
        target_dir =  list(pathlib.Path(f'{SHARE_TEMP_DIR}/hololive IDOL PROJECT').glob('live'))[0]
    elif os.path.isdir(pathlib.Path(target_dir)):
        target_dir = target_dir
    else:
        target_dir = ''

    return str(target_dir)


# 種の所定位置への移動
def seed_move(seed_dir, target_dir, keyword):
    tdatetime = datetime.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'{SEED_DOWNLOAD_DIR}/{date}'

    result = ''
    # 種移動元：移動先決定
    if seed_dir == 't':
        seed_dir = pathlib.Path(today_download_dir)
    else:
        seed_dir = pathlib.Path(f'{SEED_DOWNLOAD_DIR}/{seed_dir}')

    post_str = ''
    glob_str = '*'
    if keyword != '':
        post_str = f' keyword: {keyword}'
        glob_str = f'*{keyword}*'
    result = f'たねのいどう src: {str(seed_dir)} dst: {str(target_dir)}{post_str}\n'

    seeds = list(pathlib.Path(seed_dir).glob(glob_str))
    for seed in seeds:
        shutil.move(str(seed), str(target_dir))

    return result


# 種栽培
def plant_seed(target_dir):
    result = ''
    seedlist = list(pathlib.Path(target_dir).glob('*.torrent'))
    if len(seedlist) == 0:
        return f'たねがみつからなかったよ(´･ω･`) ({target_dir})'
    # else:
        # post_str = '```いどうしたたね:\n' + '\n'.join(seed_names) + '```'
        # message.send(post_str)

    # message.send('さいばいをかいしするよ(｀･ω･´)')

    proc = subprocess.Popen(f'aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 --dir="{str(target_dir)}" "{str(target_dir)}/"*.torrent', shell=True)
    time.sleep(10)

    while True:
        if len(list(pathlib.Path(target_dir).glob('*.aria2'))) == 0:
            proc.kill()
            break

        time.sleep(10)

    # seeds backup
    for seed in seedlist:
        if not os.path.isfile(f'{SEED_BACKUP_DIR}/{seed.name}'):
            shutil.move(str(seed), SEED_BACKUP_DIR)
        else:
            os.remove(str(seed))

    # message.send('おわったよ(｀･ω･´)')


# discord用 文字数が2000を超えたら改行単位で配列にする
def str_to_array(in_str):
    result = []
    if len(in_str) <= 2000:
        return [in_str]
    else:
        res_line = ''
        res_line_temp = ''
        for line in in_str.split('\n'):
            res_line_temp += f'{res_line}{line}\n'
            if len(res_line_temp) > 2000:
                result.append(res_line)
                res_line = line
            else:
                res_line = res_line_temp
            res_line_temp = ''

    result.append(res_line)

    return result
