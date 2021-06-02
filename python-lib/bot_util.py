# swirhen.tv bot utility
# slackbot と discord botから呼び出す共通処理
# import section
import os
import re
import sys
import pathlib
import shutil
import subprocess
import locale
import datetime
import time
import MySQLdb
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argument section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
GIT_ROOT_DIR = '/home/swirhen/sh'
YOUR_NICK = 'swirhen'
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
HOLOMEN_TWITTER_ID_LIST = f'{SCRIPT_DIR}/holomen_twitter_id_list.txt'


# 日付文字列取得
def get_now_datetime_str(dt_type, shift_datetime='0'):
    now_datetime = datetime.datetime.now()
    if shift_datetime[-1] == 'm':
        date_time = now_datetime - datetime.timedelta(minutes=int(shift_datetime[:-1]))
    elif shift_datetime[-1] == 'h':
        date_time = now_datetime - datetime.timedelta(hours=int(shift_datetime[:-1]))
    elif shift_datetime[-1] == 'd':
        date_time = now_datetime - datetime.timedelta(days=int(shift_datetime[:-1]))
    else:
        date_time = now_datetime

    if dt_type == 'YMDHMS':
        return date_time.strftime('%Y%m%d%H%M%S')
    elif dt_type == 'YMD_HMS':
        return date_time.strftime('%Y/%m/%d-%H:%M:%S')
    elif dt_type == 'YMD_HMS_SQL':
        return date_time.strftime('%Y-%m-%d %H:%M:%S')
    elif dt_type == 'YMD_SQL':
        return date_time.strftime('%Y-%m-%d')
    elif dt_type == 'YMD':
        return date_time.strftime('%Y%m%d')
    elif dt_type == 'YMD_A':
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        return date_time.strftime('%Y/%-m/%-d (%A)')
    elif dt_type == 'H':
        return date_time.strftime('%-H')
    elif dt_type == 'HM':
        return date_time.strftime('%-H:%M')
    else:
        return ''


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
def seed_search(keyword, target_category, not_dl_flg):
    date = get_now_datetime_str('YMD')
    today_download_dir = f'{SEED_DOWNLOAD_DIR}/{date}'
    if not_dl_flg == '':
        hit_result = trsc.search_seed(True, target_category, keyword)
    else:
        hit_result = trsc.search_seed(False, target_category, keyword)

    if len(hit_result) > 0:
        post_str = f'みつかったしゅば(｀・ω・´)\n```# 結果\n'
        for result_item in hit_result:
            post_str += f'カテゴリ: {result_item[0]} キーワード: {result_item[2]} タイトル: {result_item[1]}\n'
            if not_dl_flg != '':
                if result_item[4] != None:
                    post_str += f'ダウンロード済み 保存先: {result_item[4]}\n'
                else:
                    post_str += f'URL: {result_item[3]}\n'

        if not_dl_flg == '':
            post_str += f'# ダウンロードしたseedファイル ({today_download_dir})\n'
            for result_item in hit_result:
                post_str += f'{result_item[1]}.torrent\n'

        post_str += '```'
        return post_str
    else:
        return 'なかったしゅば(´・ω・`)'


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
    date = get_now_datetime_str('YMD')
    today_download_dir = f'{SEED_DOWNLOAD_DIR}/{date}'

    result = ''
    # 種移動元決定
    if seed_dir == 't':
        seed_dir = today_download_dir
    elif str.isdigit(seed_dir) and (int(seed_dir) > 0 or int(seed_dir) >= 100):
        date_offset = get_now_datetime_str('YMD', f'{seed_dir}d')
        seed_dir = str(pathlib.Path(f'{SEED_DOWNLOAD_DIR}/{date_offset}'))
    else:
        seed_dir = str(pathlib.Path(f'{SEED_DOWNLOAD_DIR}/{seed_dir}'))

    post_str = ''
    glob_str = '*'
    if keyword != '':
        post_str = f' keyword: {keyword}'
        glob_str = f'*{keyword}*'
    result = f'たねのいどう src: {str(seed_dir)} dst: {target_dir}{post_str}\n'

    seeds = list(pathlib.Path(seed_dir).glob(glob_str))
    for seed in seeds:
        shutil.move(str(seed), target_dir)

    return result


# 移動先の種列挙
def get_seeds_list(target_dir):
    result = []
    seeds = list(pathlib.Path(target_dir).glob('*.torrent'))
    for seed in seeds:
        result.append(seed.name)

    return result


# 種栽培
def plant_seed(target_dir):
    proc = subprocess.Popen(f'aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 --dir="{target_dir}" "{target_dir}/"*.torrent', shell=True)
    time.sleep(10)

    while True:
        if len(list(pathlib.Path(target_dir).glob('*.aria2'))) == 0:
            proc.kill()
            break

        time.sleep(10)

    # seeds backup
    seed_backup(target_dir)


