#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# フィード作成(リストから)
# convert from mpc98.sh
# /data/share/movie/98 PSP用/list.txt のリストファイルにある情報をもとに
# 複数の番組フィードを作成する
# リストファイルの書式: [フィードのディレクトリ名(98 PSP用の下にあること)] [フィードタイトル]
import pathlib
import re
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil


TARGET_DIR_PARENT = f'{str(current_dir)}/../98 PSP用'
LISTFILE = f'{TARGET_DIR_PARENT}/list.txt'

# main section
if __name__ == '__main__':
    lines = open(LISTFILE, 'r', encoding='utf-8').read().splitlines()
    for line in lines:
        feed_directry_name = re.sub(r'^([^ ]+) (.*)', r'\1', line)
        feed_directory = f'{TARGET_DIR_PARENT}/{feed_directry_name}'
        feed_title = re.sub(r'^([^ ]+) (.*)', r'\2', line)

        if pathlib.Path(feed_directory).is_dir():
            swiutil.make_feed_manually(feed_directory, feed_title)
        else:
            print(f'error: directory not found. {feed_directory}')
