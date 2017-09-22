#!/usr/bin/env zsh
# 動画エンコード用シェル
# 実行したディレクトリに存在するシリーズ系動画(*話*.mp4等)
# をすべてエンコードし、フィードを更新、Twitterに告知する
# usage 169f.sh [priority file]
PYTHON_PATH="/home/swirhen/.pythonbrew/pythons/Python-3.4.3/bin/python"
source /home/swirhen/.zshrc
cd /data/share/movie
(
IFS=$'\n';
for a in `ls -rt *話*.(avi|mp4|mkv|wmv)`
do
  if [ -f "$a" ]; then
    error=0
    until [ -f "/data/share/movie/98 PSP用/$a.mp4" ];
    do
      error=`expr $error + 1`
      if [ $error -gt 10 ]; then
        break;
      fi
      /data/share/movie/sh/169mp45.sh "$a" "/data/share/movie/98 PSP用/"
    done
    /data/share/movie/sh/mmpc.sh
    /data/share/movie/sh/mmpc3.sh
    /data/share/movie/sh/mmv.sh "$a"
    sleep 3
    /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【publish】$a.webm"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【publish】$a.webm"
  fi
done
)
