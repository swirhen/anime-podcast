# ニコニコDL
# usage nicodl.sh [URL] [ファイルタイトル] [音声のみフラグ]
# 音声のみフラグがあればmp4からm4a抽出
url=$1
title=$2
audflg=$3

/usr/bin/python /data/share/movie/sh/nicovideo-dl -u swirhen@gmail.com -p irankae1 "${url}" -o nicodl_temp

# 音声エンコ
if [ "${audflg:-null}" != null ]; then
    /usr/bin/wine ffmpeg.exe -i nicodl_temp -acodec libmp3lame -ab 64k -ac 2 -ar 44100 "${title}.mp3"
    rm nicodl_temp
else
    mv nicodl_temp "${title}.mp4"
    echo "${title}.mp4"
fi
