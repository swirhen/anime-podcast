#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re,pathlib
import urllib.request
from bs4 import BeautifulSoup
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil
sys.path.append(f'/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as ts


# fantiaのタイトル取得
def get_fantia_title(keyword, regexp='\<.*?\>|\ -.*|【.*?】', uri='https://fantia.jp/posts/'):
    id = re.sub(r'\D', '', keyword)
    html = urllib.request.urlopen(uri + id)
    soup = BeautifulSoup(html, "html.parser")
    title = re.sub(regexp, '', str(soup.find('title'))).strip()
    rtitle = keyword + " - " + title
    ret = swiutil.file_name_cut(rtitle)
    return ret


# avのタイトル取得(sukebeiのDBからとる)
def get_av_title(keyword, regexp='\+\+\+|\[.*?\]', cut=True):
    result = ts.search_seed_ext('av', keyword)
    
    if len(result) == 0:
        return 'NORESULTSFOUND'
    else:
        title = result[0][1]
        title = re.sub(regexp, '', title).strip()
        if cut:
            ret = swiutil.file_name_cut(title)
        else:
            ret = title
    return ret


# main section
if __name__ == '__main__':
    args = sys.argv
    mode = args[1]
    keyword = args[2]
    if len(args) > 3:
        regexp = args[3]
    if len(args) > 4:
        if args[3] == '':
            if mode == 'f':
                regexp = '\<.*?\>|\ -.*|【.*?】'
            elif mode == 'a':
                regexp = '\+\+\+|\[.*?\]'
        uri = args[4]
    
    if mode == 'f':
        if len(args) == 4:
            ret = get_fantia_title(keyword, regexp)
        elif len(args) == 5:
            ret = get_fantia_title(keyword, regexp, uri)
        else:
            ret = get_fantia_title(keyword)
    
    if mode == 'a':
        if len(args) == 4:
            ret = get_av_title(keyword, regexp)
        elif len(args) == 5:
            ret = get_av_title(keyword, regexp, False)
        else:
            ret = get_av_title(keyword)

print(ret)
