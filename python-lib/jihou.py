# -*- coding: utf-8 -*-
import sys
import swirhentv_util as su
import bot_util as bu

CHANNEL = 'ztb_jihou'


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        debug = True

    hour = int(bu.get_now_datetime_str('H'))
    date = bu.get_now_datetime_str('YMD_A')
    if hour == 0:
        date = bu.get_now_datetime_str('YMD_A')
        post_str = f'@here {date} になりました。 {str(hour)} 時ごろをお知らせします。'
    elif hour == 12:
        post_str = f'@here {hour} 時ごろをお知らせします。おひるです。'
    elif hour == 15:
        post_str = f'@here {hour} 時ごろをお知らせします。おやつです。'
    else:
        if debug:
            hourminute = bu.get_now_datetime_str('HM')
            post_str = f'@here {hourminute} ごろをお知らせします。(debug mode)'
            print(post_str)
            exit(0)
        else:
            post_str = f'@here {hour} 時ごろをお知らせします。'
    
    su.discord_post(CHANNEL, post_str)
