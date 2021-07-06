#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ディレクトリリネーム用シェル
# ディレクトリを連番+スペースつきにリネームする
# 92〜99、00で開始するディレクトリは無視
# shって名前のdirも無視
# 引数 "-r" をつけると先頭の連番とスペースを削除
# import section
import glob
import os
import re
import sys


def mnu(arg=''):
    dirlist = glob.glob('*/')
    dirlist.sort()

    num = 1
    for directory in dirlist:
        exp = r'^00\ |^9[2-9]\ |^sh$'
        if re.match(exp, directory):
            print(f'{directory} : 処理除外')
            continue
        else:
            exp = r'^[0-9][0-9]\ (.*)'
            dirname_without_num = re.sub(exp, r'\1', directory)
            if arg == '-r':
                if directory != dirname_without_num:
                    os.rename(directory, dirname_without_num)
                    print(f'# rename {directory} -> {dirname_without_num}')
            else:
                numstr = '{0:02d}'.format(num)
                dirname_with_num = f'{numstr} {dirname_without_num}'
                if directory != dirname_with_num:
                    os.rename(directory, dirname_with_num)
                    print(f'# rename {directory} -> {dirname_with_num}')
                num += 1


# main section
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        mnu(args[1])
    elif len(args) == 1:
        mnu()
    else:
        print(f'usage: {args[0]} (-r)')
        exit(1)
