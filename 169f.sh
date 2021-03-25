#!/usr/bin/env zsh
# 動画エンコード用シェル
# movieディレクトリに存在するシリーズ系動画(*話*.mp4等)
# をすべてエンコードし、フィードを更新、Twitterに告知する
# usage 169f.sh (current dir flag)
# 引数に何か入れるとカレントディレクトリでやる(movieに移動しない)
PYTHON_PATH="python3"
source /home/swirhen/.zshrc
if [ "$1" = "" ]; then
  cd /data/share/movie
fi
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
      /data/share/movie/sh/169mp4.sh "$a" "/data/share/movie/98 PSP用/"
    done
    /data/share/movie/sh/mmpc.sh
#    if [ "$1" = "" ]; then
      /data/share/movie/sh/mmv.sh "$a"
#    fi
    sleep 3
    /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "【publish】$a.mp4"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "【publish】$a.mp4"
  fi
done
)
