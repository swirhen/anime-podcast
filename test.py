#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib
import subprocess

current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
DOWNLOAD_DIR = '/data/share/temp'
os.chdir(DOWNLOAD_DIR)

# subprocess.call(['aria2c', '--listen-port=38888', '--max-upload-limit=200K', '--seed-ratio=0.01', '--seed-time=1 ', DOWNLOAD_DIR + '/*.torrent'])
subprocess.Popen('aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent', shell=True)
