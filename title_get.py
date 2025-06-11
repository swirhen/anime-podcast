#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re,pathlib
import urllib.request
from bs4 import BeautifulSoup
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil


def get_fantia_title(name, regexp='\<.*?\>|\ -.*|【.*?】', uri='https://fantia.jp/posts/'):
    id = re.sub(r'\D', '', name)
    html = urllib.request.urlopen(uri + id)
    soup = BeautifulSoup(html, "html.parser")
    title = re.sub(regexp, '', str(soup.find('title'))).strip()
    rtitle = name + " - " + title
    ret = swiutil.file_name_cut(rtitle)
    return ret


# main section
if __name__ == '__main__':
    args = sys.argv
    mode = args[1]
    keyword = args[2]
    if len(args) > 3:
        print(args[3])
        regexp = args[3]
    if len(args) > 4:
        uri = args[4]
    
    if mode == 'f':
        if len(args) == 4:
            ret = get_fantia_title(keyword, regexp)
        if len(args) == 5:
            ret = get_fantia_title(keyword, regexp, uri)
        else:
            ret = get_fantia_title(keyword)

print(ret)
