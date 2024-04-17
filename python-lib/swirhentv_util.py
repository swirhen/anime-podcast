#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv python library
# import section
import os
import pathlib
import re
import shutil
import subprocess
from sys import stderr
import urllib.request
import requests
import time
import glob
from datetime import datetime as dt
from bs4 import BeautifulSoup
from slacker import Slacker
import slackbot_settings
import sqlite3
import make_feed_db as db

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
#RUBY_PATH = '/home/swirhen/.rbenv/versions/2.6.6/bin/ruby'
RUBY_PATH = 'ruby'
CHECKLIST_FILE_PATH = f'{SCRIPT_DIR}/../checklist.txt'
SEED_BACKUP_DIR = f'{SCRIPT_DIR}/../download_seeds'
DISCORD_WEBHOOK_URI_FILE = f'{SCRIPT_DIR}/discord_webhook_url'
FEED_XML_DIR = f'{SCRIPT_DIR}/../../98 PSP用'
SYOBOCAL_URI = 'http://cal.syoboi.jp/find?sd=0&kw='
SWIRHENTV_URI = 'http://swirhen.tv/movie/pspmp4/'
FEED_DB = f'{SCRIPT_DIR}/swirhentv_feed.db'
NYAA_MOVIE_FEED_DB = f'{SCRIPT_DIR}/../nyaa_movie_feed.db'

# slackにpostする
def slack_post(channel, text, username='swirhentv', icon_emoji=''):
    slack = Slacker(slackbot_settings.API_TOKEN)
    slack.chat.post_message(
        channel,
        text,
        username=username,
        icon_emoji=icon_emoji,
        link_names=1,
    )


# slackにファイルアップロード
def slack_upload(channel, filepath, filetype='text'):
    slack = Slacker(slackbot_settings.API_TOKEN)
    slack.files.upload(channels=channel, file_=filepath, filetype=filetype)


# twitterでつぶやく(tiarrametroのsocket経由)
def tweeet(text, channel='#Twitter@t2'):
    subprocess.run(f'/usr/bin/php /home/swirhen/tiasock/tiasock.php "{channel}" "{text}"', shell=True)


# discord channel decision
def get_discord_webhook_url(target_channel):
    result = ''
    with open(DISCORD_WEBHOOK_URI_FILE) as file:
        for line in file.read().splitlines():
            channel = line.split()[0]
            webhook_uri = line.split()[1]
            if channel == target_channel:
                result = webhook_uri
                break
    return result


# discordにpostする
def discord_post(channel, text):
    discord_webhook_uri = get_discord_webhook_url(channel)
    if discord_webhook_uri != '':
        main_content = {
            'content': text.replace('@channel', '@here')
        }
        try:
            requests.post(discord_webhook_uri, main_content)
        except Exception as e:
            print(e)


# discordにuploadする
def discord_upload(channel, filename):
    discord_webhook_uri = get_discord_webhook_url(channel)
    if discord_webhook_uri != '':
        with open(filename, 'rb') as file:
            files = {'param_name': (pathlib.Path(filename).name, file)}
            try:
                requests.post(discord_webhook_uri, files=files)
            except Exception as e:
                print(e)


# discord/slack multi post
def multi_post(channel, text, username='swirhentv', icon_emoji=''):
    if len(text) > 4000:
        if text.split('\n')[0][0] == '@':
            slack_post(channel, text.split('\n')[0])
            text = re.sub('^.*\n', '', text)
        if re.search('```', text):
            text = text.replace('```', '')
        date_time = dt.now().strftime('%Y%m%d%H%M%S')
        post_file_temp = f'{SCRIPT_DIR}/slack_post_temp_{date_time}.txt'
        writefile_new(post_file_temp, text)
        slack_upload(channel, post_file_temp)
        os.remove(post_file_temp)
    else:
        slack_post(channel, text, username, icon_emoji)

    if len(text) > 2000:
        if text.split('\n')[0][0] == '@':
            discord_post(channel, text.split('\n')[0])
            text = re.sub('^.*\n', '', text)
        if re.search('```', text):
            text = text.replace('```', '')
        date_time = dt.now().strftime('%Y%m%d%H%M%S')
        post_file_temp = f'{SCRIPT_DIR}/discord_post_temp_{date_time}.txt'
        writefile_new(post_file_temp, text)
        discord_upload(channel, post_file_temp)
        os.remove(post_file_temp)
    else:
        discord_post(channel, text.replace('@channel', '@here'))


