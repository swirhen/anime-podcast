# -*- coding: utf-8 -*-
# きょうのいちまい
# すいれんさんの待ち受け画像貯蔵ディレクトリ(2021年以降)から画像を1枚ランダムで表示する
# 直近30枚からは表示しない
# import section
import os
import subprocess
import random
import pathlib
import swirhentv_util as swiutil
from datetime import datetime as dt

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
RECENT_LIST = f'{SCRIPT_DIR}/today_picture_recent.txt'
RECENT_LIST_S = f'{SCRIPT_DIR}/today_picture_recent_s.txt'
PIC_DIR = '/data/share/temp/wallpaper*'
PIC_DIR_S = '/data/share/temp/nekomata_okazu'
CHANNEL = 'ztb_today_pic'


def choice_the_picture(urlflag=False, recent_list=RECENT_LIST, year=''):
    if year == '':
        pyear = str(int(dt.now().strftime('%Y')) - 1)
        fileset = set(subprocess.run(f'find {PIC_DIR} -type f -newermt "2020-12-31"', shell=True, stdout=subprocess.PIPE).stdout.decode().strip().splitlines())
    else:
        pyear = str(int(year) - 1)
        fileset = set(subprocess.run(f'find {PIC_DIR} -type f -newermt "2020-12-31" ! -newermt "{year}-12-31"', shell=True, stdout=subprocess.PIPE).stdout.decode().strip().splitlines())

    recent_filelist = []
    if os.path.exists(recent_list):
        with open(recent_list) as file:
            recent_filelist = file.read().splitlines()
    choiced_file_path = random.choice(list(fileset - set(recent_filelist)))

    if urlflag:
        return choiced_file_path.replace('/data', 'http://swirhen.tv')
    else:
        return (recent_filelist[-4000:] + [choiced_file_path])


def choice_the_picture_sensitive():
    fileset = set(subprocess.run(f'find {PIC_DIR_S} -type f ', shell=True, stdout=subprocess.PIPE).stdout.decode().strip().splitlines())

    recent_filelist = []
    if os.path.exists(RECENT_LIST_S):
        with open(RECENT_LIST_S) as file:
            recent_filelist = file.read().splitlines()
    choiced_file_path = random.choice(list(fileset - set(recent_filelist)))

    return (recent_filelist[-99:] + [choiced_file_path])


def reply_url_the_picture(year=''):
    if year != '':
        fileurl = choice_the_picture(True, 'dummy', year)
        app_str = f'({year}年のやつ)'
    else:
        fileurl = choice_the_picture(True, 'dummy')
        app_str = ''
    reply_text = f'画像おみくじ　ぬん₍₍ ◝((๑╹ᆺ╹))◟ ⁾⁾ぬん {app_str}\n' \
                '(すいれん.tv のとあるディレクトリから画像をランダムに抽出)\n' \
                f'{fileurl}'
    return reply_text


def today_picture_normal():
    filelist = choice_the_picture()
    swiutil.discord_post(CHANNEL, 'どどんどどんどんどん！ 画像ちゃん！\n'
                        f'{filelist[-1].replace("/data", "http://swirhen.tv")}')
    with open(RECENT_LIST, mode='w') as file:
        file.write('\n'.join(filelist))


def today_picture_sensitive():
    filelist = choice_the_picture_sensitive()
    with open(RECENT_LIST_S, mode='w') as file:
        file.write('\n'.join(filelist))
    reply_text = f'それはそれとして晩ごはんのおかずどうぞ～\n' \
                f'{filelist[-1].replace("/data", "http://swirhen.tv")}'
    return reply_text


if __name__ == '__main__':
    today_picture_normal()
