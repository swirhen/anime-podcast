# /bin/sh
# @author swirhen
# ffmpegをつかってPSPやあいほんむけのどうがをつくる
# wineをつかってwindowsばんのばいなりをつかってしまう版
# usage:169mp42.sh [infile] [out directory] [encode option]
# どらいぶがちがうどうがのときにtmpをてきせつなばしょにかえる
#if [ $# -gt 1 ]; then
#  drive=`expr "$2" : "\/\(data.\?\)\/.*"`
#else
  tmp=`readlink -f "$PWD"`
  drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
#fi
if [ ${drive:-null} = null ] ; then
  drive=data
fi
# いろいろちぇっく
# へんなfpsのどうがのばあい 30000/1001にとういつしてごまかす
fpsfix="-r 30000/1001"
/usr/bin/ffmpeg -i "$1" 2>> /tmp/fps.txt
echo "$1 fps check"
echo `egrep '.*tbr.*' /tmp/fps.txt`
fpsck=`egrep -c '.*(23\.98|29\.97|30\.00|24\.00|25\.00) tbr.*' /tmp/fps.txt`
opt=""
if [ $fpsck -eq 0 ]; then
  echo "# $1 is invalid fps!"
  opt=$fpsfix
fi
# あすぺくとひをじどうはんべつする
# 4:3だったら360x270にするけど、1440x1080だけはやらない
echo "$1 aspect check"
echo `egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+' /tmp/fps.txt`
asck=`egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+' /tmp/fps.txt`
asw=`echo $asck | cut -d"," -f3 | cut -d"x" -f1 | sed "s/\s//g"`
ash=`echo $asck | cut -d"," -f3 | cut -d"x" -f2 | sed "s/\s//g"`
echo $ash
if [ ${#ash} -gt 4 ]; then
  ash=`echo $ash | cut -d"[" -f1`
fi
echo $ash
# あすぺくとひをじどうはんべつする
aspect=`echo "scale=2; $ash / $asw" | bc`
wide="480"
if [ $aspect = ".75" ]; then
	echo "# $1 is 4:3!"
	wide="360"
fi
if [ $asw = "1440" -a $ash = "1080" ]; then
	echo "# $1 is 4:3... no! 16:9!"
	wide="480"
fi
if [ ${5:-null} = "1" ]; then
  echo "# comp 16:9"
  wide="480"
fi
if [ ${5:-null} = "0" ]; then
  echo "# comp 4:3"
  wide="360"
fi
rm /tmp/fps.txt
# えんこする
/usr/bin/wine ffmpeg.exe -i "$1" $4 -s "$wide"x270 -vcodec libx264 -b 500k -crf 20 -g 230 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -nr 50 -qmin 12 -sc_threshold 65 -bidir_refine 1 -keyint_min 3 -cmp chroma -flags bitexact+alt+mv4+loop -f mp4 -coder 1 -level 13 -acodec libfaac -ac 2 -ar 48000 -ab 128k -threads 0 $3 $opt /$drive/tmp/"$1".mp4
# MP4Boxでfaststartたいおうにする
sleep 5
/usr/local/bin/MP4Box -ipod /$drive/tmp/"$1".mp4
sleep 5
/bin/mv -v /$drive/tmp/"$1".mp4 "$2""$1".mp4
