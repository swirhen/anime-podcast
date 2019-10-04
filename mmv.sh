#!/usr/bin/env zsh
# 動画リネーム用シェル
# usage: ./rename.sh 与えるファイル群 リネーム用リスト
# リネーム用リストにはリネームもとファイルの検索文字と正式な作品名を
# tabで繋げて記述すること
LIST=/data/share/movie/checklist.txt
cnt=0
while read DUMMY DUMMY2 LINE
do
  if [ ${cnt} != 0 ]; then
    NAME="${LINE#*\|}"
    NAME=`echo "${NAME}" | sed "s/&amp;/\&/g"`
    nn=`echo "$1" | sed -e "s/\ 第.\{2,4\}話\.\(mp4\|mkv\)//"`
    if [ "${nn}" = "${NAME}" ]; then
      echo "# move $1"
      mv -v "$1" /data/share/movie/*"${NAME}"/.
      break
    fi
  fi
  (( cnt++ ))
done < ${LIST}
