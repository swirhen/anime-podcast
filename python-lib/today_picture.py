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

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
RECENT_LIST = f'{SCRIPT_DIR}/today_picture_recent.txt'
PIC_DIR = '/data/share/temp/wallpaper*'
CHANNEL = 'ztb_today_pic'
# CHANNEL = 'bot-open'


def choice_the_picture(urlflag=False):
    fileset = set(subprocess.run(f'find {PIC_DIR} -type f -newermt "2021-01-01"', shell=True, stdout=subprocess.PIPE).stdout.decode().strip().splitlines())
    recent_filelist = []
    if os.path.exists(RECENT_LIST):
        with open(RECENT_LIST) as file:
            recent_filelist = file.read().splitlines()
    choiced_file_path = random.choice(list(fileset - set(recent_filelist)))

    if urlflag:
        return choiced_file_path.replace('/data', 'http://swirhen.tv')
    else:
        return (recent_filelist[-29:] + [choiced_file_path])


def reply_url_the_picture():
    fileurl = choice_the_picture(True)
    reply_text = '画像おみくじ　ぬん₍₍ ◝((๑╹ᆺ╹))◟ ⁾⁾ぬん\n' \
                '(すいれん.tv のとあるディレクトリから画像をランダムに抽出)\n' \
                f'{fileurl}'
    return reply_text


def upload_the_picture():
    filelist = choice_the_picture()
    swiutil.discord_post(CHANNEL, 'どどんどどんどんどん！\n'
                        'きょうの一枚はこれだ！\n'
                        f'{filelist[-1].replace("/data", "http://swirhen.tv")}')
    # swiutil.discord_upload(CHANNEL, filelist[-1])
    with open(RECENT_LIST, mode='w') as file:
        file.write('\n'.join(filelist))


if __name__ == '__main__':
    upload_the_picture()
