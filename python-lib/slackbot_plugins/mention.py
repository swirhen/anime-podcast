# swirhen.tv slackbot
# mention plugin
# notice: ../slackbot_run.pyから読み込まれるので、カレントディレクトリは1個上の扱い
# import section
import os
import pathlib
import sys
from datetime import datetime as dt
import datetime
from slackbot.bot import respond_to
import slackbot_settings
from slacker import Slacker
slack = Slacker(slackbot_settings.API_TOKEN)
import bot_util as bu
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argument section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)


@respond_to('^ *でかした.*')
@respond_to('^ *よくやった.*')
def doya(message):
    message.send('(｀・ω・´)ドヤァ...')


# 最近の自動取得seed問い合わせ
@respond_to('^ *seed(.*)')
def announce_seed_info(message, argument):
    if argument != '':
        past_days = int(argument)
    else:
        past_days = 3
    message.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
    result = bu.get_seed_directory(past_days)
    message.send(f'```{result}```')


# 取得seedを移動のみ
@respond_to('^ *tmv(.*)')
def torrent_move(message, argument):
    tdatetime = dt.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'/data/share/temp/torrentsearch/{date}'
    arguments = argument.split()
    seed_dir = ''
    target_dir = ''
    keyword = ''
    if len(arguments) > 1:
        seed_dir = arguments[0]
        target_dir = arguments[1]
        if len(arguments) > 2:
            keyword = arguments[2]
    else:
        message.send('つかいかた(´・ω・`)\n'
                     'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n'
                     'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n'
                     'いどうさきディレクトリ:\n'
                     'd: どうじん c: みせいりほん m: えろまんが\n'
                     'cm: でれおんがく cl: でれらいぶ\n'
                     'mm: みりおんがく ml:みりらいぶ\n'
                     'sm:しゃにおんがく sl:しゃにらいぶ\n'
                     'hm:ほろおんがく hl:ほろらいぶ\n'
                     'もしくは ふるぱすもじれつ')
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
    seedlist = bu.get_seeds_list(target_dir)
    if len(seedlist) == 0:
        message.send('たねがみつからなかったよ(´・ω・`)')
        return 1
    else:
        post_str = '```いどうしたたね:\n' + '\n'.join(seedlist) + '```'
        message.send(post_str)


# 取得seedを移動、栽培
@respond_to('^ *tdl(.*)')
def torrent_move_and_download(message, argument):
    tdatetime = dt.now()
    date = tdatetime.strftime('%Y%m%d')
    today_download_dir = f'/data/share/temp/torrentsearch/{date}'
    arguments = argument.split()
    seed_dir = ''
    target_dir = ''
    keyword = ''
    if len(arguments) > 1:
        seed_dir = arguments[0]
        target_dir = arguments[1]
        if len(arguments) > 2:
            keyword = arguments[2]
    else:
        message.send('つかいかた(´・ω・`)\n'
                     'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n'
                     'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n'
                     'いどうさきディレクトリ:\n'
                     'd: どうじん c: みせいりほん m: えろまんが\n'
                     'cm: でれおんがく cl: でれらいぶ\n'
                     'mm: みりおんがく ml:みりらいぶ\n'
                     'sm:しゃにおんがく sl:しゃにらいぶ\n'
                     'hm:ほろおんがく hl:ほろらいぶ\n'
                     'もしくは ふるぱすもじれつ')
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
        message.send('たねがみつからなかったよ(´・ω・`)')
        return 1
    else:
        post_str = '```いどうしたたね:\n' + '\n'.join(seedlist) + '```'
        message.send(post_str)

    message.send('さいばいをかいしするよ(｀・ω・´)')

    bu.plant_seed(target_dir)

    message.send('おわったよ(｀・ω・´)')


# torrent 検索
@respond_to('^ *ts(.*)')
def torrent_search(message, argument):
    arguments = argument.split()
    keyword = ''
    target_category = 'all'
    if len(arguments) > 0:
        keyword = arguments[0]
        if len(arguments) > 1:
            target_category = arguments[1]
    else:
        message.send('つかいかた(´・ω・`)\n'
                     'ts [けんさくキーワード] [たいしょうカテゴリ]\n'
                     'カテゴリ: doujin/manga/music/comic/live/all\n'
                     '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)')
        return 1

    message.send(f'さがしてくるよ(｀・ω・´)\n'
                 f'たいしょうカテゴリ: {target_category} きーわーど: {keyword}')
    result = bu.seed_search(keyword, target_category)
    message.send(result)


# torrent 最近のリスト
@respond_to('^ *tl(.*)')
def report_seed_list(message, argument):
    tdatetime = dt.now()
    date_time = tdatetime.strftime('%Y%m%d%H%M%S')
    result_file_name = f'{SCRIPT_DIR}/seed_list_{date_time}.txt'
    arguments = argument.split()
    target_category = ''
    if len(arguments) > 0:
        target_category = arguments[0]
    else:
        message.send('つかいかた(´・ω・`)\n'
                     'tl [たいしょうカテゴリ]\n'
                     'カテゴリ: doujin/manga/music/comic/live\n'
                     '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ)')
        return 1

    seed_list = trsc.get_seed_list(target_category)
    if len(seed_list) > 0:
        message.send(f'さいきんまかれたたねのリストだよ(｀・ω・´)\n'
                     f'たいしょうカテゴリ: {target_category}')
        result = ''
        for seed in seed_list:
            result += f'{seed[1]}\n'
        swiutil.writefile_new(result_file_name, result)
        file_upload(result_file_name, result_file_name, 'text', message)
        os.remove(result_file_name)


