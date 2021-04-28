#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib
import sys

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/python-lib/')
import swirhentv_util as swutil

DOWNLOAD_DIR = '/data/share/temp'
swutil.torrent_download(DOWNLOAD_DIR, 'bot-sandbox')