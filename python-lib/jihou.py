# -*- coding: utf-8 -*-
import sys
import pathlib
import swirhentv_util as su
import bot_util as bu

current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
CHANNEL = 'jihou'
CHANNEL_OPEN = 'ztb_jihou'
NEYOU_FILE = f'{SCRIPT_DIR}/neyou.jpg'


if __name__ == '__main__':
    args = sys.argv
    debug_flg = False
    debug_arg = 25
    here_txt = '@じかんをきにしているひと '
    debug_str = ''
    if len(args) > 1:
        debug_flg = True
        debug_arg = int(args[1])
        here_txt = ''
        debug_str = ' (debugちゅう)'

    hour = int(bu.get_now_datetime_str('H'))
    date = bu.get_now_datetime_str('YMD_A')
    if hour == 0 or debug_arg == 0:
        date = bu.get_now_datetime_str('YMD_A')
        post_str = f'{here_txt}{date} になりました。 {str(hour)} 時ごろをお知らせします。'
    if hour == 0 or debug_arg == 0:
        date = bu.get_now_datetime_str('YMD_A')
        post_str = f'{here_txt}{date} になりました。 {str(hour)} 時ごろをお知らせします。'
    elif hour == 12 or debug_arg == 12:
        post_str = f'{here_txt}{hour} 時ごろをお知らせします。おひるです。'
    elif hour == 15 or debug_arg == 15:
        post_str = f'{here_txt}{hour} 時ごろをお知らせします。おやつです。'
    else:
        if debug_flg:
            hourminute = bu.get_now_datetime_str('HM')
            post_str = f'{here_txt}{hourminute} ごろをお知らせします。'
            print(post_str)
        else:
            post_str = f'{here_txt}{hour} 時ごろをお知らせします。'
    
    su.discord_post(CHANNEL, f'{post_str}{debug_str}')
    su.discord_post(CHANNEL_OPEN, f'{post_str}{debug_str}')
    if hour == 2 or debug_arg == 2:
        su.discord_upload(CHANNEL, NEYOU_FILE)
        su.discord_upload(CHANNEL_OPEN, NEYOU_FILE)
