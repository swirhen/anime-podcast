#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re,pathlib
import urllib.request
from bs4 import BeautifulSoup
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil


# main section
if __name__ == '__main__':
    args = sys.argv
    name = args[1]
    if len(args) > 2:
            regexp = args[2]
    else:
        regexp = '\<.*?\>|\ -.*|【.*?】'
    if len(args) > 3:
            uri = args[3]
    else:
        uri = 'https://fantia.jp/posts/'
    
    id = re.sub(r'\D', '', name)
    html = urllib.request.urlopen(uri + id)
    soup = BeautifulSoup(html, "html.parser")
    title = re.sub(regexp, '', str(soup.find('title'))).strip()
    rtitle = name + " - " + title
    ret = swiutil.file_name_cut(rtitle)

print(ret)
