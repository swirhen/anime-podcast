#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LIST_FILE=~/Dropbox/swirhentv/checklist.txt
RSS_TEMP=${SCRIPT_DIR}/rss.temp
RSS_XML=${SCRIPT_DIR}/rss.xml
MODE=$1

URI="https://www.nyaa.se/?page=search&cats=1_11&term=Ohys%7CLeopard&page=rss"

curl -s -S "${URI}" > ${RSS_TEMP}
xmllint --format ${RSS_TEMP} > ${RSS_XML}

EP_NUMS=()
NAMES=()
while read EP_NUM NAME
do
  EP_NUMS+=( "${EP_NUM}" )
  NAME+=( "${NAME}" )
done < ${LIST_FILE}

cnt=1
while :
do
  title=`echo "cat /rss/channel/item[${cnt}]" | xmllint --shell "${RSS_XML}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
  if [ "${title}" = "" ]; then
    break
  fi

  link=`echo "cat /rss/channel/item[${cnt}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`
#  echo "cnt:${cnt}"
#  echo "title:${title}"
#  echo "link:${link}"
  cnt2=0
  for NAME in "${NAMES[@]}"
  do
    echo "${NAME}"
    if [ "`echo ${title} | grep \"${NAME}\"`" != "" ]; then
      echo "hit! ${title}"
      EPNUM_KETA=${#EP_NUMS[${cnt2}]}
      EPNUM=`echo "${title}" | sed "s/.*${NAME} \([0-9]{2,3}\) .*/\1/"`
      if [ "${EPNUM}" -gt "${EP_NUMS[${snt2}]}" ]; then
        echo "新しい話数がある: ${EPNUM} (比較対象: ${EP_NUMS[${snt2}]}"
        echo "link: ${link}"
      fi
    fi
    (( cnt2++ ))
  done
  (( cnt++ ))
done