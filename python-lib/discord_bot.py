# -*- coding: utf-8 -*-
# import sections
import pathlib
import re
import discord

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
            past_days = message.content.split()[1]
        announce_seed_info(past_days)


# 最近の自動取得seed問い合わせ
def announce_seed_info(past_days):
    return_message = ''
    return_message += f'あつめた種の情報をおしらせするよ(さいきん{past_days}にちぶん)\n'
    paths = sorted(list(pathlib.Path(SEED_DOWNLOAD_DIR).glob('2*')), reverse=True)
    get_paths = paths[:past_days]
    seed_info = dict()
    for get_path in get_paths:
        if not get_path.name in seed_info:
            seed_info[get_path.name] = []

        seed_list = list(pathlib.Path(get_path).glob('*'))
        for seed in seed_list:
            seed_info[get_path.name].append(seed.name)

    return_message += '```'
    for dir in seed_info:
        return_message += f'directory {dir} in seeds:\n'
        for seed in seed_info[dir]:
            return_message += f'    {seed}\n'
    return_message += '```'

    return return_message


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)