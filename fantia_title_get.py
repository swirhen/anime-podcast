#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re
import urllib.request
from bs4 import BeautifulSoup

# main section
if __name__ == '__main__':
    args = sys.argv
    header = args[2]
    html = urllib.request.urlopen(args[1])    
    soup = BeautifulSoup(html, "html.parser")
    title = re.sub(r'\<.*?\>|\ -.*|【.*?】|\ ','', str(soup.find('title')))
    rtitle = header + title
    if len(rtitle.encode('utf-8')) > 255:
        over = len(rtitle.encode('utf-8')) - 255
        cut = len(title.encode('utf-8')) - over
        ret = title.encode('utf-8')[0:cut].decode('utf-8', errors='ignore')
    else:
        ret = title
print(ret)
