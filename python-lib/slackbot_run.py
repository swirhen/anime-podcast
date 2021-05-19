# -*- coding: utf-8 -*-
import os
from slackbot.bot import Bot


def main():
    pid = os.getpid()
    with open(os.getcwd() + '/slackbot.pid', 'w') as pidfile:
        pidfile.write(str(pid))
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
