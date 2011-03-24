#!/usr/bin/env zsh
# 動画エンコード用シェル
source /home/swirhen/.zshrc
for a in "$1"*話*.(avi|mp4|mkv|wmv)
do
  if [ -f "$a" ]; then
    /data/share/movie/sh/169mp43.sh "$a" "/data/share/movie/98 PSP用/"
    /data/share/movie/sh/mmpc.sh
    /home/swirhen/sh/ftpmount.sh
#    cp -v "/data/share/movie/98 PSP用/$a.mp4" "/data/share/movie/97 bashi.org/"
#    /data/share/movie/sh/mbmpc.sh
    cp -v "/data/share/movie/98 PSP用/$a.mp4" "/data/share/movie/96 swirhen.net/"
    /data/share/movie/sh/msmpc.sh
    /data/share/movie/sh/mmv.sh "$a"
    /home/swirhen/Shellscriptter/Shellscriptter.sh -r "【publish】$a.mp4"
  fi
done
