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
    date_time = bu.get_now_datetime_str('YMDHMS')

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')

    # 種情報
    elif re.search('^/seed.*', message.content):
        past_days = 3
        if len(message.content.split()) > 1:
            past_days = int(message.content.split()[1])
        await message.channel.send(f'あつめた種の情報をおしらせするよ(さいきん {past_days} にちぶん)')
        result = bu.get_seed_directory(past_days)
        if len(result) > 2000:
            result_file_name = f'{SCRIPT_DIR}/seed_info_{date_time}.txt'
            swiutil.writefile_new(result_file_name, result)
            await message.channel.send(file=discord.File(result_file_name))
            os.remove(result_file_name)
        else:
            await message.channel.send(f'```{result}```')

    # 種リスト
    elif re.search('^/tl.*', message.content):
        arguments = message.content.split()
        target_category = ''
        offset_days = '1'
        if len(arguments) > 1:
            target_category = arguments[1]
            if len(arguments) > 2:
                offset_days = arguments[2]
        else:
            await message.channel.send(bu.generate_message('usage_report_seed_list'))
            return

        seed_list = trsc.search_seed_resent(target_category, offset_days)
        if len(seed_list) > 0:
            await message.channel.send(f'さいきんまかれたたねのリストをとってくるしゅば(｀・ω・´)\n'
                                       f'たいしょうカテゴリ: {target_category} ({offset_days} にちまえから)')
            result = ''
            for seed in seed_list:
                result += f'{seed[0]}\n'
            if len(result) > 2000:
                result_file_name = f'{SCRIPT_DIR}/seed_list_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(f'```{result}```')
        else:
            await message.channel.send(f'なんかとれなかったしゅば(´・ω・`)\n')

    # 種サーチ
    elif re.search('^/ts.*', message.content):
        keyword = ''
        target_category = 'all'
        not_dl_flg = ''
        arguments = message.content.split()
        if len(arguments) > 1:
            keyword = arguments[1]
            if len(arguments) > 2:
                target_category = arguments[2]
                if len(arguments) > 3:
                    not_dl_flg = '1'
        else:
            await message.channel.send(bu.generate_message('usage_torrent_search'))
            return
        if target_category == 'all':
            not_dl_flg = '1'
        dl_post_str = ''
        if not_dl_flg != '1':
            dl_post_str = 'ダウンロードもするしゅば(｀・ω・´)'

        await message.channel.send(f'さがしてくるしゅば(｀・ω・´){dl_post_str}\n'
                                   f'たいしょうカテゴリ: {target_category} きーわーど: {keyword}')
        result = bu.seed_search(keyword, target_category, not_dl_flg)
        if re.search('なかったしゅば', result):
            await message.channel.send(result)
        else:
            if len(result) > 2000:
                await message.channel.send('みつかったしゅば(｀・ω・´)')
                result_mod = result.replace('みつかったしゅば(｀・ω・´)\n```', '').replace('```', '')
                result_file_name = f'{SCRIPT_DIR}/seed_search_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result_mod)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(result)

    # 種移動のみ
    elif re.search('^/tmv.*', message.content):
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
            await message.channel.send(bu.generate_message('usage_torrent_move'))
            return

        target_dir = bu.choose_target_dir(target_dir)
        if target_dir == '':
            await message.channel.send(bu.generate_message('usage_torrent_move_directory_choice'))
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
                result_file_name = f'{SCRIPT_DIR}/seed_move_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result)
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(f'```{result}```')

    # 種移動&栽培
    elif re.search('^/tdl.*', message.content):
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
            await message.channel.send(bu.generate_message('usage_torrent_move'))
            return

        target_dir = bu.choose_target_dir(target_dir)
        if target_dir == '':
            await message.channel.send(bu.generate_message('usage_torrent_move_directory_choice'))
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
                result_file_name = f'{SCRIPT_DIR}/seed_move_{date_time}.txt'
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
            await message.channel.send(bu.generate_message('usage_twitter_search'))
            return

        channel = bu.choose_channel(channel)
        if channel == '':
            await message.channel.send(bu.generate_message('usage_twitter_search_channel_choice'))
            return

        since = bu.get_now_datetime_str('YMD_HMS', since)
        until = bu.get_now_datetime_str('YMD_HMS', until)
    
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
                result_file_name = f'{SCRIPT_DIR}/twitter_search_{date_time}.txt'
                swiutil.writefile_new(result_file_name, result.replace('`',''))
                await message.channel.send(file=discord.File(result_file_name))
                os.remove(result_file_name)
            else:
                await message.channel.send(result)
        else:
            await message.channel.send('なかったにぇ(´・ω・`)')

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

        name = bu.get_holomen_twitter_id(name)
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

    # MHRize 期待値計算
    if re.search('^/wex.*', message.content):
        arguments = message.content.split()
        melee = '0'
        sharpness = ''
        attribute = '0'
        crit = '100'
        if len(arguments) > 2:
            melee = arguments[1]
            sharpness = arguments[2]
            if len(arguments) > 3:
                attribute = arguments[3]
                if len(arguments) > 4:
                    crit = int(arguments[4])
        else:
            await message.channel.send(bu.generate_message('usage_mhrize_weapon_expected_value_calc'))
            return
        
        if sharpness in ['y', 'yellow', '黄', '黄色', 'きいろ']:
            sharpness = '黄色'
            melee_mag = 1
            attribute_mag = 0.74
        elif sharpness in ['g', 'green', '緑', 'みどり']:
            sharpness = '緑'
            melee_mag = 1.05
            attribute_mag = 1
        elif sharpness in ['b', 'blue', '青', 'あお']:
            sharpness = '青'
            melee_mag = 1.2
            attribute_mag = 1.0625
        elif sharpness in ['w', 'white', '白', 'しろ']:
            sharpness = '白'
            melee_mag = 1.32
            attribute_mag = 1.15
        elif sharpness in ['p', 'purple', '紫', 'むらさき']:
            sharpness = '紫'
            melee_mag = 1.39
            attribute_mag = 1.2

        if attribute != '':
            attr_str = f' / 属性値: {attribute}'
        if crit != '':
            crit_str = f' / 会心: {crit}%'
            crit_str2 = f' * 会心補正(1 + 0.25 * {int(crit) / 100})'
        post_str = f'[MHRize weapon expected value calculator] (｀・ω・´) 攻撃力: {melee} / 斬れ味: {sharpness}{attr_str}{crit_str}\nの武器の期待値は～\n'
        post_str += f'物理: {round(int(melee) * melee_mag * (1 + (0.25 * {int(crit) / 100})))} ({melee} * 斬れ味補正({str(melee_mag)}){crit_str2})\n'
        post_str += f'属性: {round(int(attribute) * attribute_mag)} ({attribute} * 斬れ味補正({str(attribute_mag)})\n'
        post_str += f'合計 {round(int(melee) * melee_mag * (1 + (0.25 * {int(crit) / 100}))) + round(int(attribute) * attribute_mag)} なのら～'
        await message.channel.send(post_str)

if __name__ == "__main__":
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/discordbot.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)
