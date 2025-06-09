#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re
import urllib.request
from bs4 import BeautifulSoup

# main section
if __name__ == '__main__':
    args = sys.argv
    name = args[1]
    if len(args) == 3:
            uri = args[2]
    else:
        uri = 'https://fantia.jp/posts/'
    
    id = re.sub(r'\D', '', name)
    html = urllib.request.urlopen(uri + id)
    soup = BeautifulSoup(html, "html.parser")
    title = re.sub(r'\<.*?\>|\ -.*|【.*?】|\ ','', str(soup.find('title')))
    rtitle = name + " - " + title
    if len(rtitle.encode('utf-8')) > 255:
        over = len(rtitle.encode('utf-8')) - 255
        cut = len(title.encode('utf-8')) - over
        ret = title.encode('utf-8')[0:cut].decode('utf-8', errors='ignore')
    else:
        ret = title
print(ret)
