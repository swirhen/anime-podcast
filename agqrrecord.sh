#!/usr/bin/env bash
# 超A&G予約録画用スクリプト
# require: rtmpdump,ffmpeg,いろいろ
# usage: agqrrecord.sh [番組名] [開始オフセット] [録画時間] [動画フラグ] [隔週フラグファイル名]
# 番組名: YYYYMMDD_HHMM_番組名.mp4(mp3) というファイルになる
# 開始オフセット: sec
# 録画時間: sec
# 動画フラグ: vなら映像付き、それ以外なら音声と見なしてエンコする
# 隔週フラグファイル名: 
#     フラグファイルがあるかどうかチェックして、なければ作成だけして録画しない
#     あれば削除して録画する
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
name=$1
offset=$2
rectime=$3
vidflg=$4
recflg=$5
PYTHON_PATH="python3"
MODE=hls
#MODE=rtmp
PLAYPATH=`cat ${SCRIPT_DIR}/aandg`
OUTPUT_PATH="/data/share/movie/98 PSP用/agqr"
TMP_PATH="${OUTPUT_PATH}/flv"
FLG_PATH="${OUTPUT_PATH}/flg"

if [ "${MODE}" = "rtmp" ]; then
    PLAYPATH=`cat ${SCRIPT_DIR}/aandg2`
fi

# オフセット
sleep $offset

# 隔週対応
if [ "${recflg:-null}" != null ]; then
flgfile="${FLG_PATH}/$recflg"
    if [ -f "$flgfile" ]; then
        rm "$flgfile"
    else
        touch "$flgfile"
        exit
    fi
fi
# 日付時刻
dt=`date +"%Y%m%d_%H%M"`
dt2=`date +"%Y%m%d%H%M"`

# 保存ファイル名
filename="${TMP_PATH}/$dt"_"$name"
# パスを除いたファイル名
efilename="$dt"_"$name"

# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【超A&G自動保存開始】$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G自動保存開始】$efilename"

# 番組名バリデート
pgmname=`curl https://agqr.sun-yryr.com/api/today | jq -r ".[] | select(.ft == \"${dt2}\") | .title" | sed "s/\!/！/g"`
if [ "${pgmname}" = "" ]; then
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "@channel 【超A&G自動保存】番組表apiからこの時間開始の番組名が取得出来ませんでした。リピート放送の何かに変更されている場合があります。ご確認ください
from arg: ${name}"
fi

if [ "${pgmname}" != "${name}" ]; then
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "@channel 【超A&G自動保存】番組表apiから取得した番組名と指定番組名が違っています。確認してください
from arg: ${name}
from api: ${pgmname}"
fi

# 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
rectime_rem=${rectime}
file_num="01"
until [ ${rectime_rem} -le 0 ]
do
    filename_rec="${filename}.${file_num}.mp4"
    if [ "${MODE}" = "rtmp" ]; then
        /usr/bin/rtmpdump --rtmp "rtmpe://fms1.uniqueradio.jp/" --playpath "aandg1" --app "?rtmp://fms-base2.mitene.ad.jp/agqr/" --live -o "${filename_rec}" --stop ${rectime_rem}
    else
        /usr/bin/wine ffmpeg3.exe -i "${PLAYPATH}" -c copy -t ${rectime_rem} "${filename_rec}"
    fi
    mov_duration=`ffprobe -i "${filename_rec}" -select_streams v:0 -show_entries stream=duration 2>&1 | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"`
    # 取得したファイルが0秒、もしくは録音時間以上なら終わる
    if [ ${mov_duration} -eq 0 -o ${mov_duration} -gt ${rectime} ]; then
        break
    fi
    rectime_rem=`expr ${rectime} - ${mov_duration}`
    # 残り秒数が10秒以下なら完了とする
    if [ ${rectime_rem} -le 10 ]; then
        break
    fi
    rectime=${rectime_rem}
    file_num=$(( 10#${file_num} + 1 ))
    file_num_zp="0${file_num}"
    file_num="${file_num_zp: -2}"
done

# 保存フォルダへ移動
cd "${TMP_PATH}"

# ファイルが複数ある場合、リスト作成し、連結
filecnt=`ls "${efilename}".*.mp4 | wc -l`
if [ ${filecnt} -gt 1 ]; then
    rm -f "list_${efilename}"
    touch "list_${efilename}"

    # ファイル名にスペースが含まれる場合、アンダースコアに変更してからリスト化する
    if [ "`echo ${efilename} | grep ' '`" != "" ]; then
        rename "s/\ /_/g" "${efilename}".*.mp4
    fi
    efilename2="${efilename// /_}"

    for file in "${efilename2}".*.mp4
    do
        echo "file ${file}" >> "list_${efilename}"
    done

    # 連結
    /usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "list_${efilename}" "${efilename}.mp4"
    rm -f "${efilename}".*.mp4
    # rm -f "list_${efilename}"
else
    mv "${efilename}.01.mp4" "${efilename}.mp4"
fi

# 映像付き指定ならば出力ディレクトリにコピー。音声のみ指定なら音声抽出
if [ "${vidflg}" = "v" ]; then
    cp "${efilename}.mp4" "${OUTPUT_PATH}/"
else
    /usr/bin/wine ffmpeg3.exe -i "${efilename}.mp4" -acodec copy -map 0:1 "${OUTPUT_PATH}/${efilename}.m4a"
fi

# rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"

# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【超A&G自動保存終了】$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G自動保存終了】$efilename"