# discord/slack multi upload
def multi_upload(channel, filename, filetype='text'):
    slack_upload(channel, filename, filetype)
    discord_upload(channel, filename)


# y/nをきく
def askconfirm():
    res = input('> ')
    if res == 'y' or res == 'Y':
        return 0
    elif res == 'n' or res == 'N':
        return 1
    else:
        print('y/nを入力してください。(EnterのみはNo)')
        askconfirm()


# grep(ファイル, 完全一致/部分一致)
def grep_file(file_path, word, complete_fetch=True):
    opt_str = ''
    if complete_fetch:
        opt_str = '-x'
    result = subprocess.run(f'grep {opt_str} "{word}" "{file_path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip().splitlines()
    return result


# grep(配列, 部分一致/完全一致)
def grep_list(greplist, word, regexp_mode=True):
    result = []
    for item in greplist:
        if regexp_mode:
            if re.search(word, item):
                result.append(item)
        else:
            if word == item:
                result.append(item)
    return result


# ファイル書き込み(新規)
def writefile_new(filepath, string):
    with open(filepath, 'w') as file:
        file.write(f'{string}\n')


# ファイル書き込み(追記)
def writefile_append(filepath, string):
    with open(filepath, 'a') as file:
        file.write(f'{string}\n')


# ファイル削除
def deletefile(filepath):
    os.remove(filepath)


# ファイルの行数を得る
def len_file(filepath):
    with open(filepath) as file:
        return len(file.readlines())


# キーワードの含まれる行を削除(部分一致/完全一致)
def sed_del(filepath, sed_keyword, regexp_mode=True):
    if regexp_mode:
        subprocess.run(f'sed -i -e "/{sed_keyword}/d" "{filepath}"', shell=True)
    else:
        subprocess.run(f'sed -i -e "/^{sed_keyword}$/d" "{filepath}"', shell=True)


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
    try:
        html = urllib.request.urlopen(f'{SYOBOCAL_URI}{search_word}')
    except Exception as e:
        print(e)
        return ''
    else:
        soup = BeautifulSoup(html, "html.parser")

        result = []
        for a in soup.find_all('a'):
            if re.search('tid', str(a)):
                result += a

        if len(result) > 0:
            return result[0].translate(str.maketrans({';': '；', '!': '！', ':': '：', '/': '／'}))
        else:
            return ''


# checklist.txtからチェックリストの配列を得る
# 書式は"最終更新日時 取得話数 英語タイトル名|日本語タイトル名
def make_check_list():
    check_lists = []
    with open(CHECKLIST_FILE_PATH) as file:
        # make check list
        for line in file.read().splitlines():
            if re.search('^Last Update', line):
                continue
            last_update = re.sub(r'^([^ ]+) ([^ ]+) (.*)', r'\1', line)
            episode_number = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\2', line)
            name = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).split('|')[0]
            name_j = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).split('|')[1]
            check_list = [last_update, episode_number, name, name_j]
            check_lists.append(check_list)

    return check_lists


# checklist.txtの最後のセクションから、英語タイトル -> 日本語タイトルの変換リストを得る
def make_rename_list():
    with open(CHECKLIST_FILE_PATH) as file:
        # make rename list
        renamelist = []
        for line in file.read().splitlines():
            if re.search('^Last Update', line):
                continue
            line = re.sub(r'^[^ ]+ [^ ]+ ', '', line)
            line = line.split('|')
            renamelist.append(line)

    return renamelist