# twitter検索
@respond_to('^ *tws(.*)')
def twitter_search(message, argument):
    arguments = argument.split()
    keyword = ''
    channel = ''
    since = ''
    until = ''
    your_nick_ignore_flg = ''
    nick_flg = ''
    if len(arguments) > 2:
        keyword = arguments[0]
        channel = arguments[1]
        since = arguments[2]
        if len(arguments) > 3:
            until = arguments[3]
            if len(arguments) > 4:
                your_nick_ignore_flg = arguments[4]
                if len(arguments) > 5:
                    nick_flg = arguments[5]
    else:
        message.send('つかいかた(´・ω・`)\n'
                     'tws [けんさくキーワード or twitterid] [チャンネル] [けんさくかいしにちじ] (けんさくしゅうりょうにちじ) (じぶんのnickをむしする) (twitteridでけんさく)\n'
                     'チャンネル: y/s/k/e/f/c/m/h/ha\n'
                     '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)\n'
                     'けんさくかいしにちじ: YYYY-MM-DD HH:MM:SSけいしき\n'
                     'もしくは [なんふんまえ]m/[なんじかんまえ]h/[なんにちまえ]d\n'
                     'けんさくしゅうりょうにちじ: nowといれたら げんざいにちじ\n'
                     'じぶんのtwitteridをむしする: デフォルトは むしする(なにかいれると むししない)\n'
                     'twitteridでけんさく: デフォルトはキーワードけんさく(なにかいれると twitteridでけんさく)')
        return 1

    if channel == 'y':
        channel = '#Twitter有名人@t'
    elif channel == 's':
        channel = '#twitter声優@t'
    elif channel == 'k':
        channel = '#twitter格ゲー@t'
    elif channel == 'e':
        channel = '#twitter絵描きさん@t'
    elif channel == 'f':
        channel = '#おともだちtwitter@t'
    elif channel == 'c':
        channel = '#シンデレラ一門@t'
    elif channel == 'm':
        channel = '#ミリオン一座@t'
    elif channel == 'h':
        channel = '#hololive@t'
    elif channel == 'ha':
        channel = '#holoart@t'
    else:
        message.send('チャンネル: y/s/k/e/f/c/m/h/ha\n'
                     '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)\n')
        return 1

    now_time = dt.now()
    now_datetime = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    if since[-1] == 'm':
        shift_minutes = int(since[:-1])
        since = (now_time - datetime.timedelta(minutes=int(shift_minutes))).strftime('%Y/%m/%d %H:%M:%S')
    elif since[-1] == 'h':
        shift_hours = int(since[:-1])
        since = (now_time - datetime.timedelta(hours=int(shift_hours))).strftime('%Y/%m/%d %H:%M:%S')
    elif since[-1] == 'd':
        shift_days = int(since[:-1])
        since = (now_time - datetime.timedelta(days=int(shift_days))).strftime('%Y/%m/%d %H:%M:%S')

    if until[-1] == 'm':
        shift_minutes = int(until[:-1])
        until = (now_time - datetime.timedelta(minutes=int(shift_minutes))).strftime('%Y/%m/%d %H:%M:%S')
    elif until[-1] == 'h':
        shift_hours = int(until[:-1])
        until = (now_time - datetime.timedelta(hours=int(shift_hours))).strftime('%Y/%m/%d %H:%M:%S')
    elif until[-1] == 'd':
        shift_days = int(until[:-1])
        until = (now_time - datetime.timedelta(days=int(shift_days))).strftime('%Y/%m/%d %H:%M:%S')
    elif until == 'now':
        until = now_datetime

    k_n_str = 'キーワード'
    k_n_i_str = 'むしする'
    if nick_flg != '':
        nick_flg = True
        k_n_str = 'twitterid'
    if your_nick_ignore_flg != '':
        your_nick_ignore_flg = False
        k_n_i_str = 'むししない'

    post_str = f'けんさくするにぇ(｀・ω・´)\n' \
               f'{k_n_str}: {keyword} チャンネル: {channel}\n' \
               f'いつから: {since} いつまで: {until}\n' \
               f'じぶんのtwitteridをむしする: {k_n_i_str}'

    message.send(post_str)
    result = bu.twitter_search(keyword, channel, since, until, your_nick_ignore_flg, nick_flg)
    if len(result) > 0:
        message.send('みつかったにぇ！(｀・ω・´)')
        if len(result) > 4000:
            tdatetime = dt.now()
            date_time = tdatetime.strftime('%Y%m%d%H%M%S')
            result_file_name = f'{SCRIPT_DIR}/twitter_search_{date_time}.txt'
            swiutil.writefile_new(result_file_name, result.replace('`',''))
            file_upload(result_file_name, result_file_name, 'text', message)
            os.remove(result_file_name)
        else:
            message.send(result)
    else:
        message.send('なかったにぇ(´・ω・`)')


def file_upload(filename, filetitle, filetype, message):
    if os.path.getsize(filename) == 0:
        message.send('```(no log)```')
    else:
        slack.files.upload(
            filename,
            filename=filetitle,
            filetype=filetype,
            channels=message._body['channel'],
        )
