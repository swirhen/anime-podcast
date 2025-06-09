#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re
import urllib.request
from bs4 import BeautifulSoup

# main section
if __name__ == '__main__':
    args = sys.argv
    html = urllib.request.urlopen(args[0])
    soup = BeautifulSoup(html, "html.parser")
    print(re.sub(r'\<.*?\>|\ -.*|【.*】|\ ','', str(soup.find('title'))))
