#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 動画リネーム用シェル
# リネーム用リストにはリネーム元ファイルの検索文字と正式な作品名を
# tabで繋げて記述すること
# 第1引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第2引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペースもしくは、第1引数が指定されている場合は第1引数。

import os,glob,sys,pathlib

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../python-lib/')

import util

print (file_open('checklist.txt'))