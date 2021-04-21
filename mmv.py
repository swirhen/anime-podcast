#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画移動用シェル
# checklist.txtの後半(日本語ファイル名)のデータを使って動画ファイルを移動する
# 引数のファイルが一致する日本語ファイル名を同名のディレクトリに移動する(ディレクトリなければつくる)

import glob
import os
import pathlib
import re
import shutil
import sys

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util

args = sys.argv
FILENAME = ''
if len(args) == 2:
    FILENAME = args[1]
else:
    print('usage: ' + args[0] + ' [FILENAME]')
    exit(1)

# make rename list
renamelist = swirhentv_util.make_rename_list()

# move file
for name in renamelist:
    nameJ = name[1]
    nameJ_exp = name[1].replace('(', '\(').replace(')', '\)')
    exp = r'.*' + nameJ_exp + '.*'
    if re.match(exp, FILENAME):
        dstdir = glob.glob('*' + nameJ)
        if len(dstdir) > 0:
            dstdir = dstdir[0]
            shutil.move(FILENAME, dstdir)
        else:
            print('directory not found. makedir ' + nameJ)
            os.makedirs(nameJ)
            shutil.move(FILENAME, nameJ)
