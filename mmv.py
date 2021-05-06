#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画移動用シェル
# checklist.txtの後半(日本語ファイル名)のデータを使って動画ファイルを移動する
# 引数のファイルが一致する日本語ファイル名を同名のディレクトリに移動する(ディレクトリなければつくる)

import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swiutil


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        swiutil.move_movie(args[1])
    else:
        print('usage: ' + args[0] + ' [FILENAME or DIRECTORY]')
        exit(1)
