#!/usr/bin/env zsh
# 動画エンコード用シェル
# 実行したディレクトリに存在するシリーズ系動画(*話*.mp4等)
# をすべてエンコードし、フィードを更新、Twitterに告知する
# usage 169f.sh [priority file]
# 消失ファイル再エンコ用臨時シェル
PYTHON_PATH="python3"
source /home/swirhen/.zshrc
cd /data/share/movie
(
IFS=$'\n';
for a in `ls -t *話*.(avi|mp4|mkv|wmv)`
do
  if [ -f "$a" ]; then
    error=0
    until [ -f "/data/share/movie/98 PSP用/$a.mp4" ];
    do
      error=`expr $error + 1`
      if [ $error -gt 10 ]; then
        break;
      fi
      /data/share/movie/sh/169mp44.sh "$a" "/data/share/movie/98 PSP用/"
    done
    time=`stat "${a}" | grep Modify | awk '{ print $2,$3 }'`
    touch -t "${time:0:4}${time:5:2}${time:8:2}${time:11:2}${time:14:2}.${time:17:2}" "98 PSP用/${a}.mp4"
    /data/share/movie/sh/mmv.sh "$a"
    /data/share/movie/sh/mmpc.sh
  fi
done
)
