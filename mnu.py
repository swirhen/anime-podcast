#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ディレクトリリネーム用シェル
# ディレクトリを連番+スペースつきにリネームする
# 92〜99、00で開始するディレクトリは無視
# shって名前のdirも無視
# 引数 "-r" をつけると先頭の連番とスペースを削除

import glob
import os
import re
import sys

args = sys.argv
ARG = ''
if len(args) == 2:
    ARG = args[1]

dirlist = glob.glob('*/')
dirlist.sort()

num = 1
for directory in dirlist:
    exp = r'^00|^9[2-9]|^sh|^nico|^on|^py'
    if re.match(exp, directory):
        print(directory + ' : 処理除外')
        continue
    else:
        exp = r'^[0-9][0-9]\ (.*)'
        newdirname = re.sub(exp, r'\1', directory)
        os.rename(directory, newdirname)
        if ARG == '-r':
            if directory != newdirname:
                print('# rename ' + directory + ' -> ' + newdirname)
            continue
        else:
            numstr = '{0:02d}'.format(num)
            os.rename(newdirname, numstr + ' ' + newdirname)
            if directory != numstr + ' ' + newdirname:
                print('# rename ' + directory + ' -> ' + numstr + ' ' + newdirname)
            num += 1