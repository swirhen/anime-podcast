# -*- coding: utf-8 -*-
from socket import gethostname
HOSTNAME=gethostname()

with open('slack_api_token') as apifile:
    API_TOKEN = apifile.read().splitlines()

default_reply = "slackbot ( " + HOSTNAME + " )は起動しています"

PLUGINS = [
    'slackbot_plugins',
]
