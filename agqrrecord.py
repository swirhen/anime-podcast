#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 超A&G予約録画用スクリプト
# require: ffmpeg,いろいろ
# usage: agqrrecord.sh [番組名] [開始オフセット] [録画時間] [動画フラグ] [隔週フラグファイル名]
# 番組名: YYYYMMDD_HHMM_番組名.mp4(mp3) というファイルになる
# 開始オフセット: sec
# 録画時間: sec
# 動画フラグ: vなら映像付き、それ以外なら音声と見なしてエンコする
# 隔週フラグファイル名:
#     フラグファイルがあるかどうかチェックして、なければ作成だけして録画しない
#     あれば削除して録画する
# import section
import json
import glob
import shutil
import os
import pathlib
import re
import sys
import subprocess
import time
import urllib.request
from datetime import datetime as dt
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swiutil

# argments section
SCRIPT_DIR = str(current_dir)
OUTPUT_PATH = SCRIPT_DIR + '/../98 PSP用/agqr'
TMP_PATH = OUTPUT_PATH + '/flv'
FLG_PATH = OUTPUT_PATH + '/flg'
STREAM_URI_FILE = SCRIPT_DIR + '/m3u8_url'
STREAM_URI = open(STREAM_URI_FILE).read().splitlines()[0]
VALIDATE_API_URI = 'https://agqr.sun-yryr.com/api/now'
SLACK_CHANNEL = 'bot-open'
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
}


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4 or len(args) > 6:
        print('usage: ' + args[0] + ' [program_name] [start_offset] [record_time] (video_flag) (skip_flag_filename)')
        exit(1)

    program_name = ''
    start_offset = 0
    record_time = 0
    video_flag = 'a'
    skip_flag_filename = ''

    if len(args) > 3:
        program_name = args[1]
        start_offset = args[2]
        record_time = args[3]
        if len(args) > 4:
            video_flag = args[4]
            if len(args) == 6:
                skip_flag_filename = args[5]

    # オフセット
    time.sleep(int(start_offset))

    # TODO 隔週対応(いまないのであとでいい)

    # 日付時刻
    tdatetime = dt.now()
    dt = tdatetime.strftime('%Y%m%d_%H%M')

    # 保存ファイル名
    filename_without_path = dt + '_' + program_name
    filename = TMP_PATH + '/' + filename_without_path

    # 開始ツイートリツイートよろぺこー
    swiutil.tweeet('【超A&G自動保存開始】' + filename_without_path)
    swiutil.slack_post('【超A&G自動保存開始】' + filename_without_path)

    # 番組名バリデート
    req = urllib.request.Request(url=VALIDATE_API_URI, headers=BROWSER_HEADERS)
    response = urllib.request.urlopen(req).read()
    json_data = json.loads(response)
    now_onair_title = json_data['title']
    if now_onair_title == '':
        post_str = '@channel 【超A&G自動保存】番組表apiから番組名が取得出来ませんでした。ご確認ください\n' + \
                    'from arg:' + program_name
        swiutil.slack_post(SLACK_CHANNEL, post_str)
    elif now_onair_title != program_name:
        post_str = '@channel 【超A&G自動保存】番組表apiから取得した番組名と指定番組名が違っています。確認してください\n' + \
                   'from arg:' + program_name + '\n' + \
                   'from api:' + now_onair_title
        swiutil.slack_post(SLACK_CHANNEL, post_str)

    # 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
    rectime_remain = record_time
    file_num = '01'
    while rectime_remain > 0:
        filename_rec = filename + file_num + '.mp4'
        subprocess.run('/usr/bin/wine ffmpeg3.exe -i "' + STREAM_URI + '" -c copy -t ' + rectime_remain + ' "' + filename_rec + '"', shell=True)
        duration = subprocess.run('ffprobe -i "' + filename_rec + '" -select_streams v:0 -show_entries stream=duration | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        rectime_remain = int(rectime_remain) - int(duration)

        # 録音ファイルが0秒 or 残り時間が15秒未満なら終わる
        if int(duration) == 0 or rectime_remain < 15:
            break

        # ファイル連番を増分
        file_num = str(int(file_num) + 1).zfill(2)

    # ファイルが複数ある場合、リストを作成し、連結
    filecount = len(list(pathlib.Path(TMP_PATH).glob(filename_without_path + '*.mp4')))
    if filecount > 1:
        os.chdir(TMP_PATH)
        concat_list_file = 'list_' + filename_without_path
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        for file in glob.glob(filename_without_path + '*.mp4'):
            # ファイル名にスペースが含まれる場合、アンダースコアに変更してからリスト化する
            if re.search(' ', file):
                rename_file = file.replace(' ','_')
                shutil.move(file, rename_file)
                swiutil.writefile_append(concat_list_file, rename_file)
            else:
                swiutil.writefile_append(concat_list_file, file)

        # 連結
        subprocess.run('/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "' + concat_list_file + '" "' + filename_without_path + '.mp4', shell=True)
    else:
        shutil.move(filename_without_path + '01.mp4', filename_without_path + '.mp4')

    # 映像付き指定ならば出力ディレクトリにコピー。音声のみ指定なら音声抽出
    if video_flag == 'v':
        shutil.copy(filename_without_path + '.mp4', OUTPUT_PATH)
    else:
        subprocess.run('/usr/bin/wine ffmpeg3.exe -i "' + filename_without_path + '.mp4" -acodec copy -map 0:1 "' + OUTPUT_PATH + '/' + filename_without_path + '.m4a', shell=True)

    # rssフィード生成
    swiutil.make_feed_manually(OUTPUT_PATH, '超！A&G(+α)')

    # 終了ツイート
    swiutil.tweeet('【超A&G自動保存終了】' + filename_without_path)
    swiutil.slack_post('【超A&G自動保存終了】' + filename_without_path)
