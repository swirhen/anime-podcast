# swirhen.tv slackbot
# mention plugin
# notice: ../slackbot_run.pyから読み込まれるので、カレントディレクトリは1個上の扱い
# import section
import os
import sys
import pathlib
import shutil
import subprocess
from datetime import datetime
import time
from slackbot.bot import respond_to
import bot_util as bu
sys.path.append('/home/swirhen/sh/checker/torrentsearch')

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
    message.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
    result = bu.get_seed_directory(past_days)
    message.send(f'```{result}```')


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

    target_dir = bu.choose_target_dir(target_dir)
    if target_dir == '':
        message.send('いどうさきディレクトリ:\n'
                     'd: どうじん c: みせいりほん m: えろまんが\n'
                     'cm: でれおんがく cl: でれらいぶ\n'
                     'mm: みりおんがく ml:みりらいぶ\n'
                     'sm:しゃにおんがく sl:しゃにらいぶ\n'
                     'hm:ほろおんがく hl:ほろらいぶ\n'
                     'もしくは ふるぱすもじれつ')
        return 1

    result = bu.seed_move(seed_dir, target_dir, keyword)
    message.send(result)

    # 栽培
    seedlist = bu.get_seeds_list(target_dir)
    if len(seedlist) == 0:
        message.send('たねがみつからなかったよ(´･ω･`)')
        return 1
    else:
        post_str = '```いどうしたたね:\n' + '\n'.join(seedlist) + '```'
        message.send(post_str)

    message.send('さいばいをかいしするよ(｀･ω･´)')

    bu.plant_seed(target_dir)

    message.send('おわったよ(｀･ω･´)')


# torrent 検索
@respond_to('^ *ts(.*)')
def torrent_search(message, argment):
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
    result = bu.seed_search(keyword, target_category)
    message.send(result)
