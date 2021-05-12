#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# フィード作成(最近のアニメ)
# convert from mmpc.sh
# swirhentv_utilのmake_feed(target_dir)を呼び出すだけのもの
import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil

TARGET_DIR = f'{str(current_dir)}/../98 PSP用'

# main section
if __name__ == '__main__':
    swiutil.make_feed(TARGET_DIR)