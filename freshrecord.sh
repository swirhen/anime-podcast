#!/usr/bin/env bash
# Abema FRESH LIVE! 予約録画用スクリプト
# require: curl,ffmpeg
# usage: freshrecord [番組名] [チャンネル名(URL)] [会員配信除外フラグ] [アーカイブフラグ] [音声エンコードフラグ]
# しくみ:
# https://freshlive.tv/[チャンネル名]/programs/onair をクロール
# [番組名]の直近のもののIDを取得
# https://movie.freshlive.tv/manifest/[ID]/live.m3u8 を取得
# 最後の行(最高画質のもの)のURLを取得 (/playlist/DDDDDD.m3u8)
# live.m3u8が有効になるのは 20分前なので、1分前に開始すること
# https://movie.freshlive.tv/playlist/DDDDDD.m3u8 をcurlでクロール
# ts を行末に含む行が現れたら、ffmpegで保存開始
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
name=$1
channel=$2
memberonly_ignore_flg=$3
archive_flg=$4
audio_flg=$5
PYTHON_PATH="python3"
DATETIME=`date +"%Y%m%d_%H%M"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
DATE=`date +"%Y%m%d"`
IGNORE_WORD='*'
if [ "${memberonly_ignore_flg}" = "1" ]; then
    IGNORE_WORD="会員配信"
fi
LOG_FILE=${SCRIPT_DIR}/logs/freshrecord_${DATETIME2}.log
SAVE_DIR="${SCRIPT_DIR}/../98 PSP用/agqr"
ERR_CNT1=120
ERR_CNT2=120

logging() {
  #echo "`date '+%Y/%m/%d %H:%M:%S'` $1" >> ${LOG_FILE}
  echo "`date '+%Y/%m/%d %H:%M:%S'` $1" | tee -a ${LOG_FILE}
}

logging "### FRESH LIVE! 自動録画スクリプト 開始"

# https://freshlive.tv/[チャンネル名]/programs/onair をクロール
# [番組名]の直近のもののIDを取得
CRAWL_URI_SUFFIX="onair"
if [ "${archive_flg}" = "1" ]; then
    CRAWL_URI_SUFFIX="archive"
fi

logging "# 番組名:${name} (チャンネル: ${channel}) の放送中URL取得開始"
cnt=1
program_id=""
program_name=""
while :
do
    logging "# 放送中URLチェック 試行: ${cnt}"
    if [ ${cnt} -gt ${ERR_CNT1} ]; then
        logging "### 放送中URLチェック 試行回数エラー: 終了します"
        exit 1
    fi
    streaminfo=`curl https://freshlive.tv/${channel}/programs/${CRAWL_URI_SUFFIX} | sed "s#<a href#\n<a href#g" | sed "s#</a>#</a>\n#g" | grep "^<a href=\"/${channel}/[0-9]" | grep title | grep -v "${IGNORE_WORD}" | sed "s#<a href=\"/${channel}/\([^\"]*\)\".*title=\"\([^\"]*\)\".*#\1|\2#" | grep "${name}" | head -1`
    # archiveでない場合、upcomingからも取得してみる
    if [ "${streaminfo}" = "" -a "${archive_flg}" != "1" ]; then
        logging "# /onair から取得できず: /upcoming から取得試行"
        streaminfo=`curl https://freshlive.tv/${channel}/programs/upcoming | sed "s#<a href#\n<a href#g" | sed "s#</a>#</a>\n#g" | grep "^<a href=\"/${channel}/[0-9]" | grep title | grep -v "${IGNORE_WORD}" | sed "s#<a href=\"/${channel}/\([^\"]*\)\".*title=\"\([^\"]*\)\".*#\1|\2#" | grep "${name}" | head -1`
    fi

    if [ "${streaminfo}" != "" ]; then
        program_id="${streaminfo%|*}"
        program_name="${streaminfo#*|}"
        logging "# ${program_name} の放送中URLのID: ${program_id}"
        break
    fi
    (( cnt++ ))
    sleep 1
done

# https://movie.freshlive.tv/manifest/[ID]/live.m3u8 を取得
# 最後の行(最高画質のもの)のURLを取得 (/playlist/DDDDDD.m3u8)
# live.m3u8が有効になるのは 20分前なので、1分前に開始すること
STREAM_URI_FILENAME="live"
if [ "${archive_flg}" = "1" ]; then
    STREAM_URI_FILENAME="archive"
fi

streamuri="https://movie.freshlive.tv"
streamuri+=`curl "https://movie.freshlive.tv/manifest/${program_id}/${STREAM_URI_FILENAME}.m3u8" | tail -1`

logging "# 放送URL取得: ${streamuri}"

# https://movie.freshlive.tv/playlist/DDDDDD.m3u8 をクロール
cnt=1
while :
do
    logging "# 放送開始チェック 試行: ${cnt}"
    if [ ${cnt} -gt ${ERR_CNT2} ]; then
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

# ts を行末に含む行が現れたら、ffmpegで保存開始
filename="[FRESH LIVE] ${program_name//\//_} (${DATE})"
if [ "${archive_flg}" = "1" ]; then
    filename="[FRESH LIVE(archive)] ${program_name//\//_}"
fi

# つぶやく(開始報告)
# /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【FRESH LIVE自動保存開始】${filename}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【FRESH LIVE自動保存開始】${filename}"

/usr/bin/wine ffmpeg3.exe -i "${streamuri}" -c copy "${SCRIPT_DIR}/${filename}.mp4"

if [ "${audio_flg}" = "1" ] then
    /usr/bin/wine ffmpeg3.exe -i "${filename}.mp4" -acodec copy -map 0:1 "${filename}.m4a"
    mv "${SCRIPT_DIR}/${filename}.mp4" "${SAVE_DIR}"/mp4/
    mv "${SCRIPT_DIR}/${filename}.m4a" "${SAVE_DIR}"/
else
    mv "${SCRIPT_DIR}/${filename}.mp4" "${SAVE_DIR}"/
fi

# swirhen.tv rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"

# つぶやく(終了報告)
# /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【FRESH LIVE自動保存終了】${filename}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【FRESH LIVE自動保存終了】${filename}"

logging "### FRESH LIVE! 自動録画スクリプト 終了"
