# -*- coding: utf-8 -*-
import pathlib
from socket import gethostname
HOSTNAME=gethostname()
current_dir = pathlib.Path(__file__).resolve().parent

with open(f'{str(current_dir)}/slack_api_token') as apifile:
    API_TOKEN = apifile.read().splitlines()[0]

default_reply = "slackbot ( " + HOSTNAME + " )は起動しています"

PLUGINS = [
    'slackbot_plugins',
]
