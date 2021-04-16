#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画リネーム用シェル
# 第1引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第2引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペースもしくは、第1引数が指定されている場合は第1引数。

import os, glob, sys, pathlib,re

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
LIST_FILE_PATH = str(current_dir) + '/checklist.txt'

SFX1 = '\ '
SFX2 = '\ '
print(SFX1)
print(SFX2)
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
    listfile = open(LIST_FILE_PATH, 'r', encoding='utf-8')
except Exception:
    print("open error. not found file: ", str(LIST_FILE_PATH))
    sys.exit(1)

# make rename list
renamelist = []
for line in listfile.readlines():
    if re.search('^Last Update', line):
        continue
    line = re.sub(r'^[^ ]+ [^ ]+ ', '', line)
    line = line.strip().split("|")
    renamelist.append(line)

# make file list
filelist = []
filelist.extend(glob.glob("*.mp4") + glob.glob("*.mkv") + glob.glob("*.avi") + glob.glob("*.wmv"))

# rename files
for filename in filelist:
    for name in renamelist:
        nameE = name[0]
        nameJ = name[1]
        exp = r'.*(' + nameE + ').*' + SFX1 + '([1-9]{0,1}[0-9][0-9](.5)?)' + SFX2 + '.*\.(.*)'
        name = re.sub(exp, r'\1', filename)
        num = re.sub(exp, r'\2', filename)
        ext = re.sub(exp, r'\4', filename)

        if nameE == name:
            if os.path.isfile(filename + '.aria2'):
                print('#' + filename +' 成育中！')
            else:
                newname = nameJ + ' 第' + num + '話.' + ext
                if filename != newname:
                    print('# rename ' + filename + ' -> ' + newname)
                    os.rename(filename, newname)
                else:
                    print('# 変更後のファイル名が同じ')
            break