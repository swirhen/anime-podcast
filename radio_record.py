#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 超A&G / radiko 予約録画用スクリプト
# require: ffmpeg(なるべくあたらしめのやつ), ffprobe, grep, sed
# usage: python radio_record.py [動作モード] [番組名 or (テストオプション)] [開始オフセット] [録画時間] [(動画フラグ) or 放送局ID] (隔週フラグファイル名)
# 動作モードa (agqr)の場合 : YYYYMMDD_HHMM_番組名.mp4(m4a) というファイルになる
# 動作モードr (radiko)の場合 : 【放送局名】番組名_YYYYMMDD_HHMM.m4a というファイルになる
# 動作モードca : agqrの録音チェック 10秒取得し異常が無いかチェックする
# 動作モードcr : radikoの録音チェック 10秒取得し異常が無いかチェックする
# 動作モードcrl : radikoの地域チェック 地域情報を取得し変化がないかチェックする
# ca, cr, crlのとき、第2引数に何か文字列が設定された場合は強制チェック報告する(定時報告用)
# 開始オフセット: sec
# 録画時間: sec
# 動画フラグ(radikoモードでは放送局ID): vなら映像付き、それ以外(省略可)なら音声と見なしてエンコする
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
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil
import radikoauth

# argument section
SCRIPT_DIR = str(current_dir)
OUTPUT_PATH = f'{SCRIPT_DIR}/../98 PSP用/agqr'
TMP_PATH = f'{OUTPUT_PATH}/flv'
FLG_PATH = f'{OUTPUT_PATH}/flg'
#AGQR_STREAM_URI = 'http://ic-www.uniqueradio.jp/iphone/3G.m3u8'
AGQR_STREAM_URI = 'https://www.uniqueradio.jp/agapps/hls/cdn.m3u8'
AGQR_VALIDATE_API_URI = 'http://localhost:1234/api/now'
RADIKO_PROGRAM_INFO_URI = 'http://radiko.jp/v3/program/now/JP8.xml'
RADIKO_LOCATION_INFO_FILE = f'{SCRIPT_DIR}/loc_radiko'
with open(RADIKO_LOCATION_INFO_FILE) as file:
    RADIKO_LOCATION_INFO_FROM_FILE = file.read().splitlines()[0]
SLACK_CHANNEL = 'bot-open'


# agqr check
def agqr_check(check_option):
    temp_file = f'{TMP_PATH}/agqr_rec_temp.mp4'
    if os.path.exists(temp_file):
        os.remove(temp_file)

    agqr_record('10', temp_file)

    if os.path.isfile(temp_file):
        if check_option != '':
            swiutil.multi_post(SLACK_CHANNEL, '【超A&G チェック 定時報告】録画URLは有効です')
    else:
        swiutil.multi_post(SLACK_CHANNEL, f'【超A&G チェック】HLSでの録画に失敗しました: {AGQR_STREAM_URI}')

    if os.path.exists(temp_file):
        os.remove(temp_file)

    exit(0)


# radiko check
def radiko_check(check_option):
    # ストリームURIとtoken(仮に文化放送とする)
    authinfo = radikoauth.main('QRR')
    radikostreamurl = authinfo[0]
    radikostreamtoken = authinfo[1]

    temp_file = f'{TMP_PATH}/radiko_rec_temp.m4a'

    if os.path.exists(temp_file):
        os.remove(temp_file)

    radiko_record('10', temp_file, radikostreamurl, radikostreamtoken)

    if os.path.isfile(temp_file):
        if check_option != '':
            swiutil.multi_post(SLACK_CHANNEL, '【Radiko チェック 定時報告】録画URLは有効です')
    else:
        swiutil.multi_post(SLACK_CHANNEL, f'【Radiko チェック】HLSでの録画に失敗しました: {radikostreamurl}')

    if os.path.exists(temp_file):
        os.remove(temp_file)

    exit(0)


# radiko location check
def radiko_location_check():
    # 地域情報
    location_info = radikoauth.main()[0].strip()

    if location_info == '':
        swiutil.multi_post(SLACK_CHANNEL, '@channel 【radiko 地域判定チェック】判定地域が取得できませんでした')
    elif location_info != RADIKO_LOCATION_INFO_FROM_FILE:
        swiutil.multi_post(SLACK_CHANNEL, f'@channel 【radiko 地域判定チェック】判定地域が変更されました: {location_info}')
        swiutil.writefile_new(RADIKO_LOCATION_INFO_FILE, location_info)

    exit(0)


