# swirhen.tv slackbot
# mention plugin
import os
import sys
import pathlib
import subprocess
import time
from datetime import datetime
from slackbot.bot import respond_to
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/../')
import swirhentv_util as swiutil


@respond_to('^ *�ł�����.*')
@respond_to('^ *�悭�����.*')
def doya(message):
    message.send('(�M�E�ցE�L)�h���@...')


@respond_to('^ *test')
def test(message):
    message.send('test!')
    swiutil.slack_upload('bot-sandbox', '../slackbot_run.py')
    message.reply('���킽(�M�E�ցE�L)')


# @respond_to('^ *sdl')
# def seed_download(message):
#     message.send('���[')
#     resultfile = "/data/share/movie/sh/autodl.result"
#     cmd = '/data/share/movie/sh/autodl.sh 1'
#     call_cmd(cmd)
#     if os.path.exists(resultfile):
#         result = open(resultfile).read()
#         message.reply('���킽(�M�E�ցE�L)\n```' + 'download seeds:\n' + result + '```')
#     else:
#         message.send('���킽(�L�E�ցE`)')
#
#
# @respond_to('^ *tdl')
# def torrent_download(message):
#     message.send('���[')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/torrent_download_' + launch_dt + '.temp'
#     filetitle = 'torrent_download_' + launch_dt
#     cmd = './tdl.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('���킽(�M�E�ցE�L)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *mre')
# def movie_rename(message):
#     message.send('���[')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/mre' + launch_dt + '.temp'
#     filetitle = 'movie_rename_' + launch_dt
#     cmd = './mre.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('���킽(�M�E�ցE�L)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *rmm')
# def movie_rename2(message):
#     message.send('���[')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/rmm_' + launch_dt + '.temp'
#     filetitle = 'movie_rename_' + launch_dt
#     cmd = './rmm.sh &> {0}'.format(logfile)
#     call_cmd(cmd)
#     message.reply('���킽(�M�E�ցE�L)')
#     time.sleep(1)
#     file_upload(logfile, filetitle, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *ae')
# def auto_encode(message):
#     message.send('���[')
#     launch_dt = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
#     cmd = '/data/share/movie/sh/169f.sh'
#     call_cmd(cmd)
#     message.reply('���킽(�M�E�ցE�L) (' + launch_dt + ' �������� ���[�Ƃ��񂱁[��)')
#
#
# @respond_to('^ *tss (.*)')
# def torrent_search(message, argment):
#     message.send('�������[')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/tss_' + launch_dt + '.temp'
#     filetitle = 'seed_search_result_' + launch_dt
#     cmd = './tss.sh {0} > {1}'.format(argment, logfile)
#     call_cmd(cmd)
#     result = open(logfile).read()
#     if result == 'no result.':
#         message.send('�Ȃ�������(�L�E�ցE`)')
#         os.remove(logfile)
#     else:
#         message.reply('��������(�M�E�ցE�L)')
#         time.sleep(1)
#         file_upload(logfile, filetitle, 'text', message)
#         time.sleep(1)
#         os.remove(logfile)
#
#
# @respond_to('^ *nico (.*)')
# def torrent_search(message, argment):
#     message.send('�������[')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/nico_' + launch_dt + '.temp'
#     filetitle = 'niconico_search_result_' + launch_dt
#     cmd = '/data/share/temp/voiceactor_nico_ch/sls_crawlnicoch.sh "{0}" > {1}'.format(argment, logfile)
#     call_cmd(cmd)
#     result = open(logfile).read()
#     if result == '':
#         message.send('�Ȃ�������(�L�E�ցE`)')
#         os.remove(logfile)
#     else:
#         message.reply('��������(�M�E�ցE�L)')
#         time.sleep(1)
#         file_upload(logfile, filetitle, 'text', message)
#         time.sleep(1)
#         os.remove(logfile)
#
#
# @respond_to('^ *il (.*)')
# def insert_list(message, argment):
#     message.send('���X�g�ɂ��������(/data/share/movie/sh/checklist.txt)')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/insert_list_' + launch_dt + '.temp'
#     cmd = './chklist_mod.sh i "{0}" > {1}'.format(argment.replace(' ', '_').replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('������B')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *dl (.*)')
# def delete_list(message, argment):
#     message.send('���X�g���炳�����傷���(/data/share/movie/sh/checklist.txt)')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/delete_list_' + launch_dt + '.temp'
#     cmd = './chklist_mod.sh d "{0}" > {1}'.format(argment.replace(' ', '_').replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('������B')
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
#     message.send('���X�g�ɂ��������(' + listpath + ')')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/insert_list_manual_' + launch_dt + '.temp'
#     cmd = './common_list_mod.sh "{0}" i "{1}" > {2}'.format(listpath, '_'.join(wordlist).replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('������B')
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
#     message.send('���X�g���炳�����傷���(' + listpath + ')')
#     launch_dt = datetime.now().strftime('%Y%m%d%H%M%S')
#     logfile = 'temp/delete_list_manual_' + launch_dt + '.temp'
#     cmd = './common_list_mod.sh "{0}" d "{1}" > {2}'.format(listpath, '_'.join(wordlist).replace(',', '" "'), logfile)
#     call_cmd(cmd)
#     message.reply('������B')
#     time.sleep(1)
#     file_upload(logfile, logfile, 'text', message)
#     time.sleep(1)
#     os.remove(logfile)
#
#
# @respond_to('^ *reload.*')
# def reload(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot ���ȍX�V���܂�')
#     cmd = './update.sh 2 ' + message._body['channel']
#     call_cmd(cmd)
#
#
# @respond_to('^ *reboot.*')
# def reboot(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot �ċN�����܂�')
#     cmd = './update.sh 0 ' + message._body['channel']
#     call_cmd(cmd)
#
#
# @respond_to('^ *update.*')
# def update(message):
#     message.reply(slackbot_settings.HOSTNAME + ' slackbot ���ȍX�V & �ċN�����܂�')
#     cmd = './update.sh 1 ' + message._body['channel']
#     call_cmd(cmd)


def call_cmd(cmd):
    ret = subprocess.run(cmd, shell=True)
    return ret


def exec_cmd(cmd):
    ret = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    return ret
