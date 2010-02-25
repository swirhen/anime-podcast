# /bin/sh
# @author swirhen
# mkvextract、MP4Boxを使ってH264+aacなmkvファイルを
# mp4ファイルにつめなおす
# 音声がac3とかflacのばあいはコメントアウトしてあるところをつかう
# fpsが可変とかだと死ぬのであきらめる
# usage:mkvremarge.sh [mkv file]
NAME=`echo $1 | cut -d"." -f1`
echo $NAME
mkvextract tracks "$1" 1:video.h264
mkvextract tracks "$1" 2:audio.aac
#/usr/local/bin/ffmpeg -i audio.ac3 -acodec libfaac -ar 48000 -ab 128k audio.aac
MP4Box -fps 23.976025 -add video.h264 -add audio.aac -new "$NAME.mp4"
#MP4Box -fps 29.970030 -add video.h264:par=10:11 -add audio.aac -new "$NAME.mp4"
#MP4Box -fps 29.970030 -add video.h264 -add audio.aac -new "$NAME.mp4"
#MP4Box -fps 30.00 -add video.h264 -add audio.aac -new "$NAME.mp4"
rm video.h264
rm audio.*
