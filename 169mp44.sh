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
# いろいろちぇっく
# へんなfpsのどうがのばあい 30000/1001にとういつしてごまかす
fpsfix="-r 30000/1001"
/usr/bin/wine ffmpeg3.exe -i "$1" 2>> /tmp/fps.txt
echo "$1 fps check"
echo `egrep '.*tbr.*' /tmp/fps.txt`
fpsck=`egrep -c '.*(23\.98|29\.97|30\.00|24\.00|25\.00) tbr.*' /tmp/fps.txt`
opt=""
if [ $fpsck -eq 0 ]; then
  echo "# $1 is invalid fps!"
  opt=$fpsfix
fi
# あすぺくとひをじどうはんべつする
echo "$1 aspect check"
echo `egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+' /tmp/fps.txt`
asck=`egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+' /tmp/fps.txt`
asw=`echo $asck | cut -d"," -f3 | cut -d"x" -f1 | sed "s/\s//g"`
ash=`echo $asck | cut -d"," -f3 | cut -d"x" -f2 | sed "s/\s//g"`
echo "width: $asw"
if [ ${#ash} -gt 4 ]; then
  ash=`echo $ash | cut -d"[" -f1`
fi
echo "height: $ash"
# あすぺくとひをじどうはんべつする
aspect=`echo "scale=2; $ash / $asw" | bc`
wide="32:27"
if [ $aspect = ".75" ]; then
	echo "# $1 is 4:3!"
	wide="8:9"
fi
if [ $asw = "1440" -a $ash = "1080" ]; then
	echo "# $1 is 4:3... no! 16:9!"
	wide="32:27"
fi
if [ ${5:-null} = "1" ]; then
  echo "# comp 16:9"
  wide="32:27"
fi
if [ ${5:-null} = "0" ]; then
  echo "# comp 4:3"
  wide="8:9"
fi
size="960x540"
if [ $asw = "640" -a $ash = "480" ]; then
    size="640x480"
    wide="1:1"
fi
if [ $asw = "640" -a $ash = "360" ]; then
    size="640x360"
    wide="1:1"
fi
if [ $asw = "704" -a $ash = "396" ]; then
    size="704x396"
    wide="1:1"
fi
if [ $asw = "704" -a $ash = "400" ]; then
    size="704x396"
    wide="1:1"
fi
if [ $asw = "704" -a $ash = "480" ]; then
    size="704x480"
    wide="40:33"
fi
if [ $asw = "944" -a $ash = "720" ]; then
    size="630x480"
    wide="1:1"
fi
if [ $asw = "1008" -a $ash = "720" ]; then
    size="672x480"
    wide="1:1"
fi
rm /tmp/fps.txt
# えんこする
/usr/bin/wine ffmpeg3.exe -i "$1" $4 -s "$size" -b:v 1500k -vcodec libx264 -trellis 2 -bf 3 -b_strategy 1 -bidir_refine 1 -crf 25 -g 240 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -sc_threshold 65 -keyint_min 3 -nr 100 -qmin 12 -sn -partitions parti4x4+partp4x4+partp8x8 -f mp4 -coder 1 -level 30 -acodec aac -ac 2 -ar 48000 -b:a 128k -async 100 -threads 0 $3 $opt /$drive/tmp/"$1".mp4
#echo "/usr/bin/wine ffmpeg3.exe -i \"$1\" $4 -s \"$size\" -b 1500k -vcodec libx264 -trellis 2 -bf 3 -b_strategy 1 -bidir_refine 1 -crf 25 -g 240 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -sc_threshold 65 -keyint_min 3 -nr 100 -qmin 12 -sn -flags bitexact+alt+mv4+loop -flags2 mixed_refs -partitions parti4x4+partp4x4+partp8x8 -f mp4 -coder 1 -level 30 -acodec libfaac -ac 2 -ar 48000 -ab 128k -async 100 -threads 0 $3 $opt /$drive/tmp/\"$1\".mp4"
# MP4Boxで faststartたいおうにする アスペクトひをしていする
sleep 5
#/usr/local/bin/MP4Box -ipod -par 1="$wide" /$drive/tmp/"$1".mp4 -out /$drive/tmp/"$1"_mod.mp4
#rm /$drive/tmp/"$1".mp4
sleep 5
/bin/mv -v /$drive/tmp/"$1".mp4 "$2""$1".mp4
