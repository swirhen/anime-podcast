#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 超A&G / radiko 予約録画用スクリプト
# require: ffmpeg,いろいろ
# usage: python radio_record.py [動作モード(a or r)] [番組名] [開始オフセット] [録画時間] (動画フラグ or 放送局ID) (隔週フラグファイル名)
# 動作モードa (agqr)の場合 : YYYYMMDD_HHMM_番組名.mp4(mp3) というファイルになる
# 動作モードr (radiko)の場合 : 【放送局名】番組名_YYYYMMDD_HHMM.m4a というファイルになる
# 開始オフセット: sec
# 録画時間: sec
# 動画フラグ(radikoモードでは放送局ID): vなら映像付き、それ以外なら音声と見なしてエンコする
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
import xml.etree.ElementTree as elementTree
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swiutil
import radikoauth

# argments section
SCRIPT_DIR = str(current_dir)
OUTPUT_PATH = SCRIPT_DIR + '/../98 PSP用/agqr'
TMP_PATH = OUTPUT_PATH + '/flv'
FLG_PATH = OUTPUT_PATH + '/flg'
AGQR_STREAM_URI_FILE = SCRIPT_DIR + '/m3u8_url'
AGQR_STREAM_URI = open(AGQR_STREAM_URI_FILE).read().splitlines()[0]
AGQR_VALIDATE_API_URI = 'https://agqr.sun-yryr.com/api/now'
RADIKO_PROGRAM_INFO_URI = 'http://radiko.jp/v3/program/now/JP8.xml'
RADIKO_STREAM_URI = ''
RADIKO_STREAM_TOKEN = ''
OPERATION_STR=''
SLACK_CHANNEL = 'bot-open'
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
}


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) < 5 or len(args) > 7:
        print(f'usage: {args[0]} [operation_mode] [program_name] [start_offset] [record_time] [video_flag or station_id] (skip_flag_filename)')
        exit(1)

    operation_mode = ''
    program_name = ''
    start_offset = 0
    record_time = 0
    video_flag = 'a'
    station_id = ''
    skip_flag_filename = ''

    if len(args) > 4:
        operation_mode = args[1]
        program_name = args[2]
        start_offset = args[3]
        record_time = args[4]
        if len(args) > 5:
            if operation_mode == 'a':
                video_flag = args[5]
            else:
                station_id = args[5]
            if len(args) == 7:
                skip_flag_filename = args[6]

    # オフセット
    time.sleep(int(start_offset))

    # TODO 隔週対応(いまないのであとでいい)

    # 日付時刻
    tdatetime = dt.now()
    dt = tdatetime.strftime('%Y%m%d_%H%M')

    # 保存ファイル名、処理名、RadikoはURL取得
    xml_root = ''
    station_name = ''
    program_name_from_api = ''
    record_extent = ''
    if operation_mode == 'a':
        OPERATION_STR='超A&G'
        # 現在放送中番組名を取得
        req = urllib.request.Request(url=AGQR_VALIDATE_API_URI, headers=BROWSER_HEADERS)
        response = urllib.request.urlopen(req).read()
        json_data = json.loads(response)
        program_name_from_api = json_data['title']

        # ファイル名
        filename_without_path = dt + '_' + program_name
        filename_with_path = TMP_PATH + '/' + filename_without_path

        # 拡張子
        record_extent = 'mp4'
    else:
        OPERATION_STR='Radiko'
        # 現在放送中情報からIDで検索し、放送局名取得
        req = urllib.request.Request(RADIKO_PROGRAM_INFO_URI)
        with urllib.request.urlopen(req) as response:
            xml_string = response.read()

        xml_root = elementTree.fromstring(xml_string)

        for station in xml_root.findall('./stations/station'):
            if station.attrib['id'] == station_id:
                station_name = station.find('name').text
                # 番組名も取得してしまう
                program_name_from_api = station.findall('progs/prog')[0].find('title').text

        # URIとtoken
        authinfo = radikoauth.main(station_id)
        RADIKO_STREAM_URI = authinfo[0]
        RADIKO_STREAM_TOKEN = authinfo[1]

        # ファイル名
        filename_without_path = f'【{station_name}】{program_name}_' + dt
        filename_with_path = TMP_PATH + '/' + filename_without_path

        # 拡張子
        record_extent = 'm4a'


    # 開始ツイートリツイートよろぺこー
    swiutil.tweeet(f'【{OPERATION_STR}自動保存開始】' + filename_without_path)
    swiutil.slack_post(SLACK_CHANNEL, f'【{OPERATION_STR}自動保存開始】' + filename_without_path)

    # 番組名バリデート(radiko側はメンションしない)
    mention = ''
    if operation_mode == 'a':
        mention = '@channel '

    if program_name_from_api == '':
        post_str = f'{mention}【{OPERATION_STR}自動保存】番組表apiから番組名が取得出来ませんでした。ご確認ください\n' + \
                   f'from arg:{program_name}'
        swiutil.slack_post(SLACK_CHANNEL, post_str)
    elif program_name_from_api != program_name:
        post_str = f'{mention}【{OPERATION_STR}自動保存】番組表apiから取得した番組名と指定番組名が違っています。確認してください\n' + \
                   f'from arg:{program_name}\n' + \
                   f'from api:{program_name_from_api}'
        swiutil.slack_post(SLACK_CHANNEL, post_str)

    # 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
    rectime_remain = record_time
    file_num = '01'
    while int(rectime_remain) > 0:
        filename_rec = f'{filename_with_path}{file_num}.{record_extent}'
        if operation_mode == 'a':
            ffmpeg_str = f'/usr/bin/wine ffmpeg3.exe -i "{AGQR_STREAM_URI}" -c copy -t {rectime_remain} "{filename_rec}"'
        else:
            ffmpeg_str = f'/usr/bin/wine ffmpeg3.exe -headers "X-Radiko-Authtoken:{RADIKO_STREAM_TOKEN}" -i "{RADIKO_STREAM_URI}" -c copy -t {rectime_remain} "{filename_rec}"'

        subprocess.run(ffmpeg_str, shell=True)

        duration = subprocess.run(f'ffprobe -i "{filename_rec}" -select_streams v:0 -show_entries stream=duration | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        rectime_remain = int(rectime_remain) - int(duration)

        # 録音ファイルが0秒 or 残り時間が15秒未満なら終わる
        if int(duration) == 0 or rectime_remain < 15:
            break

        # ファイル連番を増分
        file_num = str(int(file_num) + 1).zfill(2)

    # ファイルが複数ある場合、リストを作成し、連結
    filecount = len(list(pathlib.Path(TMP_PATH).glob(f'{filename_without_path}*.{record_extent}')))
    if filecount > 1:
        os.chdir(TMP_PATH)
        concat_list_file = f'list_{filename_without_path}'
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        for file in glob.glob(f'{filename_without_path}*.{record_extent}'):
            # ファイル名にスペースが含まれる場合、アンダースコアに変更してからリスト化する
            if re.search(' ', file):
                rename_file = file.replace(' ','_')
                shutil.move(file, rename_file)
                swiutil.writefile_append(concat_list_file, f'file {rename_file}')
            else:
                swiutil.writefile_append(concat_list_file, f'file {file}')

        # 連結
        subprocess.run(f'/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "{concat_list_file}" "{filename_without_path}.{record_extent}', shell=True)
        for file in open(concat_list_file).read().splitlines():
            os.remove(file)
    else:
        shutil.move(f'{filename_with_path}01.{record_extent}', f'{filename_with_path}.{record_extent}')

    # 映像付き指定ならば出力ディレクトリにコピー。音声のみ指定なら音声抽出
    if operation_mode == 'a':
        if video_flag == 'v':
            shutil.copy(f'{filename_with_path}.{record_extent}', OUTPUT_PATH)
        else:
            subprocess.run(f'/usr/bin/wine ffmpeg3.exe -i "{filename_with_path}.mp4" -acodec copy -map 0:1 "{OUTPUT_PATH}/{filename_without_path}.m4a"', shell=True)
    else:
        shutil.move(f'{filename_with_path}.{record_extent}', OUTPUT_PATH)

    # rssフィード生成
    swiutil.make_feed_manually(OUTPUT_PATH, '超！A&G(+α)')

    # 終了ツイート
    swiutil.tweeet(f'【{OPERATION_STR}自動保存終了】{filename_without_path}')
    swiutil.slack_post(SLACK_CHANNEL, f'【{OPERATION_STR}自動保存終了】{filename_without_path}')
