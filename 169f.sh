#!/usr/bin/env zsh
# 動画エンコード用シェル
# 実行したディレクトリに存在するシリーズ系動画(*話*.mp4等)
# をすべてエンコードし、フィードを更新、Twitterに告知する
# usage 169f.sh [priority file]
source /home/swirhen/.zshrc
for a in "$@" *話*.(avi|mp4|mkv|wmv)
do
  if [ -f "$a" ]; then
    error=0
    until [ -f "/data/share/movie/98 PSP用/$a.mp4" ];
    do
      error=`expr $error + 1`
      if [ $error -gt 10 ]; then
        break;
      fi
      /data/share/movie/sh/169mp43.sh "$a" "/data/share/movie/98 PSP用/"
    done
    /data/share/movie/sh/mmpc.sh
    /data/share/movie/sh/mmpc3.sh
    /data/share/movie/sh/mmv.sh "$a"
    sleep 3
    /home/swirhen/tiasock/tiasock_swirhentv.sh "【publish】$a.mp4"
  fi
done
