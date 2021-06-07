#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.error, urllib.parse
import re
import base64
from sys import argv

auth_token = ""
auth_key = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
key_lenght = 0
key_offset = 0


def auth1():
    url = "https://radiko.jp/v2/api/auth1"
    headers = {}
    auth_response = {}

    headers = {
        "User-Agent": "curl/7.56.1",
        "Accept": "*/*",
        "X-Radiko-App": "pc_html5",
        "X-Radiko-App-Version": "0.0.1",
        "X-Radiko-User": "dummy_user",
        "X-Radiko-Device": "pc",
    }
    req = urllib.request.Request(url, None, headers)
    try:
        res = urllib.request.urlopen(req)
    except Exception as e:
        print(e)
    else:
        auth_response["body"] = res.read()
        auth_response["headers"] = res.info()
    return auth_response


def get_partial_key(auth_response):
    authtoken = auth_response["headers"]["x-radiko-authtoken"]
    offset = auth_response["headers"]["x-radiko-keyoffset"]
    length = auth_response["headers"]["x-radiko-keylength"]
    offset = int(offset)
    length = int(length)
    partialkey = auth_key[offset:offset + length]
    partialkey = base64.b64encode(partialkey.encode())

    # logging.info(f"authtoken: {authtoken}")
    # logging.info(f"offset: {offset}")
    # logging.info(f"length: {length}")
    # logging.info(f"partialkey: {partialkey}")

    return [partialkey, authtoken]


def auth2(partialkey, auth_token):
    url = "https://radiko.jp/v2/api/auth2"
    area = ''
    headers = {
        "X-Radiko-AuthToken": auth_token,
        "X-Radiko-Partialkey": partialkey,
        "X-Radiko-User": "dummy_user",
        "X-Radiko-Device": 'pc'
    }
    req = urllib.request.Request(url, None, headers)
    try:
        res = urllib.request.urlopen(req)
    except Exception as e:
        print(e)
    else:
        txt = res.read()
        area = txt.decode()
    return area


def gen_temp_chunk_m3u8_url(url, auth_token):
    headers = {
        "X-Radiko-AuthToken": auth_token,
    }
    req = urllib.request.Request(url, None, headers)
    try:
        res = urllib.request.urlopen(req)
    except Exception as e:
        print(e)
        return ''
    else:
        body = res.read().decode()
        lines = re.findall('^https?://.+m3u8$', body, flags=(re.MULTILINE))
        # embed()
        return lines[0]


def main(station_id=''):
    res = auth1()
    ret = get_partial_key(res)
    token = ret[1]
    partialkey = ret[0]
    area = auth2(partialkey, token)
    if station_id != '':
        url = f'http://f-radiko.smartstream.ne.jp/{station_id}/_definst_/simul-stream.stream/playlist.m3u8'
        m3u8 = gen_temp_chunk_m3u8_url(url, token)
        info = [m3u8, token]
    else:
        info = [area]

    return info


if __name__ == '__main__':
    if len(argv) > 1:
        info = main(argv[1])
        print(f'{info[0]} {info[1]}')
    else:
        info = main()
        print(info[0])
