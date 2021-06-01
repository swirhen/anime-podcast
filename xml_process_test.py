#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xml処理のスピードをテストする
# import section
import sys
import pathlib
import time
import urllib.request
import xml.etree.ElementTree as elementTree
import subprocess
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil

# arguments section
SCRIPT_DIR = str(current_dir)


# ログ書き込み
def main():
    # tekitouna nyaa feed URL get
    
