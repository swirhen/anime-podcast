#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画リネーム用シェル
# checklist.txtの後半(英語ファイル名|日本語ファイル名)のデータを使って動画ファイルをリネームする
# [英語ファイル名] -[SFX1][話数][SFX2](mp4 1280x720 aac).mp4
# -> [日本語ファイル名] 第[話数]話.mp4
# 第1引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第2引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペースもしくは、第1引数が指定されている場合は第1引数。

import glob
import os
import pathlib
import re
import sys


def main(filepath, SFX1='\ ', SFX2='\ '):
    current_dir = pathlib.Path(__file__).resolve().parent
    sys.path.append(str(current_dir) + '/python-lib/')
    import swirhentv_util

    # make rename list
    renamelist = swirhentv_util.make_rename_list()

    # make file list
    os.chdir(filepath)
    filelist = []
    filelist.extend(
        glob.glob("*.mp4") +
        glob.glob("*.mkv") +
        glob.glob("*.avi") +
        glob.glob("*.wmv"))

    # rename files
    for filename in filelist:
        for name in renamelist:
            nameE = name[0]
            nameJ = name[1]
            exp = r'.*(' + nameE + ').*' + SFX1 + '([0-9]{0,1}[0-9][0-9](.5)?)' + SFX2 + '.*\.(.*)'
            name = re.sub(exp, r'\1', filename)
            num = re.sub(exp, r'\2', filename)
            ext = re.sub(exp, r'\4', filename)

            if nameE == name:
                if os.path.isfile(filename + '.aria2'):
                    print('#' + filename + ' 成育中！')
                else:
                    newname = nameJ + ' 第' + num + '話.' + ext
                    if filename != newname:
                        print('# rename ' + filename + ' -> ' + newname)
                        os.rename(filename, newname)
                    else:
                        print('# 変更後のファイル名が同じ')
                break


# main section
filepath = ''
SFX1 = '\ '
SFX2 = '\ '
args = sys.argv
if len(args) == 1:
    filepath = args[2]
    if len(args) == 2:
        SFX1 = args[3]
    elif len(args) == 3:
        SFX2 = args[4]
    else:
        print("too many arguments.")
        exit(1)

main(filepath, SFX1, SFX2)
