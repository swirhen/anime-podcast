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
PLAYPATH=`cat ${SCRIPT_DIR}/aandg`
PLAYPATH=`cat ${SCRIPT_DIR}/aandg2`

# オフセット
sleep $offset

# 隔週対応
if [ "${recflg:-null}" != null ]; then
flgfile="/data/share/movie/98 PSP用/agqr/flg/$recflg"
    if [ -f "$flgfile" ]; then
        rm "$flgfile"
    else
        touch "$flgfile"
        exit
    fi
fi
# 日付時刻
dt=`date +"%Y%m%d_%H%M"`

# 保存ファイル名
filename="/data/share/movie/98 PSP用/agqr/flv/$dt"_"$name"
# パスを除いたファイル名
efilename="$dt"_"$name"

# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【超A&G自動保存開始】$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G自動保存開始】$efilename"

# 録音時間に満たないファイルが生成されてしまった場合、続きから録音し直す(最終的に録音時間合計に達するまで続ける)
rectime_rem=${rectime}
file_num="01"
until [ ${rectime_rem} -le 0 ]
do
    filename_rec="${filename}.${file_num}.mp4"
    /usr/bin/rtmpdump --rtmp "rtmpe://fms1.uniqueradio.jp/" --playpath "aandg1" --app "?rtmp://fms-base2.mitene.ad.jp/agqr/" --live -o "${filename_rec}" --stop ${rectime_rem}
    # HLS録画(rtmp終了対策)
    #/usr/bin/wine ffmpeg3.exe -i "${PLAYPATH}" -c copy -t ${rectime_rem} "${filename_rec}"
    mov_duration=`ffprobe -i "${filename_rec}" -select_streams v:0 -show_entries stream=duration 2>&1 | grep duration | sed s/duration=// | sed "s/\.[0-9]*$//g"`
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
cd "/data/share/movie/98 PSP用/agqr/flv"

# リスト作成
rm -f "list_${efilename}"
touch "list_${efilename}"
for file in "${efilename}".*.mp4
do
    echo "file ${file}" >> "list_${efilename}"
done

# 映像付きならばエンコード用のシェルを呼ぶ。音声のみならmp3エンコード
if [ "${vidflg}" = "v" ]; then
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp4" ];
    do
        /usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "list_${efilename}" "/data/share/movie/98 PSP用/agqr/$efilename.mp4"
    done
else
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp3" ];
    do
        /usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i "list_${efilename}" -acodec libmp3lame -ab 64k -ac 2 -ar 24000 "/data/share/movie/98 PSP用/agqr/$efilename.mp3"
    done
fi
rm -f "list_${efilename}"

# rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"

# つぶやく
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【超A&G自動保存終了】$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【超A&G自動保存終了】$efilename"
