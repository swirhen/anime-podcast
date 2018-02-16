# /bin/sh
# @author swirhen
# ffmpegÇÇ¬Ç©Ç¡ÇƒPSPÇ‚Ç†Ç¢ÇŸÇÒÇﬁÇØÇÃÇ«Ç§Ç™ÇÇ¬Ç≠ÇÈ
# usage:169mp4.sh [infile] [out directory] [encode option]
# Ç«ÇÁÇ¢Ç‘Ç™ÇøÇ™Ç§Ç«Ç§Ç™ÇÃÇ∆Ç´Ç…tmpÇÇƒÇ´ÇπÇ¬Ç»ÇŒÇµÇÂÇ…Ç©Ç¶ÇÈ
tmp=`readlink -f "$PWD"`
drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
if [ ${drive:-null} = null ] ; then
  drive=data
fi
# Ç¢ÇÎÇ¢ÇÎÇøÇ•Ç¡Ç≠
# Ç÷ÇÒÇ»fpsÇÃÇ«Ç§Ç™ÇÃÇŒÇ†Ç¢ 30000/1001Ç…Ç∆Ç§Ç¢Ç¬ÇµÇƒÇ≤Ç‹Ç©Ç∑
fpsfix="-r 30000/1001"
/usr/bin/ffmpeg -i "$1" 2>> /tmp/fps.txt
echo "$1 fps check"
echo `egrep '.*fps.*' /tmp/fps.txt`
fpsck=`egrep -c '.*(23\.98|29\.97|30\.00|24\.00|25\.00) fps.*' /tmp/fps.txt`
opt=""
if [ $fpsck -eq 0 ]; then
  echo "# $1 is invalid fps!"
  opt=$fpsfix
fi
# Ç†Ç∑ÇÿÇ≠Ç∆Ç–ÇÇ∂Ç«Ç§ÇÕÇÒÇ◊Ç¬Ç∑ÇÈ
# 4:3ÇæÇ¡ÇΩÇÁ360x270Ç…Ç∑ÇÈÇØÇ«ÅA1440x1080ÇæÇØÇÕÇ‚ÇÁÇ»Ç¢
echo "$1 aspect check"
echo `egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+,' /tmp/fps.txt`
asck=`egrep '[0-9][0-9][0-9]+x[0-9][0-9][0-9]+,' /tmp/fps.txt`
asw=`echo $asck | cut -d"," -f3 | cut -d"x" -f1 | sed "s/\s//g"`
ash=`echo $asck | cut -d"," -f3 | cut -d"x" -f2 | sed "s/\s//g"`
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
rm /tmp/fps.txt
# Ç¶ÇÒÇ±Ç∑ÇÈ
/usr/bin/ffmpeg -i "$1" -s "$wide"x270 -vcodec h264 -b 500k -acodec aac -ac 2 -ar 48000 -ab 128k -async 100 -crf 20 -g 230 -mbd 2 -me umh -subq 6 -qdiff 6 -me_range 32 -nr 50 -qmin 12 -sc_threshold 65 -bidir_refine 1 -keyint_min 3 -cmp chroma -flags bitexact+alt+mv4+loop -f mp4 -coder 0 -level 13 -threads 0 $3 $opt /$drive/tmp/"$1".mp4
# MP4BoxÇ≈faststartÇΩÇ¢Ç®Ç§Ç…Ç∑ÇÈ
/usr/local/bin/MP4Box -ipod /$drive/tmp/"$1".mp4
/bin/mv -v /$drive/tmp/"$1".mp4 "$2""$1".mp4
