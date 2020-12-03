#!/bin/bash
# Install: ffmpeg

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
PATH=$PATH:/usr/local/bin
PYTHON_PATH="python3"
TMP_PATH="/data/tmp"
OUTPUT_PATH="/data/share/movie/98 PSP用/agqr"
FFMPEG_PATH="/usr/bin/wine ffmpeg3.exe"
FFPROBE_PATH="ffprobe"

# 使い方
show_usage() {
  echo "Usage: $COMMAND [-a] [-o bangumi_mei] [-t recording_seconds] station_ID offset"
  echo '       -a  Output area info(ex. 'JP13,東京都,tokyo Japan'). No recording.'
  echo '       -o  Default output_name = /data/tmp/[${station_name}]_`date +%Y%m%d-%H%M`.m4a'
  echo '             "hogehoge" = /data/tmp/[JOQR]hogehoge_20130123-1700.m4a'
  echo '       -t  Default recording_seconds = 30'
  echo '           60 = 1 minute, 3600 = 1 hour, 0 = go on recording until stopped(control-C)'
}

# 引数解析
COMMAND=`basename $0`
while getopts aho:t: OPTION
do
  case $OPTION in
    a ) OPTION_a="TRUE" ;;
    o ) OPTION_o="TRUE" ; VALUE_o="$OPTARG" ;;
    t ) OPTION_t="TRUE" ; VALUE_t="$OPTARG" ;;
    * ) show_usage ; exit 1 ;;
  esac
done

shift $(($OPTIND - 1)) #残りの非オプションな引数のみが、$@に設定される

if [ $# = 0 -a "$OPTION_a" != "TRUE" ]; then
  show_usage ; exit 1
fi

# オプション処理
channel=$1
offset=0
if [ "$2" != "" ]; then
    offset=$2
fi

if [ "$OPTION_o" = "TRUE" ]; then
    pgmname="$VALUE_o"
fi

if [ "$OPTION_t" = "TRUE" ]; then
    rectime=$VALUE_t
fi

station_name=`curl -s "http://radiko.jp/v2/api/program/station/today?station_id=$channel" |/usr/bin/xpath -e "//station/name/text()" 2>/dev/null`
# 保存ファイル名
filename="${TMP_PATH}/【${station_name}】${pgmname}_`date +%Y%m%d-%H%M`}"
# パスを除いたファイル名
efilename="【${station_name}】${pgmname}_`date +%Y%m%d-%H%M`}"

# プレイリストURL、トークン、エリア情報を取得
if [ "${channel}" != "" ]; then
    PLINFO=( `${PYTHON_PATH} ${SCRIPT_DIR}/radikoauth.py ${channel}` )
    m3u8=${PLINFO[0]}
    token=${PLINFO[1]}
else
    PLINFO=( `${PYTHON_PATH} ${SCRIPT_DIR}/radikoauth.py` )
    area="${PLINFO[0]} ${PLINFO[1]}"
fi

if [ "$OPTION_a" = "TRUE" ]; then
    echo "${area}"
    exit 0
fi

# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【Radiko自動録音開始】${station_name} ${pgmname}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【Radiko自動録音開始】${efilename}"

# オフセット
sleep ${offset}

# 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
rectime_rem=${rectime}
file_num="01"
until [ ${rectime_rem} -le 0 ]
do
    filename_rec="${filename}.${file_num}.m4a"
    ${FFMPEG_PATH} -headers "X-Radiko-Authtoken:${token}" -i "${m3u8}" -c copy -t ${rectime_rem} "${filename_rec}"
    mov_duration=`${FFPROBE_PATH} -i "${filename_rec}" -select_streams v:0 -show_entries stream=duration 2>&1 | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"`
    if [ ${mov_duration} -ge ${rectime} ]; then
        break
    fi
    rectime_rem=`expr ${rectime} - ${mov_duration}`
    rectime=${rectime_rem}
    file_num=$(( 10#${file_num} + 1 ))
    file_num_zp="0${file_num}"
    file_num="${file_num_zp: -2}"
done

# 保存フォルダへ移動
cd "${TMP_PATH}"

# ファイルが複数ある場合、リスト作成
filecnt=`ls "${efilename}".*.m4a | wc -l`
if [ ${filecnt} -gt 1 ]; then
    rm -f "list_${efilename}"
    touch "list_${efilename}"
    for file in "${efilename}".*.m4a
    do
        echo "file ${file}" >> "list_${efilename}"
    done
    # 連結
    ${FFMPEG_PATH} -safe 0 -f concat -i "list_${efilename}" "${OUTPUT_PATH}/$efilename.m4a"

    # あとしまつ
    # rm -f "list_${efilename}"
    rm -f "${efilename}".*.m4a
else
    mv "${efilename}".01.m4a "${OUTPUT_PATH}/$efilename.m4a"
fi

# rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"
# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【Radiko自動録音終了】${station_name} ${pgmname}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【Radiko自動録音終了】${efilename}"
