#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ディレクトリリネーム用シェル
# ディレクトリを連番+スペースつきにリネームする
# 92〜99、00で開始するディレクトリは無視
# shって名前のdirも無視
# 引数 "-r" をつけると先頭の連番とスペースを削除

import glob
import os
import pathlib
import pprint
import re
import shutil
import sys

args = sys.argv
ARG = ''
if len(args) == 2:
    ARG = args[1]

dirlist = glob.glob('*/')

pprint.pprint(dirlist)