# 種検索(sqlite3)
def get_feed_list(last_check_date):
    conn = sqlite3.connect(NYAA_MOVIE_FEED_DB)
    cur = conn.cursor()

    select_sql = 'select title, link from feed_data' \
                f' where created_at > "{last_check_date}"' \
                 ' and download_flag = 0'
    
    result = list(cur.execute(select_sql))
    conn.close()
    return result


# ダウンロードのアップデート
def update_download_feed(values):
    conn = sqlite3.connect(NYAA_MOVIE_FEED_DB)
    cur = conn.cursor()

    str_value = '", "'.join(values)
    update_sql = f'update feed_data set download_flag = True where link in ("{str_value}")'
    cur.execute(update_sql)
    conn.commit()
    conn.close()


# 新番組のアップデート
def update_new_program_feed(values, update):
    conn = sqlite3.connect(NYAA_MOVIE_FEED_DB)
    cur = conn.cursor()

    str_value = '", "'.join(values)
    update_sql = f'update feed_data set created_at = "{update}" where link in ("{str_value}")'
    cur.execute(update_sql)
    conn.commit()
    conn.close()


# 動画リネーム
# checklist.txtの後半(英語ファイル名|日本語ファイル名)のデータを使って動画ファイルをリネームする
# [英語ファイル名] -[SFX1][話数][SFX2](mp4 1280x720 aac).mp4
# -> [日本語ファイル名] 第[話数]話.mp4
# 第1引数: ディレクトリ(指定したディレクトリ以下のすべてのファイルをリネームする)
# 第2引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第3引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペース。
def rename_movie_file(file_path, separator1='\ ', separator2='\ '):
    return_log = []

    # make rename list
    renamelist = make_rename_list()

    # make file list
    os.chdir(file_path)
    file_list = []
    file_list.extend(
        glob.glob("*.mp4") + glob.glob("*.mkv") + glob.glob("*.avi") + glob.glob("*.wmv"))

    # rename files
    for filename in file_list:
        for name in renamelist:
            name_e = name[0]
            name_j = name[1]
            exp = r'.*(' + name_e + ').*' + separator1 + '([0-9]{0,1}[0-9][0-9](.5|.1)?)' + separator2 + '.*\.(.*)'
            name = re.sub(exp, r'\1', filename)
            num = re.sub(exp, r'\2', filename)
            ext = re.sub(exp, r'\4', filename)

            if name_e == name:
                td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
                if os.path.isfile(f'{filename}.aria2'):
                    log_str = f'{filename}.aria2 が存在。 成育中'
                else:
                    new_name = f'{name_j} 第{num}話.{ext}'
                    if file_path != new_name:
                        log_str = f'rename file: {filename} -> {new_name}'
                        os.rename(filename, new_name)
                    else:
                        log_str = '変更後のファイル名が同じ'

                return_log.append(f'{td} {log_str}')
                print(log_str)
                break

    return '\n'.join(return_log)


# 動画移動
# checklist.txtの後半(日本語ファイル名)のデータを使って動画ファイルを移動する
# 引数のファイルが一致する日本語ファイル名を同名のディレクトリに移動する(ディレクトリなければつくる)
# 引数がディレクトリだったら、ディレクトリ以下のファイルすべてを処理
def move_movie(file_path):
    return_log = []
    # arg check
    if os.path.isdir(file_path):
        for filename in pathlib.Path(file_path).glob('*.*'):
            function_log = move_movie_proc(filename)
            return_log.append(function_log)
    else:
        function_log = move_movie_proc(file_path)
        return_log.append(function_log)

    return '\n'.join(return_log)


