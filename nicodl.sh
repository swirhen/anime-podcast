# �j�R�j�RDL
# usage nicodl.sh [URL] [�t�@�C���^�C�g��] [�����̂݃t���O]
# �����̂݃t���O�������mp4����m4a���o
url=$1
title=$2
audflg=$3

/usr/bin/python /data/share/movie/sh/nicovideo-dl -u swirhen@gmail.com -p irankae1 "${url}" -o nicodl_temp

# �����G���R
if [ "${audflg:-null}" != null ]; then
    /usr/bin/wine ffmpeg.exe -i nicodl_temp -acodec libmp3lame -ab 64k -ac 2 -ar 44100 "${title}.mp3"
    rm nicodl_temp
else
    mv nicodl_temp "${title}.mp4"
fi
