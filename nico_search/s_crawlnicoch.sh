#!/usr/bin/env zsh
# ニコニコ検索して、保存するコマンドのリストを吐く
# 引数:
# 1: 検索ワード
# 2: なんでもいいので入れると音声モード(コマンドの後ろに aがつく)
SRC_WORD="$1"
SRC_WORD_ENC=`echo "${SRC_WORD}" | nkf -wMQ | sed 's/=$//g' | tr = % | tr -d "\n"`
AUDIO_FLG=""
if [ "$2" != "" ]; then
	AUDIO_FLG=" a"
fi
# 複数ページあったら結果がなくなるまでクロールする
PAGE=1
while :
do
    result=`curl "http://www.nicovideo.jp/search/${SRC_WORD_ENC}?sort=f&order=d&page=${PAGE}" | grep ".*a title.*${SRC_WORD}" | sed "s#^.*<a.*title=\"\(.*\)\".*href=\"\(.*\)?ref.*#/data/share/movie/sh/nicodl.sh \"http://www.nicovideo.jp\2\" \"\1\"#" | sed "s/\ href.*/ ${AUDIO_FLG}/"`
    if [ "${result}" != "" ]; then
        echo ${result}
    else
        break
    fi
    (( PAGE++ ))
done