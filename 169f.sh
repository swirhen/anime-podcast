#!/usr/bin/env zsh
# 動画エンコード用シェル
source /home/swirhen/.zshrc
for a in "$@" *話*.(avi|mp4|mkv|wmv)
do
  if [ -f "$a" ]; then
    until [ -f "/data/share/movie/98 PSP用/$a.mp4" ];
    do
      /data/share/movie/sh/169mp43.sh "$a" "/data/share/movie/98 PSP用/"
    done
    /data/share/movie/sh/mmpc.sh
    /data/share/movie/sh/mmpc3.sh
    /data/share/movie/sh/mmv.sh "$a"
    sleep 5
    /home/swirhen/Shellscriptter/Shellscriptter.sh -r "【publish】$a.mp4"
  fi
done
