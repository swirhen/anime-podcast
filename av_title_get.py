#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re,pathlib
sys.path.append(f'/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as ts
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil

# main section
if __name__ == '__main__':
    args = sys.argv
    keyword = args[1]
    if len(args) == 3:
        regexp = args[2]
    else:
        regexp = '\+\+\+|\[.*?\]'

    result = ts.search_seed_ext('av', keyword)

    if len(result) == 0:
        print('NORESULTSFOUND')
    else:
        title = result[0][1]
        title = re.sub(regexp, '', title).strip()
        ret = swiutil.file_name_cut(title)
        print(ret)