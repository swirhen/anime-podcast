#!/usr/bin/env bash
# Abema Fresh! 予約録画用スクリプト
# require: curl,ffmpeg
# usage: freshrecord [番組名] [チャンネル名(URL)] [会員配信除外フラグ] [アーカイブフラグ]
# しくみ:
# https://freshlive.tv/[チャンネル名]/programs/upcoming をクロール
# [番組名]の直近のもののIDを取得
# https://movie.freshlive.tv/manifest/[ID]/live.m3u8 を取得
# 最後の行(最高画質のもの)のURLを取得 (/playlist/DDDDDD.m3u8)
# live.m3u8が有効になるのは 20分前なので、1分前に開始すること
# https://movie.freshlive.tv/playlist/DDDDDD.m3u8 をcurlでクロール
# ts を含む行が現れたら、ffmpegで保存開始
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
name=$1
channel=$2
memberonly_ignore_flg=$3
archive_flg=$4
PYTHON_PATH="python3"
DATETIME=`date +"%Y%m%d_%H%M"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
DATE=`date +"%Y%m%d"`
ignoreword='*'
if [ "${memberonly_ignore_flg}" = "1" ]; then
    ignoreword="会員配信"
fi
LOG_FILE=${SCRIPT_DIR}/logs/freshrecord_${DATETIME2}.log
SAVE_DIR="${SCRIPT_DIR}/../98 PSP用/agqr"
ERR_CNT=300

logging() {
  echo "`date '+%Y/%m/%d %H:%M:%S'` $1" >> ${LOG_FILE}
}

logging "### Abema Fresh! 自動録画スクリプト 開始"

# https://freshlive.tv/[チャンネル名]/programs/upcoming をクロール
# [番組名]の直近のもののIDを取得
CRAWL_URI_SUFFIX="onair"
if [ "${archive_flg}" = "1" ]; then
    CRAWL_URI_SUFFIX="archive"
fi
logging "# 番組名:${name} (チャンネル: ${channel}) の放送URL取得開始"
cnt=0
program_id=""
program_name=""
while :
do
    if [ ${cnt} -gt 60 ]; then
        logging "### 放送中IDチェック試行回数エラー: 終了します"
        exit 1
    fi
    streaminfo=`curl https://freshlive.tv/${channel}/programs/${CRAWL_URI_SUFFIX} | sed "s#<a href#\n<a href#g" | sed "s#</a>#</a>\n#g" | grep "^<a href=\"/${channel}/[0-9]" | grep title | grep -v "${ignoreword}" | sed "s#<a href=\"/${channel}/\([^\"]*\)\".*title=\"\([^\"]*\)\".*#\1|\2#" | grep "${name}" | head -1`

    if [ "${streaminfo}" != "" ]; then
        program_id="${streaminfo%|*}"
        program_name="${streaminfo#*|}"
        logging "# ${program_name} の放送中ID: ${program_id}"
        break
    fi
    (( cnt++ ))
    sleep 1
done

# https://movie.freshlive.tv/manifest/[ID]/live.m3u8 を取得
# 最後の行(最高画質のもの)のURLを取得 (/playlist/DDDDDD.m3u8)
# live.m3u8が有効になるのは 20分前なので、1分前に開始すること
STREAM_URI_SUFFIX="live"
if [ "${archive_flg}" = "1" ]; then
    STREAM_URI_SUFFIX="archive"
fi
streamuri="https://movie.freshlive.tv"
streamuri+=`curl "https://movie.freshlive.tv/manifest/${program_id}/${STREAM_URI_SUFFIX}.m3u8" | tail -1`

logging "# 放送URL取得: ${streamuri}"

# https://movie.freshlive.tv/playlist/DDDDDD.m3u8 をcurlでクロール
cnt=0
while :
do
    if [ ${cnt} -gt ${ERR_CNT} ]; then
        logging "### 放送開始チェック試行回数エラー: 終了します"
        exit 1
    fi
    start_flg=`curl "${streamuri}" | grep "ts$" | wc -l`
    if [ "${start_flg}" -gt 0 ]; then
        logging "# 放送開始！"
        break
    fi
    (( cnt++ ))
    sleep 1
done

# ts を含む行が現れたら、ffmpegで保存開始
filename="[FRESH LIVE] ${program_name//\//_} (${DATE}).mp4"
if [ "${archive_flg}" = "1" ]; then
    filename="[FRESH LIVE(archive)] ${program_name//\//_}.mp4"
fi

# つぶやく
# /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【FRESH LIVE自動保存開始】${filename}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【FRESH LIVE自動保存開始】${filename}"

/usr/bin/wine ffmpeg3.exe -i "${streamuri}" -c copy "${SAVE_DIR}"/"${filename}"

# rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"
# つぶやく
# /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【FRESH LIVE自動保存終了】${filename}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【FRESH LIVE自動保存終了】${filename}"

logging "### Abema Fresh! 自動録画スクリプト 終了"
