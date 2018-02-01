#!/usr/bin/env zsh
# ニコニコ検索して、保存するコマンドのリストを吐く(slack bot用)
# 引数:
# 1: 検索ワード
NICODL_CMD="/data/share/movie/sh/nicodl.sh"
SRC_WORD="$1"
SRC_WORD_ENC=`echo "${SRC_WORD}" | nkf -wMQ | sed 's/=$//g' | tr = % | tr -d "\n"`
# 複数ページあったら結果がなくなるまでクロールする
PAGE=1
while :
do
    result=`curl -sS "http://www.nicovideo.jp/search/${SRC_WORD_ENC}?sort=f&order=d&page=${PAGE}" | grep ".*a title.*${SRC_WORD}" | sed "s#^.*<a.*title=\"\(.*\)\".*href=\"\(.*\)?ref.*#http://www.nicovideo.jp\2 : \1#" | sed "s/\ href.*//"`
    if [ "${result}" != "" ]; then
        echo ${result}
    else
        break
    fi
    (( PAGE++ ))
done