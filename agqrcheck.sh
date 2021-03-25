#!/usr/bin/env bash
# 超A&G予約録画用・ストリーム有効性チェック
# ストリームURLの有効性をチェックする
# 無効の場合はアラート
# 引数が指定された場合は定時報告する
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
PYTHON_PATH="python3"
FILE_M3U8=${SCRIPT_DIR}/m3u8_url
REC_FILE=${SCRIPT_DIR}/agqr_rec.mp4

PLIST=`cat ${FILE_M3U8}`
/usr/bin/wine ffmpeg3.exe -i "${PLIST}" -c copy -t 10 "${REC_FILE}"

if [ -s ${REC_FILE} ]; then
    rm -f ${REC_FILE}
    if [ "$1" != "" ]; then
        /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G チェック 定時報告】録画URLは有効です"
        ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G チェック 定時報告】録画URLは有効です"
    fi
else
    rm -f ${REC_FILE}
    /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G チェック】HLSでの録画に失敗しました: ${PLIST}"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G チェック】HLSでの録画に失敗しました: ${PLIST}"
fi