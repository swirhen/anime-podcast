#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# フィード作成(引数版)
# convert from mmmpc.sh
# 引数1: /data/share/movie/98 PSP用 以下のディレクトリ名
# 引数2: フィードタイトル
import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swiutil

TARGET_DIR_PARENT = str(current_dir) + '/../98 PSP用'


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3:
        feed_directory = TARGET_DIR_PARENT + '/' + args[1]
        feed_title = args[2]
        if pathlib.Path(feed_directory).is_dir():
            swiutil.make_feed_manually(feed_directory, feed_title)
        else:
            print('error: directory not found. ' + feed_directory)
    else:
        print('usage: ' + args[0] + ' [feed_directory_name] [feed_title]')
        exit(1)
