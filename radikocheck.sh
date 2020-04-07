#!/usr/bin/env bash
# radiko 地域判定チェック
# require: radikorec.sh
# 地域判定をチェックする
# loc_radiko ファイルに記録
# 変更されている場合はアラート
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
PYTHON_PATH="python3"
FILE=${SCRIPT_DIR}/loc_radiko
TMPFILE=/temp/loc_radiko

${SCRIPT_DIR}/radikorec.sh -a 2>&1 | tail -1 > ${TMPFILE}
DIFF=`diff ${FILE} ${TMPFILE}`

if [ "${DIFF}" != "" ]; then
    # つぶやく
    /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【radiko 地域判定チェック】判定地域が変更されました: `cat ${TMPFILE}`"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "@channel 【radiko 地域判定チェック】判定地域が変更されました: `cat ${TMPFILE}`"
fi