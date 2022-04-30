# -*- coding: utf-8 -*-
# import sections
import random
import sys
import os
import pathlib
import re
import discord
import bot_util as bu

# argument section
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
with open(f'{SCRIPT_DIR}/discord_token_dice') as tokenfile:
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

        # dicebot
    if re.search('^/dice.*', message.content):
        arguments = message.content.split()

        if len(arguments) == 2:
            orders = arguments[1].split('d')
            if len(orders) != 2 or not orders[0].isdecimal() or not orders[1].isdecimal():
                await message.channel.send(bu.generate_message('usage_dice_bot'))
                return
            else:
                count = int(orders[0])
                dice = int(orders[1])
            
            post_str = f'[dice bot] {arguments[1]} を振ります'
            await message.channel.send(post_str)

            results = []
            for i in range(count):
                results.append(random.randint(1,dice))
            
            post_str = '結果： '
            total = 0

            if len(results) <= 10:
                if len(count) > 1 and len(list(set(results))) == 1:
                    post_str += 'repdigit(ゾロ目)!\n'
                else:
                    post_str += '\n'

                for i in range(len(results)):
                    post_str += f'{i + 1}回目 : {results[i]}\n'
                    total += results[i]
            else:
                post_str += '\n'
                for i in range(len(results)):
                    total += results[i]

            post_str += f'合計 : {total}'
                
            await message.channel.send(post_str)

        else:
            await message.channel.send(bu.generate_message('usage_dice_bot'))
            return


if __name__ == "__main__":
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/discordbot_dice.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    # Botの起動とDiscordサーバーへの接続
    client.run(TOKEN)
