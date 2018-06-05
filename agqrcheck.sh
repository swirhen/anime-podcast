#!/usr/bin/env bash
# 超A&G予約録画用・ストリーム有効性チェック
# require: rtmpdump
# ストリームURLの有効性をチェックする
# aandg ファイルに書かれた文字列でチェックし、ダメならaandg2 ファイルのものをテスト
# aandg2 ファイルで有効であれば、文字列入れ替え
# 両方無効の場合はアラート
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
PYTHON_PATH="python3"
FILE=${SCRIPT_DIR}/aandg
FILE2=${SCRIPT_DIR}/aandg2
REC_FILE=${SCRIPT_DIR}/agqr_rec

num=`expr $RANDOM % 2 + 1`
PP=`cat ${FILE}`
/usr/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "${PP}" --app "?rtmp://fms-base1.mitene.ad.jp/agqr/" --live -o "${REC_FILE}" --stop 1

if [ -s ${REC_FILE} ]; then
    rm -f ${REC_FILE}
    exit 0
else
    rm -f ${REC_FILE}
    PP2=`cat ${FILE2}`
    /usr/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "${PP2}" --app "?rtmp://fms-base1.mitene.ad.jp/agqr/" --live -o "${REC_FILE}" --stop 1
    if [ -s ${REC_FILE} ]; then
        rm -f ${REC_FILE}
        # エラーだったFILEをFILE2に、成功したPPをFILEに
        echo ${PP} > ${FILE2}
        echo ${PP2} > ${FILE}

        cd /data/share/movie/sh
        git commit -m 'playpath update' ${FILE}
        git commit -m 'playpath2 update' ${FILE2}
        git pull
        git push origin master

        # つぶやく
        /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G playpathチェック】有効playpathが変更されました 旧playpath: ${PP} 新playpath: ${PP2}"
        ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "@here 【超A&G playpathチェック】有効playpathが変更されました 旧playpath: ${PP} 新playpath: ${PP2}"
    else
        # つぶやく
        /home/swirhen/tiasock/tiasock_common.sh "#anigera@w" "【超A&G playpathチェック】エラー：playpathが両方無効になりました playpath: ${PP}、${PP2}"
        ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "@channel 【超A&G playpathチェック】エラー：playpathが両方無効になりました playpath: ${PP}、${PP2}"
    fi
fi