# seed backup
def seed_backup(target_dir):
    for seed in pathlib.Path(target_dir).glob('*.torrent'):
        if not os.path.isfile(f'{SEED_BACKUP_DIR}/{seed.name}'):
            shutil.move(str(seed), SEED_BACKUP_DIR)
        else:
            os.remove(str(seed))


# twitter search
def twitter_search(keyword_or_nick, channel, since, until, your_nick_ignore_flg=True, nick_flg=False):
    # database connect
    connection = MySQLdb.connect(
        host='localhost',
        user='tiarra',
        passwd='arrati',
        db='tiarra')
    cursor = connection.cursor()

    # all log select
    select_sql = "select n.name, l.log, l.created_on" \
                 " from channel c, log l, nick n" \
                 " where l.channel_id = c.id" \
                 " and l.nick_id = n.id" \
                f" and l.created_on >= '{since}'" \
                f" and l.created_on <= '{until}'" \
                f" and c.name = '{channel}'"

    if nick_flg:
        select_sql += f" and n.name = '{keyword_or_nick}'"

    if your_nick_ignore_flg:
        select_sql += f" and n.name not like '%{YOUR_NICK}%'"

    select_sql += " order by l.created_on"

    cursor.execute(select_sql)

    logs = []
    nick_p = ''
    log_text_p = ''
    date_p = ''
    for row in cursor:
        nick = row[0]
        log_text = row[1]
        date = row[2].strftime('%Y/%m/%d %H:%M:%S')

        # 1行前とnick, 投稿日時が同じ場合はログに改行を加えて追加する
        # 違う場合、1行前のものを配列に加える
        if nick_p != '':
            if nick_p == nick and date_p == date:
                log_text_p += f'\n{log_text}'
            else:
                logs.append([nick_p, log_text_p, date_p])
                log_text_p = log_text

        nick_p = nick
        date_p = date

    # ループ終了 最後の行
    logs.append([nick_p, log_text_p, date_p])

    cursor.close()

    result = []
    result_str = ''
    for log in logs:
        nick = log[0]
        text = log[1]
        date = log[2]

        if not nick_flg:
            if re.search(keyword_or_nick, text.replace('\n','_')):
                result.append(f'[{date}] <{nick}> {text}')
        else:
            result.append(f'[{date}] <{nick}> {text}')

    if len(result) > 0:
        result_str += '```' + '\n'.join(result) + '```'

    return result_str


# twitter search(nick and count)
def twitter_search2(nick, count):
    since = get_now_datetime_str('YMD_HMS', '7d')

    # database connect
    connection = MySQLdb.connect(
        host='localhost',
        user='tiarra',
        passwd='arrati',
        db='tiarra')
    cursor = connection.cursor()

    # all log select
    select_sql = "select n.name, l.log, l.created_on" \
                    " from channel c, log l, nick n" \
                    " where l.channel_id = c.id" \
                    " and l.nick_id = n.id" \
                    f" and l.created_on >= '{since}'" \
                    f" and c.name = '#hololive@t'" \
                    f" and n.name = '{nick}'" \
                    f" and n.name not like '%swirhen%'" \
                    " order by l.created_on"

    cursor.execute(select_sql)

    logs = []
    if len(cursor.fetchall()) > 0:
        nick_p = ''
        log_text_p = ''
        date_p = ''
        for row in cursor:
            nick = row[0]
            log_text = row[1]
            date = row[2].strftime('%Y/%m/%d %H:%M:%S')

            # 1行前とnick, 投稿日時が同じ場合はログに改行を加えて追加する
            # 違う場合、1行前のものを配列に加える
            if nick_p != '':
                if nick_p == nick and date_p == date:
                    log_text_p += f'\n{log_text}'
                else:
                    logs.append([nick_p, log_text_p, date_p])
                    log_text_p = log_text

            nick_p = nick
            date_p = date

        # ループ終了 最後の行
        logs.append([nick_p, log_text_p, date_p])

    cursor.close()

    result_str = ''
    if len(logs) > 0:
        logs.reverse()
        for i,log in enumerate(logs):
            if i >= int(count):
                break
            nick = log[0]
            text = log[1]
            date = log[2]
            result_str = f'[{date}] <{nick}> {text}\n{result_str}'

        result_str = f'```{result_str}```'

    return result_str


