# /bin/sh
# @author swirhen
# ffmpegをつかってPSPやあいほんむけのどうがをつくる
# wineをつかってwindowsばんのばいなりをつかってしまう版
# あいほん4やNGPなどにたいおうするさくていをほどこした こうかいぞうど版
# usage:169mp43.sh [infile] [out directory] [encode option] [encode option(before)] [force aspect ratio]
# 4つめのひきすうはサイズけっていのまえにえんこーどおぷしょんをつけたいとき
# 5こめのひきすうは"0"だときょうせいてきに4:3 "1"なら16:9となる

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
#/usr/bin/wine ffmpeg.exe -i "$1" $4 -s "320x240" -b 500k -vcodec libx264 -trellis 2 -bf 3 -b_strategy 1 -bidir_refine 1 -crf 25 -g 240 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -sc_threshold 65 -keyint_min 3 -nr 100 -qmin 12 -sn -flags bitexact+alt+mv4+loop -flags2 mixed_refs -partitions parti4x4+partp4x4+partp8x8 -f mp4 -coder 1 -level 30 -acodec libfaac -ac 2 -ar 48000 -ab 96k -async 100 -threads 0 $3 /$drive/tmp/"$1".mp4
# MP4Boxで faststartたいおうにする アスペクトひをしていする
sleep 5
/usr/local/bin/MP4Box -ipod -par 1=1:1 /$drive/tmp/"$1".mp4 -out /$drive/tmp/"$1"_mod.mp4
rm /$drive/tmp/"$1".mp4
sleep 5
/bin/mv -v /$drive/tmp/"$1"_mod.mp4 "$2""$1".mp4
