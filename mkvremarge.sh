#!/usr/bin/env zsh
# @author swirhen
# mkvextract、MP4Box -tmp /data/tmpを使ってH264+aacなmkvファイルを
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
    AFMT1=`cat fmt.txt | grep Audio | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
elif [ `cat fmt.txt | grep Audio | wc -l` -eq 2 ]; then
    echo "this is multi track(2) movie!"
    AFMT1=`cat fmt.txt | grep Audio | sed -n 1p | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    AFMT2=`cat fmt.txt | grep Audio | sed -n 2p | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    MLFLG=1
elif [ `cat fmt.txt | grep Audio | wc -l` -eq 3 ]; then
    echo "this is multi track(3) movie!"
    AFMT1=`cat fmt.txt | grep Audio | sed -n 1p | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    AFMT2=`cat fmt.txt | grep Audio | sed -n 2p | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    AFMT3=`cat fmt.txt | grep Audio | sed -n 3p | cut -d"," -f1 | sed "s/\s//g" | cut -d":" -f3`
    MLFLG=2
else
    echo "too many audio tracks..."
    rm fmt.txt
    exit
fi

echo "Audio format1: "$AFMT1
echo "Audio format2: "$AFMT2
echo "Audio format3: "$AFMT3
if [ $AFMT1 = "aac" ]; then
    AEXT1="aac"
elif [ $AFMT1 = "libfaad" ]; then
    AEXT1="aac"
elif [ $AFMT1 = "flac" ]; then
    AEXT1="flac"
elif [ $AFMT1 = "vorbis" ]; then
    AEXT1="ogg"
elif [ $AFMT1 = "mp3" ]; then
    AEXT1="mp3"
elif [ $AFMT1 = "ac3" ]; then
    AEXT1="ac3"
elif [ $AFMT1 = "pcm_s16le" ]; then
    AEXT1="wav"
else
    AEXT1="ac3"
fi
if [ $MLFLG -gt 0 ]; then
  if [ $AFMT2 = "aac" ]; then
      AEXT2="aac"
  elif [ $AFMT2 = "libfaad" ]; then
      AEXT2="aac"
  elif [ $AFMT2 = "flac" ]; then
      AEXT2="flac"
  elif [ $AFMT2 = "vorbis" ]; then
      AEXT2="ogg"
  elif [ $AFMT2 = "mp3" ]; then
      AEXT2="mp3"
  elif [ $AFMT2 = "ac3" ]; then
      AEXT2="ac3"
  elif [ $AFMT2 = "pcm_s16le" ]; then
      AEXT2="wav"
  else
      AEXT2="ac3"
  fi
fi
if [ $MLFLG -eq 2 ]; then
  if [ $AFMT3 = "aac" ]; then
      AEXT3="aac"
  elif [ $AFMT3 = "libfaad" ]; then
      AEXT3="aac"
  elif [ $AFMT3 = "flac" ]; then
      AEXT3="flac"
  elif [ $AFMT3 = "vorbis" ]; then
      AEXT3="ogg"
  elif [ $AFMT3 = "mp3" ]; then
      AEXT3="mp3"
  elif [ $AFMT3 = "ac3" ]; then
      AEXT3="ac3"
  elif [ $AFMT3 = "pcm_s16le" ]; then
      AEXT3="wav"
  else
      AEXT3="ac3"
  fi
fi
echo "Audio Extension1: "$AEXT1
echo "Audio Extension2: "$AEXT2
echo "Audio Extension3: "$AEXT3
rm fmt.txt

mkvextract tracks "$1" 1:video.h264
#ffm -i "$1" -s $VSIZE -vcodec libx264 -b 2500k -r $R -crf 20 -g 230 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -nr 50 -qmin 12 -sc_threshold 65 -bidir_refine 1 -keyint_min 3 -cmp chroma -flags bitexact+alt+mv4+loop -level 30 -threads 0  /tmp/vga/"$1".m4v
if [ $MLFLG -eq 1 ]; then
    mkvextract tracks "$1" 2:audio1.$AEXT1
    mkvextract tracks "$1" 3:audio2.$AEXT2
    if [ $AEXT1 != "aac" ]; then
        ffm -i audio1.$AEXT1 -acodec libfaac -ar 48000 -ab 128k audio1.aac
    fi
    if [ $AEXT2 != "aac" ]; then
        ffm -i audio2.$AEXT2 -acodec libfaac -ar 48000 -ab 128k audio2.aac
    fi
    MP4Box -tmp /data/tmp -fps $FPS -add video.h264 -add audio1.aac -add audio2.aac -new "$NAME.mp4"
elif [ $MLFLG -eq 2 ]; then
    mkvextract tracks "$1" 2:audio1.$AEXT1
    mkvextract tracks "$1" 3:audio2.$AEXT2
    mkvextract tracks "$1" 4:audio3.$AEXT3
    if [ $AEXT1 != "aac" ]; then
        ffm -i audio1.$AEXT1 -acodec libfaac -ar 48000 -ab 128k audio1.aac
    fi
    if [ $AEXT2 != "aac" ]; then
        ffm -i audio2.$AEXT2 -acodec libfaac -ar 48000 -ab 128k audio2.aac
    fi
    if [ $AEXT3 != "aac" ]; then
        ffm -i audio3.$AEXT3 -acodec libfaac -ar 48000 -ab 128k audio3.aac
    fi
    MP4Box -tmp /data/tmp -fps $FPS -add video.h264 -add audio1.aac -add audio2.aac -add audio3.aac -new "$NAME.mp4"
else
    mkvextract tracks "$1" 2:audio1.$AEXT1
    if [ $AEXT1 != "aac" ]; then
        ffm -i audio1.$AEXT1 -acodec libfaac -ar 48000 -ab 128k -ac 2 audio1.aac
    fi
    if [ $# -eq 2 ]; then
      MP4Box -tmp /data/tmp -fps $FPS -add video.h264 -add audio1.aac -add "$2" -new "$NAME.mp4"
    else
      MP4Box -tmp /data/tmp -fps $FPS -add video.h264 -add audio1.aac -new "$NAME.mp4"
    fi
fi
rm video.h264
rm audio*.*
/usr/bin/wine ffmpeg.exe -i "$NAME.mkv" |& grep Duration
/usr/bin/wine ffmpeg.exe -i "$NAME.mp4" |& grep Duration
