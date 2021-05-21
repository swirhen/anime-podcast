# swirhen.tv slackbot
# mention plugin
# notice: ../slackbot_run.pyから読み込まれるので、カレントディレクトリは1個上の扱い
# import section
import sys
from datetime import datetime
from slackbot.bot import respond_to
import bot_util as bu
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argument section
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
def announce_seed_info(message, argument):
    if argument != '':
        past_days = int(argument)
    else:
        past_days = 3
    message.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
    result = bu.get_seed_directory(past_days)
    message.send(f'```{result}```')


# 取得seedを移動、栽培
@respond_to('^ *tdl(.*)')
def torrent_move_and_download(message, argument):
    tdatetime = datetime.now()
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
        message.send('つかいかた(´･ω･`)\n'
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
def torrent_search(message, argument):
    arguments = argument.split()
    keyword = ''
    target_category = 'all'
    if len(arguments) > 0:
        keyword = arguments[0]
        if len(arguments) > 1:
            target_category = arguments[1]
    else:
        message.send('つかいかた(´･ω･`)\n'
                     'ts [けんさくキーワード] [たいしょうカテゴリ]\n'
                     'カテゴリ: doujin/manga/music/comic/live/all\n'
                     '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)')
        return 1

    message.send(f'さがしてくるよ(｀･ω･´)\n'
                 f'たいしょうカテゴリ: {target_category} きーわーど: {keyword}')
    result = bu.seed_search(keyword, target_category)
    message.send(result)


# torrent 最近のリスト
@respond_to('^ *tl(.*)')
def report_seed_list(message, argument):
    arguments = argument.split()
    keyword = ''
    if len(arguments) > 0:
        target_category = arguments[0]
    else:
        message.send('つかいかた(´･ω･`)\n'
                     'tl [たいしょうカテゴリ]\n'
                     'カテゴリ: doujin/manga/music/comic/live\n'
                     '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ)')
        return 1

    seed_list = trsc.get_seed_list(target_category)
    if len(seed_list) > 0:
        message.send(f'さいきんまかれたたねのリストだよ(｀･ω･´)\n'
                     f'たいしょうカテゴリ: {target_category}')
        post_str = '```'
        for seed in seed_list:
            post_str += f'{seed[1]}\n'
        post_str = '```'
        message.send(post_str)