# agqr record
def agqr_record(rec_time, output_file):
    ffmpeg_str = f'/usr/bin/wine ffmpeg3.exe -i "{AGQR_STREAM_URI}" -c copy -t {rec_time} "{output_file}"'
    if rec_time == '10':
        p = subprocess.Popen(ffmpeg_str, shell=True)
        time.sleep(15)
        p.terminate()
        ffmpeg_pid = p.pid + 1
        p2 = subprocess.run(f'ps {ffmpeg_pid} | grep ffmpeg3 | wc -l', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        if int(p2.stdout) == 1:
            subprocess.run(f'kill {ffmpeg_pid}', shell=True)
    else:
        subprocess.run(ffmpeg_str, shell=True)


# radiko record
def radiko_record(rec_time, output_file, stream_url, stream_token):
    ffmpeg_str = f'/usr/bin/wine ffmpeg3.exe -headers "X-Radiko-Authtoken:{stream_token}" -i "{stream_url}" -c copy -t {rec_time} "{output_file}"'
    if rec_time == '10':
        p = subprocess.Popen(ffmpeg_str, shell=True)
        time.sleep(15)
        p.terminate()
        ffmpeg_pid = p.pid + 1
        p2 = subprocess.run(f'ps {ffmpeg_pid} | grep ffmpeg3 | wc -l', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        if int(p2.stdout) == 1:
            subprocess.run(f'kill {ffmpeg_pid}', shell=True)
    else:
        subprocess.run(ffmpeg_str, shell=True)


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        check_opt = ''
        if len(args) == 3:
            check_opt = args[2]

        if args[1] == 'ca':
            agqr_check(check_opt)
        elif args[1] == 'cr':
            radiko_check(check_opt)
        elif args[1] == 'crl':
            radiko_location_check()

    if len(args) < 5 or len(args) > 7:
        print(f'usage: {args[0]} [operation_mode] [program_name] [start_offset] [record_time] [(video_flag) or station_id] (skip_flag_filename)')
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

    if operation_mode == 'r' and station_id == '':
        print('Radikoモードの場合は放送局IDを指定してぺこ')
        print(f'usage: {args[0]} [operation_mode] [program_name or test_option] [start_offset] [record_time] [video_flag or station_id] (skip_flag_filename)')
        exit(1)

    # オフセット
    time.sleep(int(start_offset))

    # 隔週対応
    if skip_flag_filename != '':
        flg_filename_with_path = f'{FLG_PATH}/{skip_flag_filename}'
        if os.path.exists(flg_filename_with_path):
            os.remove(flg_filename_with_path)
        else:
            pathlib.Path(flg_filename_with_path).touch()
            exit(0)

    # 日付時刻
    tdatetime = dt.now()
    dt = tdatetime.strftime('%Y%m%d_%H%M')

    # 動作モードによる変数切り替え
    operation_str = ''
    station_name = ''
    program_name_from_api = ''
    record_extent = ''
    opt_str = ''
    mention = ''
    radiko_stream_url = ''
    radiko_stream_token = ''
    if operation_mode == 'a':
        operation_str = '超A&G'
        # 現在放送中番組名を取得
        # req = urllib.request.Request(url=AGQR_VALIDATE_API_URI)
        # try:
        #     response = urllib.request.urlopen(req).read()
        # except Exception as e:
        #     print(e)
        # else:
        #     if response != b'':
        #         json_data = json.loads(response)
        #         program_name_from_api = json_data['title']

        # 保存ファイル名(拡張子無し)
        filename_without_path = f'{dt}_{program_name}'
        filename_with_path = f'{TMP_PATH}/{filename_without_path}'

        # 一時保存拡張子
        record_extent = 'mp4'
        # 長さ取得の際のオプション文字列
        opt_str = 'v'
        # メンション文字列
        mention = '@channel '
    else:
        operation_str = 'Radiko'
        # エリアチェック
        location_info = radikoauth.main()[0].strip()
        location_area = location_info[0:4]
        if location_area != 'JP8,':
            post_str = f'【{operation_str}自動保存】エリア判定が現在茨城県(JP8)以外のため、番組が取得出来ない可能性があります。ご確認ください\n' \
                       f'現在のエリア:{location_info}'
            swiutil.multi_post(SLACK_CHANNEL, post_str)

        # 放送局IDから放送局名を取得現在放送中番組名を取得
        req = urllib.request.Request(RADIKO_PROGRAM_INFO_URI)
        try:
            with urllib.request.urlopen(req) as response:
                xml_string = response.read()
        except Exception as e:
            print(e)
        else:
            xml_root = elementTree.fromstring(xml_string)
            for station in xml_root.findall('./stations/station'):
                if station.attrib['id'] == station_id:
                    station_name = station.find('name').text
                    # 番組名取得(現在放送中xmlから取れるのは直近の2番組なので、1番目を取得)
                    # Radikoくんは放送時間ぴったりだと直前の番組が1番目になっているので、2番目を取るようにしてみる
                    program_name_from_api = station.findall('progs/prog')[1].find('title').text

        # ストリームURIとtoken
        auth_info = radikoauth.main(station_id)
        radiko_stream_url = auth_info[0]
        radiko_stream_token = auth_info[1]

        # 保存ファイル名(拡張子無し)
        filename_without_path = f'【{station_name}】{program_name}_{dt}'
        filename_with_path = f'{TMP_PATH}/{filename_without_path}'

        # 一時保存拡張子
        record_extent = 'm4a'
        # 長さ取得の際のオプション文字列
        opt_str = 'a'

    # 開始ツイートリツイートよろぺこー
    swiutil.multi_post(SLACK_CHANNEL, f'【{operation_str}自動保存開始】{filename_without_path}')

    # 番組名バリデート
    if operation_mode != 'a':
        if program_name_from_api == '':
            post_str = f'{mention}【{operation_str}自動保存】番組表apiから番組名が取得出来ませんでした。ご確認ください\n' \
                        f'from arg:{program_name}'
            swiutil.multi_post(SLACK_CHANNEL, post_str)
        elif program_name_from_api != program_name:
            post_str = f'{mention}【{operation_str}自動保存】番組表apiから取得した番組名と指定番組名が違っています。確認してください\n' \
                        f'from arg:{program_name}\n' \
                        f'from api:{program_name_from_api}'
            swiutil.multi_post(SLACK_CHANNEL, post_str)

    # 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
    rectime_remain = record_time
    file_num = '01'
    while int(rectime_remain) > 0:
        filename_rec = f'{filename_with_path}{file_num}.{record_extent}'
        if operation_mode == 'a':
            agqr_record(rectime_remain, filename_rec)
        else:
            radiko_record(rectime_remain, filename_rec, radiko_stream_url, radiko_stream_token)

        duration = subprocess.run(f'ffprobe -i "{filename_rec}" -select_streams {opt_str}:0 -show_entries stream=duration | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
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
        concat_files = []
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        for file in sorted(glob.glob(f'{filename_without_path}*.{record_extent}')):
            # ファイル名にスペースが含まれる場合、アンダースコアに変更してからリスト化する
            if re.search(' ', file):
                rename_file = file.replace(' ','_')
                shutil.move(file, rename_file)
                swiutil.writefile_append(concat_list_file, f'file {rename_file}')
                concat_files.append(rename_file)
            else:
                swiutil.writefile_append(concat_list_file, f'file {file}')
                concat_files.append(file)

        # 連結
        subprocess.run(f'/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "{concat_list_file}" "{filename_without_path}.{record_extent}"', shell=True)
        # post_str = 'jointed files:\n```' + '\n'.join(concat_files) + '```'
        # swiutil.multi_post(SLACK_CHANNEL, post_str)
        # 連結元ファイル削除
        for file in concat_files:
            os.remove(file)
    else:
        # ファイルが1つだった場合はリネームだけする
        shutil.move(f'{filename_with_path}01.{record_extent}', f'{filename_with_path}.{record_extent}')

    # (agqrモード)映像付き指定ならば出力ディレクトリにコピー。音声のみ指定なら音声抽出
    if operation_mode == 'a':
        if video_flag == 'v':
            shutil.copy(f'{filename_with_path}.{record_extent}', OUTPUT_PATH)
        else:
            subprocess.run(f'/usr/bin/wine ffmpeg3.exe -i "{filename_with_path}.{record_extent}" -acodec copy -map 0:1 "{OUTPUT_PATH}/{filename_without_path}.m4a"', shell=True)
    else:
        # Radikoモードは即時出力ディレクトリに移動
        shutil.move(f'{filename_with_path}.{record_extent}', OUTPUT_PATH)

    # rssフィード生成
    swiutil.make_feed_manually(OUTPUT_PATH, '超！A&G(+α)')

    # 終了ツイート
    swiutil.multi_post(SLACK_CHANNEL, f'【{operation_str}自動保存終了】{filename_without_path}')
