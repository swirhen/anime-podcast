# -*- coding: utf-8 -*-
# import sections
from email.message import Message
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
    
    if message.channel.name == 'bot-sandbox':
        # ホロメン twitter検索
        if re.search('^/hts.*', message.content):
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
                    await message.channel.send(result)
            else:
                await message.channel.send('そのこはここ1週間postがないにぇ(´・ω・`)しんでんで...')
        
        elif re.search('^/sws.*', message.content):
            argument = re.sub(r'^/sws', '', message.content).strip()
            if argument != '':
                await message.channel.send(f'さがしてくるぺこ！(｀・ω・´) 検索キーワード: {argument}')
                result = swiutil.get_feed_xml_list(argument)
                if len(result) > 0:
                    await message.channel.send('みつかったぺこ(｀・ω・´)\n')
                    if result[0] == '1' or result[0] == '2':
                        if result[0] == '1':
                            post_str = 'キーワードはxmlのなまえと一致したぺこ。xmlのさいしん10件を表示するぺこ\n'
                        else:
                            post_str = 'キーワードはxmlのタイトルと一致したぺこ。xmlのさいしん10件を表示するぺこ\n'
                        await message.channel.send(post_str)
                        post_str = '```'
                        for i, item in enumerate(result):
                            if i == 0:
                                continue
                            elif i == 1:
                                post_str += f'タイトル: {item[0]} URL: {item[1]}\n'
                            else:
                                post_str += f'{item}\n'
                        post_str += '```'
                    else:
                        post_str = 'キーワードはxmlのなかのタイトルに一致したぺこ。ヒットしたxmlを表示するぺこ'
                        await message.channel.send(post_str)
                        post_str = '```'
                        for i, item in enumerate(result):
                            if i == 0:
                                continue
                            else:
                                post_str += f'タイトル: {item[0]} URL: {item[1]}\n'
                        post_str += '```'
                    if len(post_str) > 2000:
                        result_file_name = f'{SCRIPT_DIR}/swirhentv_search_{date_time}.txt'
                        swiutil.writefile_new(result_file_name, post_str.replace('`',''))
                        await message.channel.send(file=discord.File(result_file_name))
                        os.remove(result_file_name)
                    else:
                        await message.channel.send(post_str)
                else:
                    await message.channel.send('ねぇぺこ(´・ω・`)\n')
            else:
                await message.channel.send(bu.generate_message('usage_swirhentv_feed_search'))


if __name__ == "__main__":
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/discordbot_ztb.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)
