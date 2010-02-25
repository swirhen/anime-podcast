# /bin/sh
# @author swirhen
# mkvextract$B!"(BMP4Box$B$r;H$C$F(BH264+aac$B$J(Bmkv$B%U%!%$%k$r(B
# mp4$B%U%!%$%k$K$D$a$J$*$9(B
# $B2;@<$,(Bac3$B$H$+(Bflac$B$N$P$"$$$O%3%a%s%H%"%&%H$7$F$"$k$H$3$m$r$D$+$&(B
# fps$B$,2DJQ$H$+$@$H;`$L$N$G$"$-$i$a$k(B
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
