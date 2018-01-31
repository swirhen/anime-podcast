#!/usr/bin/env zsh
# $B%K%3%K%38!:w$7$F!"J]B8$9$k%3%^%s%I$N%j%9%H$rEG$/(B
# $B0z?t(B:
# 1: $B8!:w%o!<%I(B
# 2: $B$J$s$G$b$$$$$N$GF~$l$k$H2;@<%b!<%I(B($B%3%^%s%I$N8e$m$K(B a$B$,$D$/(B)
SRC_WORD="$1"
SRC_WORD_ENC=`echo "${SRC_WORD}" | nkf -wMQ | sed 's/=$//g' | tr = % | tr -d "\n"`
echo "hogeee:${SRC_WORD_ENC}"
AUDIO_FLG=""
PAGE=1
if [ "$2" != "" ]; then
	AUDIO_FLG=" a"
fi
if [ "$3" != "" ]; then
	PAGE=$3
fi

curl "http://www.nicovideo.jp/search/${SRC_WORD_ENC}?sort=f&order=d&page=${PAGE}" | grep ".*a title.*${SRC_WORD}" | sed "s#^.*<a.*title=\"\(.*\)\".*href=\"\(.*\)?ref.*#/data/share/movie/sh/nicodl.sh \"http://www.nicovideo.jp\2\" \"\1\"#" | sed "s/\ href.*/ ${AUDIO_FLG}/"
