# -*- coding: utf-8 -*-
# import sections
import sys
import os
import pathlib
import re
import discord
import bot_util as bu
import swirhentv_util as swiutil
sys.path.append('/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as trsc

# argument section
SHARE_TEMP_DIR = '/data/share/temp'
SEED_DOWNLOAD_DIR = f'{SHARE_TEMP_DIR}/torrentsearch'
SEED_BACKUP_DIR = f'{SHARE_TEMP_DIR}/torrentsearch/downloaded'
DL_URL_LIST_FILE = f'/home/swirhen/sh/checker/torrentsearch/download_url.txt'
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
with open(f'{SCRIPT_DIR}/discord_token_ztb') as tokenfile:
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
    date_time = bu.get_now_datetime_str('YMDHMS')

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    
    # ホロメン twitter検索
    elif re.search('^/hts.*', message.content):
        arguments = message.content.split()
        name = ''
        count = '5'
        if len(arguments) > 1:
            name = arguments[1]
            if len(arguments) > 2:
                count = arguments[2]
        else:
            await message.channel.send(bu.generate_message('usage_holomen_twitter_search'))
            return

        name = bu.get_holomen_twitter_id(name)
        await message.channel.send(f'さがすにぇ(｀・ω・´)\ntarget twitter id: {name}')

        result = bu.twitter_search2(name, count)

        if len(result) > 0:
            await message.channel.send('みつかったにぇ！(｀・ω・´)')
            if len(result) > 2000:
                result_file_name = f'{SCRIPT_DIR}/twitter_search2_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result.replace('`',''))
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(result.replace('```','`'))
        else:
            await message.channel.send('そのこはここ1週間postがないにぇ(´・ω・`)しんでんで...')


if __name__ == "__main__":
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/discordbot_ztb.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)
