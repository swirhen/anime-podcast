# -*- coding: utf-8 -*-
# import sections
import os
import pathlib
import re
from datetime import datetime
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
SCRIPT_DIR = str(current_dir)
with open(f'{SCRIPT_DIR}/discord_token') as tokenfile:
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

    # 種情報
    if re.search('^/seed.*', message.content):
        tdatetime = datetime.now()
        dt = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_info_{dt}.txt'
        past_days = 3
        if len(message.content.split()) > 1:
            past_days = int(message.content.split()[1])
        await message.channel.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
        result = bu.get_seed_directory(past_days)
        swiutil.writefile_new(result_file_name, result)
        await message.channel.send(file=discord.File(result_file_name))
        os.remove(result_file_name)

    if re.search('^/ts.*', message.content):
        tdatetime = datetime.now()
        dt = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_search_{dt}.txt'
        keyword = ''
        target_category = 'all'
        argments = message.content.split()
        if len(argments) > 2:
            keyword = argments[1]
            if len(argments) > 3:
                target_category = argments[2]
        else:
            await message.channel.send('つかいかた(´･ω･`)\nts [けんさくキーワード] [たいしょうカテゴリ]\nカテゴリ: doujin/manga/music/comic/live/all\n(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)')
            return

        await message.channel.send(f'さがしてくるよ(｀･ω･´)\nたいしょうカテゴリ: {target_category} きーわーど: {keyword}')
        result = bu.seed_search(keyword, target_category)
        if re.search('なかったよ',result):
            await message.channel.send(result)
        else:
            await message.channel.send('みつかったよ(｀･ω･´)')
            result_mod = result.replace('みつかったよ\n```','').replace('```','')
            swiutil.writefile_new(result_file_name, result_mod)
            await message.channel.send(file=discord.File(result_file_name))
            os.remove(result_file_name)


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