# 動画移動のメイン処理
def move_movie_proc(file_path):
    return_log = []
    # make rename list
    renamelist = make_rename_list()
    # move file
    for name in renamelist:
        name_j = name[1]
        name_j_exp = name[1].replace('(', '\(').replace(')', '\)')
        if re.search(r'' + name_j_exp, pathlib.Path(file_path).name):
            parent_dir = pathlib.Path(file_path).parent
            dst_dirs = list(parent_dir.glob(f'*{name_j}'))
            dst_dir = ''
            td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
            if len(dst_dirs) == 1:
                dst_dir = dst_dirs[0]
            elif len(dst_dirs) == 0:
                log_str = f'directory not found. makedir {name_j}'
                return_log.append(f'{td} {log_str}')
                print(log_str)
                dst_dir = f'{str(parent_dir)}/{name_j}'
                os.makedirs(dst_dir)
            else:
                log_str = f'directory so many. {name_j}'
                return_log.append(f'{td} {log_str}')
                print(log_str)
                exit(1)

            log_str = f'move file: {str(file_path)} -> {str(dst_dir)}'
            td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
            return_log.append(f'{td} {log_str}')
            print(log_str)
            shutil.move(str(file_path), str(dst_dir))

    return '\n'.join(return_log)


# 文字列カット(指定バイト数より多い場合文字単位で削除)
def truncate(in_str, num_bytes, encoding='utf-8'):
    while len(in_str.encode(encoding)) > num_bytes:
        in_str = in_str[:-1]
    return in_str


# トレント栽培
def torrent_download(filepath, slack_channel='bot-open'):
    os.chdir(filepath)
    seedlist = glob.glob('*.torrent')
    return_log = []
    if len(seedlist) == 0:
        log_str = f'seed file not found: {filepath}'
        td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
        return_log.append(f'{td} {log_str}')
        return '\n'.join(return_log)

    post_msg='swirhen.tv seed download start:\n' \
             '```' + '\n'.join(seedlist) + '```'
    multi_post(slack_channel, post_msg)
    td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
    return_log.append(f'{td} {post_msg.replace("`", "")}')

    proc = subprocess.Popen('aria2c --listen-port=38888 --max-upload-limit=500K --seed-time=0 --enable-http-pipelining=true --on-download-complete=exit *.torrent', shell=True)
    time.sleep(10)

    # TODO 時間測定して、6時間以上経っていたら停めてしまうタイムアウト処理
    # aria2が残っているものに関してダウンロードフラグを戻す処理などが必要？
    while True:
        if len(glob.glob(f'{filepath}/*.aria2')) == 0:
            proc.kill()
            break

        time.sleep(10)

    # seeds backup
    for seedfile in seedlist:
        if not os.path.isfile(f'{SEED_BACKUP_DIR}/{seedfile}'):
            shutil.move(seedfile, SEED_BACKUP_DIR)
        else:
            os.remove(seedfile)

    post_msg='swirhen.tv seed download completed.'
    multi_post(slack_channel, post_msg)
    td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
    return_log.append(f'{td} {post_msg}')

    return '\n'.join(return_log)


# 動画エンコード
# ディレクトリ内の動画をエンコードし、完了都度フィード生成し、つぶやく(twitterとslack)
def encode_movie_in_directory(input_dir, output_dir):
    return_log = []

    for filename in pathlib.Path(input_dir).glob(f'*話*.*'):
        td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
        # 移動先のファイルチェック
        dstlist = glob.glob(f'{output_dir}/{filename.name}.mp4')
        if len(dstlist) > 0:
            multi_post('bot-open', f'@channel 【error】{filename.name}.mp4 が出力先に既に存在しているため、エンコードをスキップしました')
            continue
        
        return_log.append(f'{td} movie encode start: {filename.name}.mp4')
        encode_movie_proc(str(filename), output_dir)
        time.sleep(3)
        make_feed(output_dir)
        multi_post('bot-open', f'【publish】{filename.name}.mp4')
        td = dt.now().strftime('%Y/%m/%d-%H:%M:%S')
        return_log.append(f'{td} movie encode complete: {filename.name}.mp4')

    return '\n'.join(return_log)


