#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import pathlib
import subprocess
import sys

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swutil
from datetime import datetime as dt
import time

SCRIPT_DIR = str(current_dir)
DOWNLOAD_DIR = '/data/share/temp'
TDATETIME = dt.now()
DATETIME = TDATETIME.strftime('%Y/%m/%d-%H:%M:%S')

seedlist = glob.glob(DOWNLOAD_DIR + '/*.torrent')
if len(seedlist) == 0:
    print('seed file not found: ' + DOWNLOAD_DIR)
    exit(1)

print('栽培監視開始')
post_msg='torrent douwnload: 以下のファイルの栽培を開始\n' + \
         '```' + '\n'.join(seedlist) + '```'
swutil.slack_port('bot-sandbox', post_msg)

os.chdir(DOWNLOAD_DIR)
proc = subprocess.Popen('aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent', shell=True)

time.sleep(10)

while True:
    if len(glob.glob(DOWNLOAD_DIR + '/*.aria2')) == 0:
        proc.kill()
        break

post_msg='torrent douwnload: 以下のファイルの栽培を完了\n' + \
         '```' + '\n'.join(seedlist) + '```'
swutil.slack_port('bot-sandbox', post_msg)
