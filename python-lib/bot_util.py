# swirhen.tv bot utility
# slackbot Ç∆ discord botÇ©ÇÁåƒÇ—èoÇ∑ã§í èàóù
# import section
import os
import re
import sys
import pathlib
import shutil
import subprocess
from datetime import datetime
import time
import git
import urllib.request
from slackbot.bot import respond_to
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argment section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
GIT_ROOT_DIR = '/home/swirhen/sh'


def get_seed_directory(past_days):
    result = ''
    paths = sorted(list(pathlib.Path(SEED_DOWNLOAD_DIR).glob('2*')), reverse=True)
    get_paths = paths[:past_days]
    seed_info = dict()
    for get_path in get_paths:
        if not get_path.name in seed_info:
            seed_info[get_path.name] = []

        seed_list = list(pathlib.Path(get_path).glob('*'))
        for seed in seed_list:
            seed_info[get_path.name].append(seed.name)

    for path in seed_info:
        result += f'directory {path} in seeds:\n'
        for seed in seed_info[path]:
            result += f'    {seed}\n'

    return result