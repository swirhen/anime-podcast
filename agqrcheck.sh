#!/usr/bin/env bash
# 超A&G予約録画用・ストリーム有効性チェック
# require: rtmpdump
# ストリームURLの有効性をチェックする
# FILE [aandg2] でrtmp取得をチェック
# FILE [aandg] でHLS取得をチェック
# 無効の場合はアラート
# 引数が指定された場合は定時報告する
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
PYTHON_PATH="python3"
FILE_M3U8=${SCRIPT_DIR}/aandg
FILE=${SCRIPT_DIR}/aandg2
REC_FILE=${SCRIPT_DIR}/agqr_rec.mp4

okflg1=0
okflg2=0

PP=`cat ${FILE}`
/usr/bin/rtmpdump --rtmp "rtmpe://fms1.uniqueradio.jp/" --playpath "${PP}" --app "?rtmp://fms-base2.mitene.ad.jp/agqr/" --live -o "${REC_FILE}" --stop 1

if [ -s ${REC_FILE} ]; then
    rm -f ${REC_FILE}
    okflg1=1
else
    rm -f ${REC_FILE}
    /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G チェック】RTMPでの録画にに失敗しました: ${PP}"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G チェック】RTMPでの録画に失敗しました: ${PP}"
fi

PLIST=`cat ${FILE_M3U8}`
/usr/bin/wine ffmpeg3.exe -i "${PLIST}" -c copy -t 10 "${REC_FILE}"

if [ -s ${REC_FILE} ]; then
    rm -f ${REC_FILE}
    okflg2=1
else
    rm -f ${REC_FILE}
    /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G チェック】HLSでの録画にに失敗しました: ${PLIST}"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G チェック】HLSでの録画に失敗しました: ${PLIST}"
fi

if [ "$1" != "" -a ${okflg1} -eq 1 -a ${okflg2} -eq 1 ]; then
    /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G チェック 定時報告】RTMP / HLS 録画URLはともに有効です ${PP} / ${PLIST}"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G チェック 定時報告】RTMP / HLS 録画URLはともに有効です ${PP} / ${PLIST}"
fi