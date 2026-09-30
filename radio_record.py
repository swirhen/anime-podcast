#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# radiko 予約録音用スクリプト
# require: ffmpeg(なるべくあたらしめのやつ), ffprobe, grep, sed
# usage: python radio_record.py [動作モード] [番組名] [開始オフセット] [録音時間] [放送局ID] (隔週フラグファイル名)
# 動作モードr : 【放送局名】番組名_YYYYMMDD_HHMM.m4a というファイルになる
# 動作モードcr : radikoの録音チェック 10秒取得し異常が無いかチェックする
# 動作モードcrl : radikoの地域チェック 地域情報を取得し変化がないかチェックする
# cr のとき、第2引数に何か文字列が設定された場合は強制チェック報告する(定時報告用)
# 開始オフセット: sec
# 録音時間: sec
# 隔週フラグファイル名:
#     フラグファイルがあるかどうかチェックして、なければ作成だけして録音しない
#     あれば削除して録音する
# import section
import base64
import secrets
import shutil
import os
import pathlib
import sys
import subprocess
import time
import urllib.request
from datetime import datetime as dt, timedelta
import xml.etree.ElementTree as elementTree
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir / 'python-lib'))
import swirhentv_util as swiutil

# argument section
SCRIPT_DIR = str(current_dir)
OUTPUT_PATH = f'{SCRIPT_DIR}/../98 PSP用/agqr'
TMP_PATH = f'{OUTPUT_PATH}/flv'
FLG_PATH = f'{OUTPUT_PATH}/flg'
RADIKO_PROGRAM_INFO_URI = 'http://radiko.jp/v3/program/now/JP8.xml'
RADIKO_LOCATION_INFO_FILE = f'{SCRIPT_DIR}/loc_radiko'
SLACK_CHANNEL = 'bot-open'
RADIKO_AUTH_KEY = 'bcd151073c03b352e1ef2fd66c32209da9ca0afa'
RADIKO_AUTH_HEADERS = {
    'X-Radiko-App': 'pc_html5',
    'X-Radiko-App-Version': '0.0.1',
    'X-Radiko-User': 'dummy_user',
    'X-Radiko-Device': 'pc',
}