# チャンネル名判定
def choose_channel(target_channel):
    if target_channel == 'y':
        target_channel = '#Twitter有名人@t'
    elif target_channel == 's':
        target_channel = '#twitter声優@t'
    elif target_channel == 'k':
        target_channel = '#twitter格ゲー@t'
    elif target_channel == 'e':
        target_channel = '#twitter絵描きさん@t'
    elif target_channel == 'f':
        target_channel = '#おともだちtwitter@t'
    elif target_channel == 'c':
        target_channel = '#シンデレラ一門@t'
    elif target_channel == 'm':
        target_channel = '#ミリオン一座@t'
    elif target_channel == 'h':
        target_channel = '#hololive@t'
    elif target_channel == 'ha':
        target_channel = '#holoart@t'
    else:
        target_channel = ''
    return target_channel


# 各種返答メッセージ
MESSAGE_DICT = dict()
MESSAGE_DICT['usage_torrent_move'] = 'つかいかた(´・ω・`)\n' \
                                     'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n' \
                                     'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n' \
                                     'いどうさきディレクトリ:\n' \
                                     'd: どうじん c: みせいりほん m: えろまんが\n' \
                                     'cm: でれおんがく cl: でれらいぶ\n' \
                                     'mm: みりおんがく ml:みりらいぶ\n' \
                                     'sm:しゃにおんがく sl:しゃにらいぶ\n' \
                                     'hm:ほろおんがく hl:ほろらいぶ\n' \
                                     'もしくは ふるぱすもじれつ'
MESSAGE_DICT['usage_torrent_move_directory_choice'] = 'いどうさきディレクトリ:\n' \
                                                      'd: どうじん c: みせいりほん m: えろまんが\n' \
                                                      'cm: でれおんがく cl: でれらいぶ\n' \
                                                      'mm: みりおんがく ml:みりらいぶ\n' \
                                                      'sm:しゃにおんがく sl:しゃにらいぶ\n' \
                                                      'hm:ほろおんがく hl:ほろらいぶ\n' \
                                                      'もしくは ふるぱすもじれつ'
MESSAGE_DICT['usage_torrent_search'] = 'つかいかた(´・ω・`)\n' \
                                       'ts [けんさくキーワード] [たいしょうカテゴリ]\n' \
                                       'カテゴリ: doujin/manga/music/comic/live/all\n' \
                                       '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)'
MESSAGE_DICT['usage_report_seed_list'] = 'つかいかた(´・ω・`)\n' \
                                         'tl [たいしょうカテゴリ]\n' \
                                         'カテゴリ: doujin/manga/music/comic/live\n' \
                                         '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ)'
MESSAGE_DICT['usage_twitter_search'] = 'つかいかた(´・ω・`)\n' \
                                       'tws [けんさくキーワード or twitterid] [チャンネル] [けんさくかいしにちじ] [けんさくしゅうりょうにちじ] [twitteridでけんさく] [じぶんのtwitteridをむしする]\n' \
                                       'チャンネル: y/s/k/e/f/c/m/h/ha\n' \
                                       '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)\n' \
                                       'けんさくかいしにちじ: YYYY-MM-DD HH:MM:SSけいしき\n' \
                                       'もしくは [なんふんまえ]m/[なんじかんまえ]h/[なんにちまえ]d\n' \
                                       'けんさくしゅうりょうにちじ: nowといれたら げんざいにちじ\n' \
                                       'twitteridでけんさく: 0: キーワードけんさく 1: twitteridでけんさく\n' \
                                       'じぶんのtwitteridをむしする: 0: むしする 1: むししない'
MESSAGE_DICT['usage_twitter_search_channel_choice'] = 'チャンネル: y/s/k/e/f/c/m/h/ha\n' \
                                                      '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)'
MESSAGE_DICT['usage_holomen_twitter_search'] = 'つかいかた(´・ω・`)\n' \
                                               'hts [twitterid or ニックネーム] (さかのぼるpostのかず デフォルト 5)'
MESSAGE_DICT['usage_swirhentv_feed_search'] = 'つかいかた(´・ω・`)\n' \
                                              'sws (けんさくキーワード)\n'\
                                              'すいれんtv のフィードを検索するぺこ(｀・ω・´)\n' \
                                              'けんさくキーワードをいれると フィードのタイトル/ファイル名/フィード内のタイトル から検索するぺこ\n' \
                                              'フィードリストはこちらぺこ(1日1回更新)\n' \
                                              'http://swirhen.tv/movie/pspmp4/swirhentv_feed_list.txt'


# 各種返答メッセージ
def generate_message(message_type):
    if message_type in MESSAGE_DICT:
        return MESSAGE_DICT[message_type]
    else:
        return ''


# ホロメン twitter id
def get_holomen_twitter_id(name):
    hit_flag = False
    if name != '':
        with open(HOLOMEN_TWITTER_ID_LIST) as file:
            for line in file.read().splitlines():
                names = line.split()[0]
                twitter = line.split()[1]
                if re.search(name, names) or re.search(name, twitter):
                    hit_flag = True
                    result = twitter
                    break
    if hit_flag:
        return result
    else:
        return ''