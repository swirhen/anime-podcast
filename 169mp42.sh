# /bin/sh
# @author swirhen
# ffmpeg$B$r$D$+$C$F(BPSP$B$d$"$$$[$s$`$1$N$I$&$,$r$D$/$k(B
# wine$B$r$D$+$C$F(Bwindows$B$P$s$N$P$$$J$j$r$D$+$C$F$7$^$&HG(B
# usage:169mp42.sh [infile] [out directory] [encode option]
# $B$I$i$$$V$,$A$,$&$I$&$,$N$H$-$K(Btmp$B$r$F$-$;$D$J$P$7$g$K$+$($k(B
tmp=`readlink -f "$PWD"`
drive=`expr "$tmp" : "\/\(data.\?\)\/.*"` if [ ${drive:-null} = null ] ; then
  drive=data
fi
# $B$$$m$$$m$A$'$C$/(B
# $B$X$s$J(Bfps$B$N$I$&$,$N$P$"$$(B 30000/1001$B$K$H$&$$$D$7$F$4$^$+$9(B
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
# $B$"$9$Z$/$H$R$r$8$I$&$O$s$Y$D$9$k(B
# 4:3$B$@$C$?$i(B360x270$B$K$9$k$1$I!"(B1440x1080$B$@$1$O$d$i$J$$(B
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
# $B$($s$3$9$k(B
/usr/bin/wine ffmpeg.exe -i "$1" -s "$wide"x270 -vcodec libx264 -b 500k -acodec libfaac -ac 2 -ar 48000 -ab 128k -async 100 -crf 20 -g 230 -mbd 2 -me_method umh -subq 6 -qdiff 6 -me_range 32 -nr 50 -qmin 12 -sc_threshold 65 -bidir_refine 1 -keyint_min 3 -cmp chroma -flags bitexact+alt+mv4+loop -f mp4 -coder 0 -level 13 -threads 0 $3 $opt /$drive/tmp/"$1".mp4
# MP4Box$B$G(Bfaststart$B$?$$$*$&$K$9$k(B
/usr/local/bin/MP4Box -ipod /$drive/tmp/"$1".mp4
/bin/mv -v /$drive/tmp/"$1".mp4 "$2""$1".mp4
