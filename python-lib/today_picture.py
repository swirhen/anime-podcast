# -*- coding: utf-8 -*-
# きょうのいちまい
# すいれんさんの待ち受け画像貯蔵ディレクトリ(2021年以降)から画像を1枚ランダムで表示する
# 直近30枚からは表示しない
# import section
import subprocess
import random
import pathlib
import swirhentv_util as swiutil

# argment section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
RECENT_LIST = f'{SCRIPT_DIR}/today_picture_recent.txt'
PIC_DIR = '/data/share/temp/wallpaper*'
CHANNEL = 'bot-open'
# CHANNEL = 'ztb_bot-sandbox'


def choice_the_picture(urlflag=False):
    fileset = set(subprocess.run(f'find {PIC_DIR} -type f -newermt "2021-01-01"', shell=True, stdout=subprocess.PIPE).stdout.decode().strip().splitlines())
    with open(RECENT_LIST) as file:
        recent_filelist = file.read().splitlines()
    choiced_file_path = random.choice(list(fileset - set(recent_filelist)))

    if urlflag:
        return choiced_file_path.replace('/data', 'swirhen.tv')
    else:
        return recent_filelist[1:] + [choiced_file_path]


def upload_the_picture():
    filelist = choice_the_picture()
    swiutil.discord_post('どどんどどんどんどん！\n'
                        'きょうの一枚はこれだ！(すいれん.tv のとあるディレクトリから画像をランダムに抽出)')
    swiutil.discord_upload(CHANNEL, filelist[-1])
    with open(RECENT_LIST, mode='w') as file:
        file.write('\n'.join(filelist))


if __name__ == '__main__':
    upload_the_picture()
