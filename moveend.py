#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 期またぎ移動用スクリプト
import os, sys, re, glob, math, psutil, shutil, pprint

BASE_DIR = '/data/share/movie'
PSPMP4_98_DIR = BASE_DIR + '/98 PSP用'
PSPMP4_MV_DIR = '/data2/movie2/pspmp4'
ROOT_MV_DIR = '/data3/movie3'
ROOT_MV_LINK_DIR = '/data/share/movie/0004 過去連載終了分'
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
        path = glob.glob(BASE_DIR + '/*' + name)
        if len(path) > 0:
            size = get_dir_size(path[0])
            filesize += size
        else:
            print('source path (' + BASE_DIR + '/*' + name + ') is not found')
            continue

    totalsize = math.ceil(filesize / 1024 / 1024 / 1024)
    print('total size : ' + str(totalsize) + ' GB')
    freesize = math.floor(psutil.disk_usage(ROOT_MV_DIR).free / 1024 / 1024 / 1024)
    print('free space size(' + ROOT_MV_DIR + ') : ' + str(freesize) + ' GB')

    if totalsize < freesize:
        print('Disk Space Check :OK')
    else:
        print('Disk Space Check :NG')
        exit(1)

    waitenter()

    # 移動先ディレクトリ作成
    dstpath = ''
    FIND_ROOT_MV_DIR = glob.glob(ROOT_MV_DIR + '/*' + YEAR + '-Q' + QUARTER + '終了分')
    if len(FIND_ROOT_MV_DIR) > 0:
        dstpath = FIND_ROOT_MV_DIR[0]
    else:
        # 最後の番号を取得
        lastpath = sorted(glob.glob(ROOT_MV_DIR + '/*'))[-1]
        dstnum = str(int(re.sub(r'^.*\/', '', lastpath)[1:3]) + 1).zfill(3)
        dstpath = ROOT_MV_DIR + '/' + dstnum.ljust(4) + YEAR + '-Q' + QUARTER + '終了分'
        print('destination directory is not found. make directory: ' + dstpath)
        os.makedirs(dstpath)

    # 移動
    for name in endlist:
        if name[0] == '#':
            continue

        srcpath = glob.glob(BASE_DIR + '/*' + name)
        if len(srcpath) > 0:
            srcpath = srcpath[0]
        else:
            print('source path (' + BASE_DIR + '/*' + name + ') is not found')
            continue

        print('# move: ' + srcpath + ' -> ' + dstpath)
        result = shutil.move(srcpath, dstpath)
        print('# complete: ' + result)

    print('ALL: 移動完了')


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
    endlist.append(line.strip())

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
