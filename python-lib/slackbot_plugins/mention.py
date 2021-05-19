# swirhen.tv slackbot
# mention plugin
# notice: ../slackbot_run.pyから読み込まれるので、カレントディレクトリは1個上の扱い
# import section
import os
import sys
import pathlib
import subprocess
import time
from datetime import datetime
from slackbot.bot import respond_to
import swirhentv_util as swiutil

# argment section
SEED_DOWNLOAD_DIR = '/data/share/temp/torrentsearch'
DATE = datetime.now().strftime('%Y%m%d')


@respond_to('^ *でかした.*')
@respond_to('^ *よくやった.*')
def doya(message):
    message.send('(｀・ω・´)ドヤァ...')


@respond_to('^ *test')
def test(message):
    message.send('test!')
    swiutil.slack_upload('bot-sandbox', 'slackbot_run.py')
    message.reply('おわた(｀・ω・´)')


@respond_to('^ *seed(.*)')
def announce_seed_info(message, argment):
    if argment != '':
        past_days = int(argment)
    else:
        past_days = 3
    message.send(f'あつめた種の情報をおしらせするよ(さいきん{past_days}にちぶん)')
    paths = list(pathlib.Path(SEED_DOWNLOAD_DIR).glob('*'))
    paths.sort(key=os.path.getctime(), reverse=True)
    get_paths = paths[:past_days]
    seed_info = dict()
    for get_path in get_paths:
        if not get_path.name in seed_info:
            seed_info[get_path.name] = []

        seed_list = list(pathlib.Path(get_path).glob('*'))
        for seed in seed_list:
            seed_info[get_path.name].append(seed.name)

    post_str = '```'
    for dir in seed_info:
        post_str += f'directory {dir} in seeds:\n'
        for seed in seed_info[dir]:
            post_str += f'{seed}\n'

    post_str += '```'

    message.send(post_str)


# @respond_to('^ *sdl')
# def seed_download(message):
#     message.send('やるー')
#     resultfile = "/data/share/movie/sh/autodl.result"
#     cmd = '/data/share/movie/sh/autodl.sh 1'
#     call_cmd(cmd)
#     if os.path.exists(resultfile):
#         result = open(resultfile).read()
#         message.reply('おわた(｀・ω・´)\n```' + 'download seeds:\n' + result + '```')
#     else:
#         message.send('おわた(´・ω・`)')
#
#
# @respond_to('^ *tdl')
# def torrent_download(message):
#     message.send('やるー')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/torrent_download_' + launch_dt + '.temp'
#     filetitle = 'torrent_download_' + launch_dt
#     cmd = './tdl.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('おわた(｀・ω・´)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *mre')
# def movie_rename(message):
#     message.send('やるー')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/mre' + launch_dt + '.temp'
#     filetitle = 'movie_rename_' + launch_dt
#     cmd = './mre.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('おわた(｀・ω・´)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *rmm')
# def movie_rename2(message):
#     message.send('やるー')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/rmm_' + launch_dt + '.temp'
#     filetitle = 'movie_rename_' + launch_dt
#     cmd = './rmm.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('おわた(｀・ω・´)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *ae')
# def auto_encode(message):
#     message.send('やるー')
#     launch_dt = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
#     cmd = '/data/share/movie/sh/169f.sh'
#     call_cmd(cmd)
#     message.reply('おわた(｀・ω・´) (' + launch_dt + ' かいしの おーとえんこーど)')
#
#
# @respond_to('^ *tss (.*)')
# def torrent_search(message, argment):
#     message.send('さがすー')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/tss_' + launch_dt + '.temp'
#     filetitle = 'seed_search_result_' + launch_dt
#     cmd = './tss.sh {0} > {1}'.format(argment, logfile)
#     call_cmd(cmd)
#     result = open(logfile).read()
#     if result == 'no result.':
#         message.send('なかったよ(´・ω・`)')
#         os.remove(logfile)
#     else:
#         message.reply('あったよ(｀・ω・´)')
#         time.sleep(1)
#         file_upload(logfile, filetitle, 'text', message)
#         time.sleep(1)
#         os.remove(logfile)
#
#
# @respond_to('^ *nico (.*)')
# def torrent_search(message, argment):
#     message.send('さがすー')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/nico_' + launch_dt + '.temp'
#     filetitle = 'niconico_search_result_' + launch_dt
#     cmd = '/data/share/temp/voiceactor_nico_ch/sls_crawlnicoch.sh "{0}" > {1}'.format(argment, logfile)
#     call_cmd(cmd)
#     result = open(logfile).read()
#     if result == '':
#         message.send('なかったよ(´・ω・`)')
#         os.remove(logfile)
#     else:
#         message.reply('あったよ(｀・ω・´)')
#         time.sleep(1)
#         file_upload(logfile, filetitle, 'text', message)
#         time.sleep(1)
#         os.remove(logfile)
#
#
# @respond_to('^ *il (.*)')
# def insert_list(message, argment):
#     message.send('リストについかするで(/data/share/movie/sh/checklist.txt)')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/insert_list_' + launch_dt + '.temp'
#     cmd = './chklist_mod.sh i "{0}" > {1}'.format(argment.replace(' ', '_').replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('おあり。')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *dl (.*)')
# def delete_list(message, argment):
#     message.send('リストからさくじょするで(/data/share/movie/sh/checklist.txt)')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/delete_list_' + launch_dt + '.temp'
#     cmd = './chklist_mod.sh d "{0}" > {1}'.format(argment.replace(' ', '_').replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('おあり。')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *ilm (.*)')
# def insert_list_manual(message, argment):
#     args = argment.split()
#     listpath = args[0]
#     wordlist = []
#     for i, arg in enumerate(args):
#         if i < 1:
#             pass
#         else:
#             wordlist.append(arg)
#
#     message.send('リストについかするで(' + listpath + ')')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/insert_list_manual_' + launch_dt + '.temp'
#     cmd = './common_list_mod.sh "{0}" i "{1}" > {2}'.format(listpath, '_'.join(wordlist).replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('おあり。')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *dlm (.*)')
# def delete_list_manual(message, argment):
#     args = argment.split()
#     listpath = args[0]
#     wordlist = []
#     for i, arg in enumerate(args):
#         if i < 1:
#             pass
#         else:
#             wordlist.append(arg)
#
#     message.send('リストからさくじょするで(' + listpath + ')')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/delete_list_manual_' + launch_dt + '.temp'
#     cmd = './common_list_mod.sh "{0}" d "{1}" > {2}'.format(listpath, '_'.join(wordlist).replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('おあり。')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *reload.*')
# def reload(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot 自己更新します')
#     cmd = './update.sh 2 ' + message._body['channel']
#     call_cmd(cmd)
#
#
# @respond_to('^ *reboot.*')
# def reboot(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot 再起動します')
#     cmd = './update.sh 0 ' + message._body['channel']
#     call_cmd(cmd)
#
#
# @respond_to('^ *update.*')
# def update(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot 自己更新 & 再起動します')
#     cmd = './update.sh 1 ' + message._body['channel']
#     call_cmd(cmd)


def call_cmd(cmd):
    ret = subprocess.run(cmd, shell=True)
    return ret


def exec_cmd(cmd):
    ret = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    return ret
