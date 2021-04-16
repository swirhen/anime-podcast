#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# swirhen.tv python library
import pathlib
import re
import sys

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
