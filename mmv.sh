# 動画リネーム用シェル
# usage: ./rename.sh 与えるファイル群 リネーム用リスト
# リネーム用リストにはリネームもとファイルの検索文字と正式な作品名を
# tabで繋げて記述すること
LIST=/data/share/movie/checklist.txt
while read DUMMY DUMMY2 LINE
do
  NAME="${LINE#*\|}"
  nn=`echo $1 | sed -e "s/\(${NAME}\).*\.mp4/\1/"`
  if [ "$nn" != "$1" ]; then
    echo "# move $1"
    mv -v "$1" /data/share/movie/*"${NAME}"/.
    break
  fi
done < ${LIST}
