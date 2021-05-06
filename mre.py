#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画リネーム用シェル
# checklist.txtの後半(英語ファイル名|日本語ファイル名)のデータを使って動画ファイルをリネームする
# ex)
# [英語ファイル名] -[SFX1][話数][SFX2](mp4 1280x720 aac).mp4
# -> [日本語ファイル名] 第[話数]話.mp4
# 第1引数(省略可): 対象ディレクトリ 省略時は現在ディレクトリ
# 第2引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。省略時は半角スペース。
# 第3引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。省略時は半角スペース もしくは、第2引数が指定されている場合は第2引数。

import os
import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swiutil


# main section
if __name__ == '__main__':
    filepath = ''
    SFX1 = '\ '
    SFX2 = '\ '
    args = sys.argv
    if len(args) == 1:
        filepath = os.getcwd()
    elif len(args) > 1:
        filepath = args[1]
        if len(args) > 2:
            SFX1 = args[2]
            SFX2 = args[2]
            if len(args) > 3:
                SFX2 = args[3]
            else:
                print('too many arguments.')
                print('usage: ' + args[0] + ' [filepath] (separator1) (separator2)')
                exit(1)

    swiutil.rename_movie(filepath, SFX1, SFX2)