# radiko 認証。(トークン, 判定地域) を返す。失敗時は ('', '')
def radiko_authenticate():
    try:
        req = urllib.request.Request('https://radiko.jp/v2/api/auth1', headers=RADIKO_AUTH_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as res:
            token = res.headers['X-Radiko-AuthToken']
            offset = int(res.headers['X-Radiko-KeyOffset'])
            length = int(res.headers['X-Radiko-KeyLength'])
        partial_key = base64.b64encode(RADIKO_AUTH_KEY[offset:offset + length].encode()).decode()

        headers = {**RADIKO_AUTH_HEADERS, 'X-Radiko-AuthToken': token, 'X-Radiko-PartialKey': partial_key}
        req = urllib.request.Request('https://radiko.jp/v2/api/auth2', headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            area = res.read().decode().strip()
    except Exception as e:
        print(e)
        return '', ''
    return token, area


# ライブ配信のプレイリストURL(lsidはセッション識別用のランダム値)
def radiko_stream_url(station_id):
    return f'https://si-f-radiko.smartstream.ne.jp/so/playlist.m3u8?station_id={station_id}&l=15&lsid={secrets.token_hex(16)}&type=b'


# radiko check
def radiko_check(check_option):
    # 仮に文化放送とする
    radikostreamurl = radiko_stream_url('QRR')
    radikostreamtoken, _ = radiko_authenticate()

    temp_file = f'{TMP_PATH}/radiko_rec_temp.m4a'

    if os.path.exists(temp_file):
        os.remove(temp_file)

    radiko_record('10', temp_file, radikostreamurl, radikostreamtoken)

    if os.path.isfile(temp_file):
        if check_option != '':
            swiutil.discord_post(SLACK_CHANNEL, '【Radiko チェック 定時報告】録画URLは有効です')
    else:
        swiutil.discord_post(SLACK_CHANNEL, f'【Radiko チェック】HLSでの録画に失敗しました: {radikostreamurl}')

    if os.path.exists(temp_file):
        os.remove(temp_file)

    exit(0)


def write_location_info(location_info):
    with open(RADIKO_LOCATION_INFO_FILE, 'w', encoding='utf-8') as file:
        file.write(f'{location_info}\n')


# radiko location check
def radiko_location_check():
    _, location_info = radiko_authenticate()

    if location_info == '':
        swiutil.discord_post(SLACK_CHANNEL, '@channel 【radiko 地域判定チェック】判定地域が取得できませんでした')
        exit(0)

    location_info_from_file = ''
    if os.path.isfile(RADIKO_LOCATION_INFO_FILE):
        with open(RADIKO_LOCATION_INFO_FILE, encoding='utf-8') as file:
            lines = file.read().splitlines()
            location_info_from_file = lines[0].strip() if lines else ''

    if location_info_from_file == '':
        # 初回は比較対象が無いので、現在の地域を基準として保存するだけにする
        write_location_info(location_info)
    elif location_info != location_info_from_file:
        swiutil.discord_post(SLACK_CHANNEL, f'@channel 【radiko 地域判定チェック】判定地域が変更されました: {location_info}')
        write_location_info(location_info)

    exit(0)


# radiko record
def radiko_record(rec_time, output_file, stream_url, stream_token):
    # radikoはRangeヘッダー付きだとプレイリストの代わりに"200 OK"だけを返すため、http_seekable/seekableで無効化する
    cmd = ['ffmpeg', '-y', '-loglevel', 'warning',
           '-headers', f'X-Radiko-Authtoken: {stream_token}\r\n',
           '-http_seekable', '0', '-seekable', '0',
           '-i', stream_url, '-c', 'copy', '-t', str(rec_time), output_file]
    try:
        subprocess.run(cmd, timeout=int(rec_time) + 60)
    except subprocess.TimeoutExpired:
        pass


def get_duration(file):
    if not os.path.isfile(file):
        return 0
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=duration', '-of', 'csv=p=0', file], capture_output=True, text=True)
    try:
        return int(float(result.stdout.strip()))
    except ValueError:
        return 0


# main section
if __name__ == '__main__':
    args = sys.argv
    for path in (OUTPUT_PATH, TMP_PATH, FLG_PATH):
        os.makedirs(path, exist_ok=True)

    if len(args) > 1:
        check_opt = ''
        if len(args) == 3:
            check_opt = args[2]

        if args[1] == 'cr':
            radiko_check(check_opt)
        elif args[1] == 'crl':
            radiko_location_check()

    if len(args) < 6 or len(args) > 7 or args[1] != 'r':
        print(f'usage: {args[0]} r [program_name] [start_offset] [record_time] [station_id] (skip_flag_filename)')
        exit(1)

    program_name = args[2]
    start_offset = args[3]
    record_time = args[4]
    station_id = args[5]
    skip_flag_filename = args[6] if len(args) == 7 else ''

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

    operation_str = 'Radiko'
    station_name = ''
    program_name_from_api = ''

    # エリアチェック(ここで得たトークンは最初の録音に使う)
    stream_token, location_info = radiko_authenticate()
    location_area = location_info[0:4]
    if location_area != 'JP8,':
        post_str = f'【{operation_str}自動保存】エリア判定が現在茨城県(JP8)以外のため、番組が取得出来ない可能性があります。ご確認ください\n' \
                   f'現在のエリア:{location_info}'
        swiutil.discord_post(SLACK_CHANNEL, post_str)

    # 放送局IDから放送局名を取得現在放送中番組名を取得
    req = urllib.request.Request(RADIKO_PROGRAM_INFO_URI)
    try:
        with urllib.request.urlopen(req) as response:
            xml_string = response.read()
            if xml_string.startswith(b'\x1f\x8b'):
                import gzip
                xml_string = gzip.decompress(xml_string)
    except Exception as e:
        print(e)
    else:
        xml_root = elementTree.fromstring(xml_string)
        for station in xml_root.findall('./stations/station'):
            if station.attrib.get('id') == station_id:
                name_elem = station.find('name')
                if name_elem is not None and name_elem.text:
                    station_name = name_elem.text
                # 放送中と次の2番組が返るので、少し先の時刻を含む番組を選ぶ(開始直前に呼ばれても録音対象を取れるように)
                target_time = (tdatetime + timedelta(seconds=60)).strftime('%Y%m%d%H%M%S')
                for prog in station.findall('progs/prog'):
                    if prog.get('ft', '') <= target_time < prog.get('to', ''):
                        program_name_from_api = prog.findtext('title') or ''
                        break

    # 保存ファイル名(拡張子無し)
    filename_without_path = f'【{station_name}】{program_name}_{dt}'
    filename_with_path = f'{TMP_PATH}/{filename_without_path}'
    record_extent = 'm4a'

    # 開始ツイートリツイートよろぺこー
    swiutil.discord_post(SLACK_CHANNEL, f'【{operation_str}自動保存開始】{filename_without_path}')

    # 番組名バリデート
    if program_name_from_api == '':
        post_str = f'【{operation_str}自動保存】番組表apiから番組名が取得出来ませんでした。ご確認ください\n' \
                   f'from arg:{program_name}'
        swiutil.discord_post(SLACK_CHANNEL, post_str)
    elif program_name_from_api != program_name:
        post_str = f'【{operation_str}自動保存】番組表apiから取得した番組名と指定番組名が違っています。確認してください\n' \
                   f'from arg:{program_name}\n' \
                   f'from api:{program_name_from_api}'
        swiutil.discord_post(SLACK_CHANNEL, post_str)

    # 途中で途切れた場合は、残り時間ぶんを再認証して録り直し、最後に連結する
    parts = []
    rectime_remain = int(record_time)
    while rectime_remain >= 15:
        part_file = f'{filename_with_path}_{len(parts) + 1:02}.{record_extent}'
        if parts:
            stream_token, _ = radiko_authenticate()
        radiko_record(rectime_remain, part_file, radiko_stream_url(station_id), stream_token)
        duration = get_duration(part_file)
        if duration == 0:
            if os.path.exists(part_file):
                os.remove(part_file)
            break
        parts.append(part_file)
        rectime_remain -= duration

    output_file = f'{OUTPUT_PATH}/{filename_without_path}.{record_extent}'
    if not parts:
        swiutil.discord_post(SLACK_CHANNEL, f'【{operation_str}自動保存失敗】録音できませんでした: {filename_without_path}')
        exit(1)
    elif len(parts) == 1:
        shutil.move(parts[0], output_file)
    else:
        concat_list_file = f'{filename_with_path}_list.txt'
        with open(concat_list_file, 'w', encoding='utf-8') as f:
            for part in parts:
                escaped = part.replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")
        result = subprocess.run(['ffmpeg', '-y', '-loglevel', 'warning', '-f', 'concat', '-safe', '0', '-i', concat_list_file, '-c', 'copy', output_file])
        if result.returncode != 0:
            # 分割ファイルは手動回収できるよう一時フォルダに残す
            if os.path.exists(output_file):
                os.remove(output_file)
            swiutil.discord_post(SLACK_CHANNEL, f'【{operation_str}自動保存失敗】連結に失敗しました。分割ファイルは {TMP_PATH} に残しています: {filename_without_path}')
            exit(1)
        for file in [*parts, concat_list_file]:
            os.remove(file)

    # rssフィード生成
    swiutil.make_feed_manually(OUTPUT_PATH, '超！A&G(+α)')

    # 終了ツイート
    swiutil.discord_post(SLACK_CHANNEL, f'【{operation_str}自動保存終了】{filename_without_path}')
