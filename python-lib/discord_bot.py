# -*- coding: utf-8 -*-
# import sections
import sys
import os
import pathlib
import re
from datetime import datetime as dt
import datetime
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
    elif re.search('^/seed.*', message.content):
        tdatetime = dt.now()
        date_time = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_info_{date_time}.txt'
        past_days = 3
        if len(message.content.split()) > 1:
            past_days = int(message.content.split()[1])
        await message.channel.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
        result = bu.get_seed_directory(past_days)
        if len(result) > 2000:
            swiutil.writefile_new(result_file_name, result)
            await message.channel.send(file=discord.File(result_file_name))
            os.remove(result_file_name)
        else:
            await message.channel.send(f'```{result}```')

    # 種リスト
    elif re.search('^/tl.*', message.content):
        tdatetime = dt.now()
        date_time = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_list_{date_time}.txt'
        target_category = ''
        arguments = message.content.split()
        if len(arguments) > 1:
            target_category = arguments[1]
        else:
            await message.channel.send('つかいかた(´・ω・`)\n'
                                       'tl [たいしょうカテゴリ]\n'
                                       'カテゴリ: doujin/manga/music/comic/live\n'
                                       '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ)')
            return

        seed_list = trsc.get_seed_list(target_category)
        if len(seed_list) > 0:
            await message.channel.send(f'さいきんまかれたたねのリストだよ(｀・ω・´)\n'
                                       f'たいしょうカテゴリ: {target_category}')
            result = ''
            for seed in seed_list:
                result += f'{seed[1]}\n'
            if len(result) > 2000:
                swiutil.writefile_new(result_file_name, result)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(f'```{result}```')
        else:
            await message.channel.send(f'なんかとれなかったよ(´・ω・`)\n')

    # 種サーチ
    elif re.search('^/ts.*', message.content):
        tdatetime = dt.now()
        date_time = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_search_{date_time}.txt'
        keyword = ''
        target_category = 'all'
        arguments = message.content.split()
        if len(arguments) > 1:
            keyword = arguments[1]
            if len(arguments) > 2:
                target_category = arguments[2]
        else:
            await message.channel.send('つかいかた(´・ω・`)\nts [けんさくキーワード] [たいしょうカテゴリ]\n'
                                       'カテゴリ: doujin/manga/music/comic/live/all\n'
                                       '(どうじん/えろまんが/おんがく/いっぱんまんが/らいぶ/ぜんぶ)')
            return

        await message.channel.send('さがしてくるよ(｀・ω・´)\n'
                                  f'たいしょうカテゴリ: {target_category} きーわーど: {keyword}')
        result = bu.seed_search(keyword, target_category)
        if re.search('なかったよ', result):
            await message.channel.send(result)
        else:
            if len(result) > 2000:
                await message.channel.send('みつかったよ(｀・ω・´)')
                result_mod = result.replace('みつかったよ(｀・ω・´)\n```', '').replace('```', '')
                swiutil.writefile_new(result_file_name, result_mod)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(result)

    # 種移動のみ
    elif re.search('^/tmv.*', message.content):
        tdatetime = dt.now()
        date_time = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_move_{date_time}.txt'
        arguments = message.content.split()
        seed_dir = ''
        target_dir = ''
        keyword = ''
        if len(arguments) > 2:
            seed_dir = arguments[1]
            target_dir = arguments[2]
            if len(arguments) > 3:
                keyword = arguments[3]
        else:
            await message.channel.send('つかいかた(´・ω・`)\n'
                                       'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n'
                                       'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n'
                                       'いどうさきディレクトリ:\n'
                                       'd: どうじん c: みせいりほん m: えろまんが\n'
                                       'cm: でれおんがく cl: でれらいぶ\n'
                                       'mm: みりおんがく ml:みりらいぶ\n'
                                       'sm:しゃにおんがく sl:しゃにらいぶ\n'
                                       'hm:ほろおんがく hl:ほろらいぶ\n'
                                       'もしくは ふるぱすもじれつ')

        target_dir = bu.choose_target_dir(target_dir)
        if target_dir == '':
            message.send('いどうさきディレクトリ:\n'
                         'd: どうじん c: みせいりほん m: えろまんが\n'
                         'cm: でれおんがく cl: でれらいぶ\n'
                         'mm: みりおんがく ml:みりらいぶ\n'
                         'sm:しゃにおんがく sl:しゃにらいぶ\n'
                         'hm:ほろおんがく hl:ほろらいぶ\n'
                         'もしくは ふるぱすもじれつ')
            return

        result = bu.seed_move(seed_dir, target_dir, keyword)
        await message.channel.send(result)
        seedlist = bu.get_seeds_list(target_dir)
        if len(seedlist) == 0:
            await message.channel.send('たねがみつからなかったよ(´・ω・`)')
            return
        else:
            await message.channel.send('いどうしたたね:')
            result = '\n'.join(seedlist)
            if len(result) > 2000:
                swiutil.writefile_new(result_file_name, result)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(f'```{result}```')

    # 種移動&栽培
    elif re.search('^/tdl.*', message.content):
        tdatetime = dt.now()
        date_time = tdatetime.strftime('%Y%m%d%H%M%S')
        result_file_name = f'{SCRIPT_DIR}/seed_move_{date_time}.txt'
        arguments = message.content.split()
        seed_dir = ''
        target_dir = ''
        keyword = ''
        if len(arguments) > 2:
            seed_dir = arguments[1]
            target_dir = arguments[2]
            if len(arguments) > 3:
                keyword = arguments[3]
        else:
            await message.channel.send('つかいかた(´・ω・`)\n'
                                       'tdl [たねのあるディレクトリ] [いどうさきのディレクトリ] [いどうするたねをしぼりこむキーワード]\n'
                                       'いどうもとディレクトリ: ひづけ(YYYYMMDD) もしくは t(きょうのひづけ)\n'
                                       'いどうさきディレクトリ:\n'
                                       'd: どうじん c: みせいりほん m: えろまんが\n'
                                       'cm: でれおんがく cl: でれらいぶ\n'
                                       'mm: みりおんがく ml:みりらいぶ\n'
                                       'sm:しゃにおんがく sl:しゃにらいぶ\n'
                                       'hm:ほろおんがく hl:ほろらいぶ\n'
                                       'もしくは ふるぱすもじれつ')

        target_dir = bu.choose_target_dir(target_dir)
        if target_dir == '':
            message.send('いどうさきディレクトリ:\n'
                         'd: どうじん c: みせいりほん m: えろまんが\n'
                         'cm: でれおんがく cl: でれらいぶ\n'
                         'mm: みりおんがく ml:みりらいぶ\n'
                         'sm:しゃにおんがく sl:しゃにらいぶ\n'
                         'hm:ほろおんがく hl:ほろらいぶ\n'
                         'もしくは ふるぱすもじれつ')
            return

        result = bu.seed_move(seed_dir, target_dir, keyword)
        await message.channel.send(result)

        # 栽培
        seedlist = bu.get_seeds_list(target_dir)
        if len(seedlist) == 0:
            await message.channel.send('たねがみつからなかったよ(´・ω・`)')
            return
        else:
            await message.channel.send('いどうしたたね:')
            result = '\n'.join(seedlist)
            if len(result) > 2000:
                swiutil.writefile_new(result_file_name, result)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(f'```{result}```')

        await message.channel.send('さいばいをかいしするよ(｀・ω・´)')

        bu.plant_seed(target_dir)

        await message.channel.send('おわったよ(｀・ω・´)')

    # twitter検索
    elif re.search('^/tws.*', message.content):
        arguments = message.content.split()
        if len(arguments) == 7:
            keyword = arguments[1]
            channel = arguments[2]
            since = arguments[3]
            until = arguments[4]
            nick_flg = arguments[5]
            your_nick_ignore_flg = arguments[6]
        else:
            await message.channel.send('つかいかた(´・ω・`)\n'
                                       'tws [けんさくキーワード or twitterid] [チャンネル] [けんさくかいしにちじ] [けんさくしゅうりょうにちじ] [twitteridでけんさく] [じぶんのtwitteridをむしする]\n'
                                       'チャンネル: y/s/k/e/f/c/m/h/ha\n'
                                       '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)\n'
                                       'けんさくかいしにちじ: YYYY-MM-DD HH:MM:SSけいしき\n'
                                       'もしくは [なんふんまえ]m/[なんじかんまえ]h/[なんにちまえ]d\n'
                                       'けんさくしゅうりょうにちじ: nowといれたら げんざいにちじ\n'
                                       'twitteridでけんさく: 0: キーワードけんさく 1: twitteridでけんさく\n'
                                       'じぶんのtwitteridをむしする: 0: むしする 1: むししない')
            return

        if channel == 'y':
            channel = '#Twitter有名人@t'
        elif channel == 's':
            channel = '#twitter声優@t'
        elif channel == 'k':
            channel = '#twitter格ゲー@t'
        elif channel == 'e':
            channel = '#twitter絵描きさん@t'
        elif channel == 'f':
            channel = '#おともだちtwitter@t'
        elif channel == 'c':
            channel = '#シンデレラ一門@t'
        elif channel == 'm':
            channel = '#ミリオン一座@t'
        elif channel == 'h':
            channel = '#hololive@t'
        elif channel == 'ha':
            channel = '#holoart@t'
        else:
            message.send('チャンネル: y/s/k/e/f/c/m/h/ha\n'
                         '(ゆうめいじん/せいゆう/かくげーぜい/えし/おともだち/いちもん/いちざ/ほろ/ほろのえ)\n')
            return 1
    
        now_time = dt.now()
        now_datetime = dt.now().strftime('%Y/%m/%d %H:%M:%S')
        if since[-1] == 'm':
            shift_minutes = int(since[:-1])
            since = (now_time - datetime.timedelta(minutes=int(shift_minutes))).strftime('%Y/%m/%d %H:%M:%S')
        elif since[-1] == 'h':
            shift_hours = int(since[:-1])
            since = (now_time - datetime.timedelta(hours=int(shift_hours))).strftime('%Y/%m/%d %H:%M:%S')
        elif since[-1] == 'd':
            shift_days = int(since[:-1])
            since = (now_time - datetime.timedelta(days=int(shift_days))).strftime('%Y/%m/%d %H:%M:%S')
    
        if until[-1] == 'm':
            shift_minutes = int(until[:-1])
            until = (now_time - datetime.timedelta(minutes=int(shift_minutes))).strftime('%Y/%m/%d %H:%M:%S')
        elif until[-1] == 'h':
            shift_hours = int(until[:-1])
            until = (now_time - datetime.timedelta(hours=int(shift_hours))).strftime('%Y/%m/%d %H:%M:%S')
        elif until[-1] == 'd':
            shift_days = int(until[:-1])
            until = (now_time - datetime.timedelta(days=int(shift_days))).strftime('%Y/%m/%d %H:%M:%S')
        elif until == 'now':
            until = now_datetime
    
        k_n_str = 'キーワード'
        k_n_i_str = 'むしする'
        if nick_flg == '1':
            nick_flg = True
            k_n_str = 'twitterid'
        else:
            nick_flg = False
        if your_nick_ignore_flg == '1':
            your_nick_ignore_flg = False
            k_n_i_str = 'むししない'
        else:
            your_nick_ignore_flg = True
    
        post_str = f'けんさくするにぇ(｀・ω・´)\n' \
                   f'{k_n_str}: {keyword} チャンネル: {channel}\n' \
                   f'いつから: {since} いつまで: {until}\n' \
                   f'じぶんのtwitteridをむしする: {k_n_i_str}'

        await message.channel.send(post_str)
        result = bu.twitter_search(keyword, channel, since, until, your_nick_ignore_flg, nick_flg)
        if len(result) > 0:
            await message.channel.send('みつかったにぇ！(｀・ω・´)')
            if len(result) > 2000:
                tdatetime = dt.now()
                date_time = tdatetime.strftime('%Y%m%d%H%M%S')
                result_file_name = f'{SCRIPT_DIR}/twitter_search_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result.replace('`',''))
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(result)
        else:
            await message.channel.send('なかったにぇ(´・ω・`)')


if __name__ == "__main__":
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/discordbot.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)
