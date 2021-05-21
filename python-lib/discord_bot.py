# -*- coding: utf-8 -*-
# import sections
import pathlib
import re
import discord
import bot_util as bu

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
        print(len(result))
        await message.channel.send(result)


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)