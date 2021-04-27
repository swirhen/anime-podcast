#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv python library
import pathlib
import re
import sys
from slacker import Slacker
import slackbot_settings

current_dir = pathlib.Path(__file__).resolve().parent
CHECKLIST_FILE_PATH = str(current_dir) + '/../checklist.txt'


def make_rename_list():
    # file open
    try:
        listfile = open(CHECKLIST_FILE_PATH, 'r', encoding='utf-8')
    except Exception:
        print("open error. not found file: ", str(CHECKLIST_FILE_PATH))
        sys.exit(1)

    # make rename list
    renamelist = []
    for line in listfile.readlines():
        if re.search('^Last Update', line):
            continue
        line = re.sub(r'^[^ ]+ [^ ]+ ', '', line)
        line = line.strip().split("|")
        renamelist.append(line)

    return renamelist


def slack_post(channel, text, username='swirhentv', icon_emoji=''):
    slack = Slacker(slackbot_settings.API_TOKEN)
    slack.chat.post_message(
        channel,
        text,
        username=username,
        icon_emoji=icon_emoji,
        link_names=1,
    )


def slack_upload(channel, filepath, filetype='text'):
    slack = Slacker(slackbot_settings.API_TOKEN)
    slack.files.upload(channels=channel, file_=filepath, filetype=filetype)


def askconfirm():
    res = input('> ')
    if res == 'y' or res == 'Y':
        return 0
    elif res == 'n' or res == 'N':
        return 1
    else:
        print('y/nを入力してください。(EnterのみはNo)')
        askconfirm()


def grep_file(filepath, word):
    with open(filepath, 'r', newline='') as f:
        lines = f.readlines()

    for line in lines:
        if line.strip() == word:
            return(line.strip())