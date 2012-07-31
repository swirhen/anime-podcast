# /bin/sh
# @author swirhen
# ffmpegをつかってPSPやあいほんむけのどうがをつくる
# wineをつかってwindowsばんのばいなりをつかってしまう版
# ぶんかほうそう ちょーA&Gせんよう てきとうえんこばーじょん
# usage:169mp4_agqr.sh [infile] [out directory]

# どらいぶがちがうどうがのときにtmpをてきせつなばしょにかえる
# じっこうでぃれくとりから ドライブをはんだん
tmp=`readlink -f "$PWD"`
drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
# しゅつりょくさきがしていされてるばあい そっち
if [ "${2:-null}" != null -o "${2:-null}" != "" ]; then
  tmp=`readlink -f "$2"`
  drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
fi
# わからないばあいは /data
if [ ${drive:-null} = null ] ; then
  drive=data
fi
# えんこする
/usr/bin/wine ffmpeg.exe -i "$1" -vcodec copy -f mp4 -acodec libfaac -ac 2 -ar 24000 -ab 64k -threads 0 $3 /$drive/tmp/"$1".mp4
# MP4Boxで faststartたいおうにする
sleep 5
/usr/local/bin/MP4Box -ipod -par 1=1:1 /$drive/tmp/"$1".mp4 -out /$drive/tmp/"$1"_mod.mp4
rm /$drive/tmp/"$1".mp4
sleep 5
/bin/mv -v /$drive/tmp/"$1"_mod.mp4 "$2""$1".mp4