# 動画エンコードのメイン処理
def encode_movie_proc(file_path, output_dir, tmpdir='/data/tmp'):
    file_name = pathlib.Path(file_path).name
    if os.path.exists(f"{tmpdir}/{file_name}.mp4"):
        os.remove(f"{tmpdir}/{file_name}.mp4")
    encode_arg = '-s "960x540" -b:v 1500k -vcodec libx264 -trellis 2 -bf 3 -b_strategy 1 -bidir_refine 1 -crf 25 -g 240 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -sc_threshold 65 -keyint_min 3 -nr 100 -qmin 12 -sn -partitions parti4x4+partp4x4+partp8x8 -f mp4 -coder 1 -movflags faststart -acodec aac -ac 2 -ar 48000 -b:a 128k -async 100 -threads 0'
    subprocess.run(f'/usr/bin/wine ffmpeg3.exe -i "{str(file_path)}" {encode_arg} "{tmpdir}/{file_name}.mp4"', shell=True)
    shutil.move(f'{tmpdir}/{file_name}.mp4', output_dir)


# しゅにるスクリプト呼び出し フィード作成(最近のアニメ)
def make_feed(target_dir):
    subprocess.run(f'{RUBY_PATH} {SCRIPT_DIR}/../mkpodcast.rb -t "{target_dir}/*.*" -b "http://swirhen.tv/movie/pspmp4/" -o "{target_dir}/index.xml" --title "最近のアニメ"', shell=True)
    db.make_feed_data('index')


# しゅにるスクリプト呼び出し フィード作成(任意のディレクトリ、タイトル)
def make_feed_manually(target_dir, title):
    target_dir_not_parent_dir = pathlib.Path(target_dir).name
    subprocess.run(f'{RUBY_PATH} {SCRIPT_DIR}/../mkpodcast.rb -t "{target_dir}/*.*" -b "http://swirhen.tv/movie/pspmp4/{target_dir_not_parent_dir}/" -o "{target_dir}.xml" --title "{title}"', shell=True)
    db.make_feed_list_data()
    db.make_feed_data(target_dir_not_parent_dir)


