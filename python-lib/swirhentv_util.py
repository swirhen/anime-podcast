#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv python library
import glob
import os
import pathlib
import re
import shutil
import subprocess
import urllib.request
import sys
import time

from bs4 import BeautifulSoup
from slacker import Slacker
import slackbot_settings

current_dir = pathlib.Path(__file__).resolve().parent
CHECKLIST_FILE_PATH = str(current_dir) + '/../checklist.txt'
SYOBOCAL_URI = 'http://cal.syoboi.jp/find?sd=0&kw='
SCRIPT_DIR = str(current_dir)
SEED_BACKUP_DIR = SCRIPT_DIR + '/download_seeds'


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
    subprocess.run('/usr/bin/php /home/swirhen/tiasock/tiasock.php "' + channel + '" "' + text + '"', shell=True)


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


# grep(完全一致)
def grep_file(file_path, word):
    with open(file_path, 'r', newline='') as f:
        lines = f.readlines()

    for line in lines:
        if line.strip() == word:
            return line.strip()


# grep(配列)
def grep_list(greplist, word):
    for item in greplist:
        m = re.search(word, item)
        if m:
            return m.group()


# ファイル書き込み(新規)
def writefile_new(filepath, string):
    with open(filepath, 'w') as file:
        file.write(string + '\n')


# ファイル書き込み(追記)
def writefile_append(filepath, string):
    with open(filepath, 'a') as file:
        file.write(string + '\n')


# ファイルの行数を得る
def len_file(filepath):
    return len(open(filepath).readlines())


# キーワードの含まれる行を削除
def sed_del(filepath, sed_keyword):
    tempfile = filepath + '.sed_del_temp'
    if pathlib.Path(tempfile).is_file():
        os.remove(pathlib.Path(tempfile))
    lines_data = open(filepath).readlines()
    for line in lines_data:
        if not re.search(sed_keyword, line):
            writefile_append(tempfile, line.strip())

    shutil.move(tempfile, filepath)


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


# checklist.txtからチェックリストの配列を得る
# 書式は"最終更新日時 取得話数 英語タイトル名|日本語タイトル名
def make_check_list():
    check_lists = []
    try:
        listfile = open(CHECKLIST_FILE_PATH, 'r', encoding='utf-8')
    except Exception:
        print("open error. not found file: " + str(CHECKLIST_FILE_PATH))
        sys.exit(1)

    # make check list
    for line in listfile.readlines():
        if re.search('^Last Update', line):
            continue
        last_update = re.sub(r'^([^ ]+) ([^ ]+) (.*)', r'\1', line).strip()
        episode_number = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\2', line).strip()
        name = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).strip().split("|")[0]
        name_j = re.sub(r'^([^ ]*) ([^ ]*) (.*)', r'\3', line).strip().split("|")[1]
        check_list = [last_update, episode_number, name, name_j]
        check_lists.append(check_list)

    return check_lists


# checklist.txtの最後のセクションから、英語タイトル -> 日本語タイトルの変換リストを得る
def make_rename_list():
    # file open
    try:
        listfile = open(CHECKLIST_FILE_PATH, 'r', encoding='utf-8')
    except Exception:
        print("open error. not found file: ", str(CHECKLIST_FILE_PATH))
        sys.exit(1)

    # make rename list
    renamelist = []
    for line in listfile.readlines():
        if re.search('^Last Update', line):
            continue
        line = re.sub(r'^[^ ]+ [^ ]+ ', '', line)
        line = line.strip().split("|")
        renamelist.append(line)

    return renamelist


# 動画リネーム
# checklist.txtの後半(英語ファイル名|日本語ファイル名)のデータを使って動画ファイルをリネームする
# [英語ファイル名] -[SFX1][話数][SFX2](mp4 1280x720 aac).mp4
# -> [日本語ファイル名] 第[話数]話.mp4
# 第1引数: ディレクトリ(指定したディレクトリ以下のすべてのファイルをリネームする)
# 第2引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第3引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペース。
def rename_movie_file(file_path, separator1='\ ', separator2='\ '):
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
            exp = r'.*(' + name_e + ').*' + separator1 + '([0-9]{0,1}[0-9][0-9](.5)?)' + separator2 + '.*\.(.*)'
            name = re.sub(exp, r'\1', filename)
            num = re.sub(exp, r'\2', filename)
            ext = re.sub(exp, r'\4', filename)

            if name_e == name:
                if os.path.isfile(filename + '.aria2'):
                    print('#' + filename + ' 成育中！')
                else:
                    new_name = name_j + ' 第' + num + '話.' + ext
                    if file_path != new_name:
                        print('# rename ' + filename + ' -> ' + new_name)
                        os.rename(filename, new_name)
                    else:
                        print('# 変更後のファイル名が同じ')
                break


