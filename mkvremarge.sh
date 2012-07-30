#!/usr/bin/env zsh
# @author swirhen
# mkvextract、MP4Boxを使ってH264+aacなmkvファイルを
# mp4ファイルにつめなおす
# 音声がac3とかflacのばあいはさいえんこする
# fpsが可変とかだと死ぬのであきらめる
# usage:mkvremarge.sh [mkv file]
source /home/swirhen/.zshrc
NAME=`echo $1 | cut -d"." -f1`
MLFLG=0
echo $NAME
/usr/bin/wine ffmpeg.exe -i "$1" &> fmt.txt
VSIZE=`cat fmt.txt | grep Video | cut -d"," -f3 | sed "s/\s//g"`
echo $VSIZE
FPS=`cat fmt.txt | grep Video | cut -d"," -f5 | sed "s/^\s//g" | cut -d" " -f1`
echo $FPS
if [ $FPS = "23.98" ]; then
    FPS="23.97605"
    R="24000/1001"
elif [ $FPS = "29.97" ]; then
    FPS="29.970030"
    R="30000/1001"
elif [ $FPS = "24" ]; then
    FPS="23.97605"
    R="24000/1001"
else
    echo "invalid fps!"
    rm fmt.txt
    exit
fi
if [ `cat fmt.txt | grep Audio | wc -l` -eq 1 ]; then
    AFMT=`cat fmt.txt | grep Audio | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
elif [ `cat fmt.txt | grep Audio | wc -l` -eq 2 ]; then
    echo "this is multi track movie!"
    AFMT=`cat fmt.txt | grep Audio | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    MLFLG=1
else
    echo "too many audio tracks..."
    rm fmt.txt
    exit
fi
echo $AFMT
if [ $AFMT = "aac" ]; then
    AEXT="aac"
elif [ $AFMT = "libfaad" ]; then
    AEXT="aac"
elif [ $AFMT = "flac" ]; then
    AEXT="flac"
elif [ $AFMT = "vorbis" ]; then
    AEXT="ogg"
elif [ $AFMT = "mp3" ]; then
    AEXT="mp3"
elif [ $AFMT = "ac3" ]; then
    AEXT="ac3"
elif [ $AFMT = "pcm_s16le" ]; then
    AEXT="wav"
else
    AEXT="ac3"
fi
echo $AEXT
rm fmt.txt
mkvextract tracks "$1" 1:video.h264
#ffm -i "$1" -s $VSIZE -vcodec libx264 -b 2500k -r $R -crf 20 -g 230 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -nr 50 -qmin 12 -sc_threshold 65 -bidir_refine 1 -keyint_min 3 -cmp chroma -flags bitexact+alt+mv4+loop -level 30 -threads 0  /tmp/vga/"$1".m4v
if [ $MLFLG -eq 1 ]; then
    mkvextract tracks "$1" 2:audio1.$AEXT
    mkvextract tracks "$1" 3:audio2.$AEXT
    if [ $AEXT != "aac" ]; then
        ffm -i audio1.$AEXT -acodec libfaac -ar 48000 -ab 128k audio1.aac
        ffm -i audio2.$AEXT -acodec libfaac -ar 48000 -ab 128k audio2.aac
    fi
    MP4Box -fps $FPS -add video.h264 -add audio1.aac -add audio2.aac -new "$NAME.mp4"
else
    mkvextract tracks "$1" 2:audio1.$AEXT
    if [ $AEXT != "aac" ]; then
        ffm -i audio1.$AEXT -acodec libfaac -ar 48000 -ab 128k -ac 2 audio1.aac
    fi
    MP4Box -fps $FPS -add video.h264 -add audio1.aac -new "$NAME.mp4"
fi
rm video.h264
rm audio*.*
ffmpeg -i "$NAME.mkv" |& grep Duration
ffmpeg -i "$NAME.mp4" |& grep Duration
