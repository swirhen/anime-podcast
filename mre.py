#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画リネーム用シェル
# 第1引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第2引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペースもしくは、第1引数が指定されている場合は第1引数。

import os, glob, sys, pathlib,pprint,re

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')

FILE_PATH = str(current_dir) + '/checklist.txt'

args = sys.argv
if len(args) > 1:
    SFX1 = args[1]
    if len(args) == 2:
        SFX2 = args[1]
    elif len(args) == 3:
        SFX2 = args[2]
    else:
        print("too many arguments.")
        exit(1)

# file open
try:
    f = open(FILE_PATH, 'r', encoding='utf-8')
except Exception:
    print("open error. not found file: ", str(FILE_PATH))
    sys.exit(1)

for line in f:
    if re.search('^Last\ Update', line):
        continue
    line = re.sub(r'[^\ ]*\ .[^\ ]\ ', '', line)
    # print(line)
    line = line.strip().split("|")
    nameE = line[0]
    nameJ = line[1]

    print(nameJ)
