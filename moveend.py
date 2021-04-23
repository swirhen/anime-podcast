#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 期またぎ移動用スクリプト
import os,sys,re,glob

BASE_DIR = '/data/share/movie'
PSPMP4_98_DIR = BASE_DIR + '/98 PSP用'
PSPMP4_MV_DIR = '/data2/movie2/pspmp4'
ROOT_MV_DIR = '/data3/movie3'
ROOT_MV_DIR_LINK = '/data/share/movie/0004 過去連載終了分'
END_LIST_FILE = ''
END_FILES = []
YEAR = ''
QUARTER = ''
TARGET = ''
PROGRESS = ''
CHECK = ''


def askyear():
    YEAR = input('Year? (YYYY)\n'
                 'q: quit\n> ')
    if re.match(r'^[1-2][0-9][0-9][0-9]$', YEAR):
        return YEAR
    elif YEAR == 'q' or YEAR == 'Q':
        print('bye')
        exit(0)
    else:
        print('Year is not valid.')
        askyear()


def askquarter():
    QUARTER = input('Quarter? (1-4)\n'
                    'q: quit\n> ')
    if re.match(r'[1-4]$', QUARTER):
        return QUARTER
    elif QUARTER == 'q' or QUARTER == 'Q':
        print('bye')
        exit(0)
    else:
        print('Quarter is not valid.')
        askquarter()


def asktarget():
    TARGET = input('Target?\n'
                   '1: root(' + BASE_DIR + ')\n'
                   '2: pspmp4(' + PSPMP4_98_DIR + ')\n'
                   'q: quit\n> ')
    if re.match(r'[1-2]$', TARGET):
        return TARGET
    elif TARGET == 'q' or TARGET == 'Q':
        print('bye')
        exit(0)
    else:
        print('Target is not valid.')
        asktarget()


def askprogress():
    PROGRESS = input('Progress?\n'
                     '1: move end program 2: remove symbolic link 3: check only\n'
                     'q: quit\n> ')
    if re.match(r'[1-3]$', PROGRESS):
        return PROGRESS
    elif PROGRESS == 'q' or PROGRESS == 'Q':
        print('bye')
        exit(0)
    else:
        print('Progress is not valid.')
        askprogress()


def askcheck():
    CHECK = input('Check?\n'
                  '0: off 1: on\n'
                  'q: quit\n> ')
    if re.match(r'[1-3]$', CHECK):
        return CHECK
    elif CHECK == 'q' or CHECK == 'Q':
        print('bye')
        exit(0)
    else:
        print('Check is not valid.')
        askcheck()


def askconfirm():
    res = input('> ')
    if res == 'y' or res == 'Y':
        return 0
    elif res == 'n' or res == 'N':
        return 1
    else:
        print('y/nを入力してください。(EnterのみはNo)')
        askconfirm()


def waitenter():
    input('(Enterで続行します)\n> ')


def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def move_root(endlist):
    os.system('clear')
    # 容量チェック
    filesize = 0
    for name in endlist:
        print(name)
        dir = glob.glob('*' + name)[0]
        print(dir)
        size = get_dir_size(dir)
        filesize += size
        print(name + ' : ' + str(size) + ' Bytes')

    print('totalsize : ' + str(filesize) + ' Bytes')
    print('totalsize : ' + str(filesize / 1024 / 1024 / 1024) + ' GB')


# main
args = sys.argv
os.system('clear')

if len(args) > 1:
    YEAR = args[1]
else:
    YEAR = askyear()

if len(args) > 2:
    QUARTER = args[2]
else:
    QUARTER = askquarter()

if len(args) > 3:
    TARGET = args[3]
else:
    TARGET = asktarget()

if len(args) > 4:
    PROGRESS = args[4]
else:
    PROGRESS = askprogress()

if len(args) > 5:
    CHECK = args[5]
else:
    CHECK = askcheck()

print('YEAR: ' + YEAR + '\n'
      'QUARTER: ' + QUARTER + '\n'
      'TARGET: ' + TARGET + '\n'
      'PROGRESS: ' + PROGRESS + '\n'
      'CHECK: ' + CHECK + '\n')

# 終了ファイルリストの存在チェック・読み込み
END_LIST_FILE = BASE_DIR + '/end_' + YEAR + 'Q' + QUARTER + '.txt'

if not os.path.isfile(END_LIST_FILE):
    print('endlist file not found.')
    exit(1)

listfile = open(END_LIST_FILE, 'r', encoding='utf-8')
endlist = []
for line in listfile.readlines():
    endlist.append(line)

# 処理分岐
if TARGET == '1':
    move_root(endlist)
# elif TARGET == '2':
#     if PROGRESS == '1':
#         move_98(endlist)
#     elif PROGRESS == '2':
#         remove_98(endlist)
#     elif PROGRESS == '3':
#         move_98(endlist)
