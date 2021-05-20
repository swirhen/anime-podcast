# swirhen.tv slackbot
# mention plugin
# notice: ../slackbot_run.pyから読み込まれるので、カレントディレクトリは1個上の扱い
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
from slackbot.bot import respond_to
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argment section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
GIT_ROOT_DIR = '/home/swirhen/sh'


@respond_to('^ *でかした.*')
@respond_to('^ *よくやった.*')
def doya(message):
    message.send('(｀・ω・´)ドヤァ...')


# 最近の自動取得seed問い合わせ
@respond_to('^ *seed(.*)')
def announce_seed_info(message, argment):
    if argment != '':
        past_days = int(argment)
    else:
        past_days = 3
    message.send(f'あつめた種の情報をおしらせするよ(さいきん{past_days}にちぶん)')
    paths = sorted(list(pathlib.Path(SEED_DOWNLOAD_DIR).glob('2*')), reverse=True)
    get_paths = paths[:past_days]
    seed_info = dict()
    for get_path in get_paths:
        if not get_path.name in seed_info:
            seed_info[get_path.name] = []

        seed_list = list(pathlib.Path(get_path).glob('*'))
        for seed in seed_list:
            seed_info[get_path.name].append(seed.name)

    post_str = '```'
    for dir in seed_info:
        post_str += f'directory {dir} in seeds:\n'
        for seed in seed_info[dir]:
            post_str += f'    {seed}\n'

    post_str += '```'

    message.send(post_str)


# 取得seedを移動、栽培
@respond_to('^ *tdl(.*)')
def torrent_move_and_download(message, argment):
    tdatetime = datetime.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'/data/share/temp/torrentsearch/{date}'
    argments = argment.split()
    seed_dir = ''
    target_dir = ''
    keyword = ''
    if len(argments) > 1:
        seed_dir = argments[0]
        target_dir = argments[1]
        if len(argments) > 2:
            keyword = argments[2]
    else:
        message.send('つかいかた(´･ω･`)\n'
                     'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n'
                     'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n'
                     'いどうさきディレクトリ:\n'
                     'd: どうじん c: みせいりほん m: えろまんが\n'
                     'cm: でれおんがく cl: でれらいぶ\n'
                     'mm: みりおんがく ml:みりらいぶ\n'
                     'sm:しゃにおんがく sl:しゃにらいぶ\n'
                     'hm:ほろおんがく hl:ほろらいぶ'
                     '\nもしくは ふるぱすもじれつ')
        return 1

    # 種移動元：移動先決定
    if seed_dir == 't':
        seed_dir = pathlib.Path(today_download_dir)
    else:
        seed_dir = pathlib.Path(f'{SEED_DOWNLOAD_DIR}/{seed_dir}')

    if target_dir == 'd':
        target_dir = sorted(list(pathlib.Path(SHARE_TEMP_DIR).glob('d2*/')), reverse=True)[0]
    elif target_dir == 'm':
        target_dir = sorted(list(pathlib.Path(SHARE_TEMP_DIR).glob('c2*/')), reverse=True)[0]
    elif target_dir == 'c':
        target_dir = list(pathlib.Path(SHARE_TEMP_DIR).glob('01*/'))[0]
    elif target_dir == 'cm':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER CINDERELLA GIRLS').glob('music'))[0]
    elif target_dir == 'cl':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER CINDERELLA GIRLS').glob('livedvd'))[0]
    elif target_dir == 'mm':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER MILLION LIVE').glob('music'))[0]
    elif target_dir == 'ml':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER MILLION LIVE').glob('livedvd'))[0]
    elif target_dir == 'sm':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER Shiny Colors').glob('music'))[0]
    elif target_dir == 'sl':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/THE IDOLM@STER Shiny Colors').glob('livedvd'))[0]
    elif target_dir == 'hm':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/hololive IDOL PROJECT').glob('music'))[0]
    elif target_dir == 'hl':
        target_dir = list(pathlib.Path(f'{SHARE_TEMP_DIR}/hololive IDOL PROJECT').glob('live'))[0]
    elif os.path.isdir(pathlib.Path(target_dir)):
        print('target_dir fullpath check: OK')
    else:
        message.send('いどうさきディレクトリ:\n'
                     'd: どうじん c: みせいりほん m: えろまんが\n'
                     'cm: でれおんがく cl: でれらいぶ\n'
                     'mm: みりおんがく ml:みりらいぶ\n'
                     'sm:しゃにおんがく sl:しゃにらいぶ\n'
                     'hm:ほろおんがく hl:ほろらいぶ\n'
                     'もしくは ふるぱすもじれつ')
        return 1

    post_str = ''
    glob_str = '*'
    if keyword != '':
        post_str = f' keyword: {keyword}'
        glob_str = f'*{keyword}*'
    message.send(f'たねのいどう src: {str(seed_dir)} dst: {str(target_dir)}{post_str}')

    seeds = list(pathlib.Path(seed_dir).glob(glob_str))
    seed_names = []
    for seed in seeds:
        shutil.move(str(seed), str(target_dir))
        seed_names.append(seed.name)

    # 栽培
    seedlist = list(pathlib.Path(target_dir).glob('*.torrent'))
    if len(seedlist) == 0:
        message.send('たねがみつからなかったよ(´･ω･`)')
        return 1
    else:
        post_str = '```いどうしたたね:\n' + '\n'.join(seed_names) + '```'
        message.send(post_str)

    message.send('さいばいをかいしするよ(｀･ω･´)')

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

    message.send('おわったよ(｀･ω･´)')


# torrent 検索
@respond_to('^ *ts(.*)')
def torrent_search(message, argment):
    tdatetime = datetime.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'/data/share/temp/torrentsearch/{date}'
    argments = argment.split()
    keyword = ''
    target_category = 'all'
    if len(argments) > 0:
        keyword = argments[0]
        if len(argments) > 1:
            target_category = argments[1]
    else:
        message.send('つかいかた(´･ω･`)\nts [けんさくキーワード] [たいしょうカテゴリ]\nカテゴリ: doujin/manga/music/comic/live/all\n(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)')
        return 1

    message.send(f'さがしてくるよ(｀･ω･´)\nたいしょうカテゴリ: {target_category} きーわーど: {keyword}')
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

        message.send(post_str)
    else:
        message.send('なかったよ(´･ω･`)')