# 動画移動
# checklist.txtの後半(日本語ファイル名)のデータを使って動画ファイルを移動する
# 引数のファイルが一致する日本語ファイル名を同名のディレクトリに移動する(ディレクトリなければつくる)
# 引数がディレクトリだったら、ディレクトリ以下のファイルすべてを処理
def move_movie(file_path):
    # arg check
    if os.path.isdir(file_path):
        for filename in pathlib.Path(file_path).glob('*.mp4'):
            move_movie_proc(filename)
    else:
        move_movie_proc(file_path)


# 動画移動のメイン処理
def move_movie_proc(file_path):
    # make rename list
    renamelist = make_rename_list()
    # move file
    for name in renamelist:
        name_j = name[1]
        name_j_exp = name[1].replace('(', '\(').replace(')', '\)')
        if re.search(r'' + name_j_exp, pathlib.Path(file_path).name):
            parent_dir = pathlib.Path(file_path).parent
            dst_dirs = list(parent_dir.glob('*' + name_j))
            dst_dir = ''
            if len(dst_dirs) == 1:
                dst_dir = dst_dirs[0]
            elif len(dst_dirs) == 0:
                print('directory not found. makedir ' + name_j)
                dst_dir = str(parent_dir) + '/' + name_j
                os.makedirs(dst_dir)
            else:
                print('directory so many.' + name_j)
                exit(1)

            print('move file. ' + str(file_path) + ' -> ' + str(dst_dir))
            shutil.move(str(file_path), str(dst_dir))


# トレント栽培
def torrent_download(filepath, slack_channel='bot-open'):
    os.chdir(filepath)
    seedlist = glob.glob('*.torrent')
    return_log = []
    if len(seedlist) == 0:
        print('seed file not found: ' + filepath)
        return 1

    post_msg='swirhen.tv seed download start:\n' + \
             '```' + '\n'.join(seedlist) + '```'
    slack_post(slack_channel, post_msg)
    return_log.append(post_msg)

    proc = subprocess.Popen('aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent', shell=True)
    time.sleep(10)

    while True:
        if len(glob.glob(filepath + '/*.aria2')) == 0:
            proc.kill()
            break

        time.sleep(10)

    # seeds backup
    for seedfile in seedlist:
        if not os.path.isfile(SEED_BACKUP_DIR + '/' + seedfile):
            shutil.move(seedfile, SEED_BACKUP_DIR)
        else:
            os.remove(seedfile)

    post_msg='swirhen.tv seed download completed.'
    slack_post(slack_channel, post_msg)
    return_log.append(post_msg)

    return '\n'.join(return_log)


# 動画エンコード
# ディレクトリ内の動画をエンコードし、完了都度フィード生成し、つぶやく(twitterとslack)
# 全完了後、各作品ディレクトリへの移動処理
def encode_movie_in_directory(input_dir, output_dir):
    for filename in pathlib.Path(input_dir).glob('*話*.mp4'):
        encode_movie_proc(str(filename), output_dir)
        time.sleep(3)
        make_feed(output_dir)
        tweeet('【publish】' + filename.name + '.mp4')
        slack_post('bot-open', '【publish】' + filename.name + '.mp4')

    move_movie(input_dir)


# 動画エンコードのメイン処理
def encode_movie_proc(file_path, output_dir, tmpdir='/data/tmp'):
    file_name = pathlib.Path(file_path).name
    encode_arg = ' -s "960x540" -b:v 1500k -vcodec libx264 -trellis 2 -bf 3 -b_strategy 1 -bidir_refine 1 -crf 25 -g 240 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -sc_threshold 65 -keyint_min 3 -nr 100 -qmin 12 -sn -partitions parti4x4+partp4x4+partp8x8 -f mp4 -coder 1 -movflags faststart -acodec aac -ac 2 -ar 48000 -b:a 128k -async 100 -threads 0 '
    subprocess.run('/usr/bin/wine ffmpeg3.exe -i "' + str(file_path) + '"' + encode_arg + '"' + tmpdir + '/' + file_name + '.mp4"', shell=True)
    shutil.move(tmpdir + '/' + file_name + '.mp4', output_dir)


def make_feed(target_dir):
    subprocess.run(SCRIPT_DIR +  '/../mkpodcast.rb -t "' + target_dir + '/*.*" -b "http://swirhen.tv/movie/pspmp4/" -o "' + target_dir + '/index.xml" --title "最近のアニメ"', shell=True)


def make_feed_manually(target_dir, title):
    target_dir_not_parent_dir = pathlib.Path(target_dir).name
    subprocess.run(SCRIPT_DIR +  '/../mkpodcast.rb -t "' + target_dir + '/*.*" -b "http://swirhen.tv/movie/pspmp4/' + target_dir_not_parent_dir + '/" -o "' + target_dir + '.xml" --title "' + title + '"', shell=True)
