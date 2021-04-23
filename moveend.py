#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 期またぎ移動用スクリプト
import os, sys, re, glob, math, psutil, shutil, pprint
import pathlib

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


# 入力(年)
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


# 入力(期)
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


# 入力(ターゲット)
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


# 入力(処理種別)
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


# 入力(チェックの有無)
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


# 入力(y/n)
def askconfirm():
    res = input('> ')
    if res == 'y' or res == 'Y':
        return 0
    elif res == 'n' or res == 'N':
        return 1
    else:
        print('y/nを入力してください。(EnterのみはNo)')
        askconfirm()


# 待ち(Enter)
def waitenter():
    input('(Enterで続行します)\n> ')


# 配下のファイルサイズ合計の取得(パス指定)
def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


# 配下のファイルサイズ合計の取得(パス, ファイル名指定)
def get_file_size(path, filename):
    total = 0
    filelist = sorted(glob.glob(path + '/' + filename + ' 第*.mp4'))
    for file in filelist:
        total += os.path.getsize(file)
    return total


# 移動処理(ルート)
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
    find_root_mv_dir = glob.glob(ROOT_MV_DIR + '/*' + YEAR + '-Q' + QUARTER + '終了分')
    if len(find_root_mv_dir) > 0:
        dstpath = find_root_mv_dir[0]
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


# 移動処理(98 PSP用)
def move_98(endlist):
    os.system('clear')
    # 容量チェック
    totalsize = 0
    for name in endlist:
        size = math.ceil(get_file_size(PSPMP4_98_DIR, name) / 1024 / 1024)
        print(name + ' : ' + str(size) + ' MB')
        totalsize += size

    totalsize = math.ceil(totalsize / 1024)
    print('total size : ' + str(totalsize) + ' GB')
    freesize = math.floor(psutil.disk_usage(PSPMP4_MV_DIR).free / 1024 / 1024 / 1024)
    print('free space size(' + PSPMP4_MV_DIR + ') : ' + str(freesize) + ' GB')

    if totalsize < freesize:
        print('Disk Space Check :OK')
    else:
        print('Disk Space Check :NG')
        exit(1)

    waitenter()

    # 移動先ディレクトリ、シンボリックリンク作成
    dstpath = ''
    find_pspmp4_mv_dir = glob.glob(PSPMP4_MV_DIR + '/' + QUARTER + 'Q-' + YEAR)
    if len(find_pspmp4_mv_dir) > 0:
        dstpath = find_pspmp4_mv_dir[0]
    else:
        dstpath = PSPMP4_MV_DIR + '/' + QUARTER + 'Q-' + YEAR
        print('destination directory is not found. make directory: ' + dstpath)
        os.makedirs(dstpath)

    dstlink = PSPMP4_98_DIR + '/' + QUARTER + 'Q-' + YEAR
    if not os.path.exists(dstlink):
        print('symbolic link is not found. make link: ' + dstlink)
        os.symlink(dstpath, dstlink)

    # 移動
    for name in endlist:
        if name[0] == '#':
            continue

        if CHECK == '1':
            filelist = list(pathlib.Path(PSPMP4_98_DIR).glob(name + ' 第*.mp4'))
            filelist_ignore_inteval_episodes = sorted([p.name for p in filelist if not re.search(r'\.5', str(p))])
            filecount = len(filelist_ignore_inteval_episodes)
            last_episode_count = int(re.sub(r'.*第(.*)話.*', r'\1', filelist_ignore_inteval_episodes[-1]))
            if filecount != last_episode_count:
                pprint.pprint(filelist_ignore_inteval_episodes)
                print('最終話とみられるファイル: ' + filelist_ignore_inteval_episodes[-1])
                print('ファイル個数: ' + str(filecount) + ' 一致しません。')
                print('move sure?')
                if askconfirm() == 1:
                    print('スキップします')
                    continue
            else:
                print(name + ' 抜けチェック: OK')

        if PROGRESS == '3':
            print('移動処理をスキップ')
        else:
            # 移動先のファイルチェック
            dstlist = glob.glob(dstpath + '/' + name + ' 第*.mp4')
            if len(dstlist) > 0:
                print('既に存在しているため、移動無し')
                continue
            else:
                movefiles = sorted(glob.glob(PSPMP4_98_DIR + '/' + name + ' 第*.mp4'))
                if len(movefiles) > 0:
                    for movefile in movefiles:
                        print('move: ' + movefile + ' -> ' + dstpath)
                        shutil.move(movefile, dstpath)
                        only_filename = re.sub(r'^.*\/', '', movefile)
                        os.symlink(dstpath + '/' + only_filename, movefile)
                        print(only_filename + ': 移動完了')

    print('ALL: 移動完了')


# シンボリックリンク削除
def remove_98(endlist):
    os.system('clear')
    for name in endlist:
        if name[0] == '#':
            continue

        check = True
        filelist = list(pathlib.Path(PSPMP4_98_DIR).glob(name + ' 第*.mp4'))
        for file in filelist:
            if not os.path.islink(file):
                check = False
                break

        if not check:
            print(name + ': 対象にシンボリックリンクでないファイルが存在。スキップします')

        # 削除
        for file in filelist:
            os.remove(file)

        print(name + ' シンボリックリンク削除: OK')


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
elif TARGET == '2':
    if PROGRESS == '1':
        move_98(endlist)
    elif PROGRESS == '2':
        remove_98(endlist)
    elif PROGRESS == '3':
        move_98(endlist)
