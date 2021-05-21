# -*- coding: utf-8 -*-
# import sections
import os
import pathlib
import re
import discord
import bot_util as bu
import swirhentv_util as swiutil

# argment section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
GIT_ROOT_DIR = '/home/swirhen/sh'
current_dir = pathlib.Path(__file__).resolve().parent
with open(f'{str(current_dir)}/discord_token') as tokenfile:
    TOKEN = tokenfile.read().splitlines()[0]


# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')

    if re.search('/seed.*', message.content):
        past_days = 3
        if len(message.content.split()) > 1:
            past_days = int(message.content.split()[1])
        await message.channel.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
        result = bu.get_seed_directory(past_days)
        # results = str_to_array(result)
        # for result in results:
        #     await message.channel.send(f'```{result}```')
        swiutil.writefile_new('result_temp', result)
        await message.channel.send(file=discord.File('result_temp'))
        os.remove('result_temp')


def str_to_array(in_str):
    result = []
    if len(in_str) <= 2000:
        return [in_str]
    else:
        res_line = ''
        res_line_temp = ''
        for line in in_str.split('\n'):
            res_line_temp += f'{res_line}{line}\n'
            if len(res_line_temp) > 2000:
                result.append(res_line)
                res_line = line
            else:
                res_line = res_line_temp
            res_line_temp = ''

    result.append(res_line)

    return result


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)