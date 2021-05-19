# -*- coding: utf-8 -*-
import os
import pathlib
from slackbot.bot import Bot
current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)


def main():
    pid = os.getpid()
    with open(f'{SCRIPT_DIR}/slackbot.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