# get swirhentv feed file list
def get_feed_xml_list():
    xml_infos = []
    feed_infos = subprocess.run(f'rg title "{FEED_XML_DIR}/"*.xml -m 1 | sed "s/\(.*\.xml\).*>\(.*\)<.*/\\1|\\2/"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip().splitlines()
    for feed_info in feed_infos:
        xml_file = feed_info.split('|')[0]
        xml_name = xml_file.replace(f'{FEED_XML_DIR}/', '')[:-4]
        xml_title = feed_info.split('|')[1]
        xml_infos.append([xml_name, xml_title, xml_file])
    return xml_infos


# swirhentv feed search(sqlite)
def feed_search(argument):
    conn = sqlite3.connect(FEED_DB)
    cur = conn.cursor()
    result = []
    xml_list = list(cur.execute('select * from feed'))
    hit_flag = False
    hit_name = ''
    for xml_info in xml_list:
        xml_name = xml_info[0]
        xml_title = xml_info[1]
        if argument == xml_name:
            hit_flag = True
            hit_name = xml_name
            result.append('1')
            result.append([xml_title, f'{SWIRHENTV_URI}{xml_name}.xml'])
            break
        elif argument == xml_title:
            hit_flag = True
            hit_name = xml_name
            result.append('2')
            result.append([xml_title, f'{SWIRHENTV_URI}{xml_name}.xml'])
            break

    if hit_flag:
        feed_list = list(cur.execute(f'select title from feed_data where name = "{hit_name}" limit 10'))
        conn.close()
        for feed in feed_list:
            result.append(feed[0])
    else:
        temp_list = []
        feeds = list(cur.execute('select f.title, d.name, count(d.name)'
        ' from feed_data d, feed f'
        f' where d.title like "%{argument}%"'
        ' and d.name = f.name'
        ' group by d.name'))
        conn.close()
        if len(feeds) > 0:
            for feed in feeds:
                temp_list.append([feed[0], str(feed[2]), f'{SWIRHENTV_URI}{feed[1]}.xml'])

        if len(temp_list) > 0:
            result.append('3')
            result.extend(temp_list)

    return result


# radiko & agqr 録画予約
def record_reserver(year='', mon='', day='', hour='', minutes='', rec_time='', program_name='', station='', video_flag=False):
    if year == '':
        # 引数がない場合は予約リストを返す
        result = []
        joblist = subprocess.run('atq | awk \'{print $1"|"$2,$3,$4,$5,$6}\'', shell=True, stdout=subprocess.PIPE).stdout.decode().splitlines()
        for jobinfo in joblist:
            jobnum = jobinfo.split('|')[0]
            jobdate = dt.strptime(jobinfo.split('|')[1], '%a %b %d %H:%M:%S %Y')
            jobcommand = subprocess.run(f'at -c {jobnum} | tail -2 | head -1', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
            result.append([jobnum, jobdate, jobcommand])
        return result
    elif year == 'd':
        deljob_info = []
        # 年に'd'と入ってきた場合は削除モード。2個目の引数をjob番号にして削除する
        joblist = subprocess.run('atq | awk \'{print $1"|"$2,$3,$4,$5,$6}\'', shell=True, stdout=subprocess.PIPE).stdout.decode().splitlines()
        for jobinfo in joblist:
            jobnum = jobinfo.split('|')[0]
            if jobnum == mon:
                jobdate = dt.strptime(jobinfo.split('|')[1], '%a %b %d %H:%M:%S %Y')
                jobcommand = subprocess.run(f'at -c {jobnum} | tail -2 | head -1', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
                deljob_info = [jobnum, jobdate, jobcommand]
                break
        if len(deljob_info) != 0:
            ret = subprocess.run(f'at -d {mon}', shell=True).returncode
            if ret == 0:
                return deljob_info
            else:
                return f'unknown error. jobid {mon} not delete'
        else:
            return f'jobid {mon} is not found. not delete'
    else:
        # 引数がある場合は予約する
        reccommand = ''
        if station == 'agqr':
            mode_str = 'a'
            rec_offset = '30'
            video_flag_str = ''
            real_rec_time = rec_time
            if video_flag:
                video_flag_str = ' v'
            reccommand = f'python /data/share/movie/sh/radio_record.py {mode_str} "{program_name}" {rec_offset} {real_rec_time}{video_flag_str}'
        else:
            mode_str = 'r'
            res = get_station_id_and_name(station)
            if len(res) == 0:
                return 'station id cannot get'
            station_id = res[0]
            rec_offset = '1'
            real_rec_time = str(int(rec_time) + 30)
            reccommand = f'python /data/share/movie/sh/radio_record.py {mode_str} "{program_name}" {rec_offset} {real_rec_time} {station_id}'
        ret = subprocess.run(f'echo "{reccommand}" | at "{hour}:{minutes} {year}-{mon}-{day}"', shell=True, stderr=subprocess.PIPE)
        if ret.returncode == 0:
            jobnum = ret.stderr.decode().splitlines()[1].split()[1]
            jobdate = dt.strptime(f'{year}/{mon}/{day} {hour}:{minutes}', '%Y/%m/%d %H:%M')
            return [jobnum, jobdate, reccommand]
        else:
            return ret.stderr.decode().strip()


# 放送局名<->放送局ID相互取得
def get_station_id_and_name(station_id_or_name):
    radiko_station_info_list = subprocess.run('curl http://radiko.jp/v3/program/now/JP8.xml | rg "station id" -A 1 | rg -v "\-\-" | sed "s/.*<.*>\\(.*\\)<\\/.*>/\\1/" | sed "s/.*=\\"\\(.*\\)\\">/\\1|/g" | sed -z "s/|\\n/|/g"', shell=True, stdout=subprocess.PIPE).stdout.decode().splitlines()
    result = []
    for station_info in radiko_station_info_list:
        station_id = station_info.split('|')[0]
        station_name = station_info.split('|')[1]
        if station_id_or_name == station_id or \
            re.search(station_id_or_name, station_name) or \
            station_id_or_name == station_name:
            result = [station_id, station_name]
            break
    return result
