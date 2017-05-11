#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
DOWNLOAD_DIR="${SCRIPT_DIR}/../"
LIST_FILE=~/Dropbox/swirhentv/checklist.txt
LIST_TEMP=${SCRIPT_DIR}/checklist.temp
RSS_TEMP=${SCRIPT_DIR}/rss.temp
RSS_XML=${SCRIPT_DIR}/rss.xml
RESULT_FILE=${SCRIPT_DIR}/autodl.result
DATETIME=`date "+%Y/%m/%d-%H:%M:%S"`
#URI="https://www.nyaa.se/?page=search&cats=1_11&term=Ohys%7CLeopard&page=rss"
URI="http://jp.leopard-raws.org/rss.php"
PYTHON_PATH="/home/swirhen/.pythonbrew/pythons/Python-3.4.3/bin/python"
CHANNEL="bot-sandbox"
POST_FLG=1
if [ "$1" != "" ]; then
  POST_FLG=0
fi

rm -f ${RESULT_FILE}

curl -s -S "${URI}" > ${RSS_TEMP}
xmllint --format ${RSS_TEMP} > ${RSS_XML}

LAST_UPDS=()
EP_NUMS=()
NAMES=()
while read LAST_UPD EP_NUM NAME
do
  if [ "${LAST_UPD}" != "Last" ]; then
    LAST_UPDS+=( "${LAST_UPD}" )
    EP_NUMS+=( "${EP_NUM}" )
    NAMES+=( "${NAME}" )
  fi
done < ${LIST_FILE}

echo "Last Update: ${DATETIME}" > ${LIST_TEMP}

# search
cnt=0
for NAME in "${NAMES[@]}"
do
  cnt2=1
  hit_flg=0
  while :
  do
    title=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
    # feed end
    if [ "${title}" = "" ]; then
      break
    fi

    link=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`

    # fetch
    if [ "`echo \"${title}\" | grep \"${NAME}\"`" != "" ]; then
      echo "hit! ${title}"
      EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}\) .*/\1/"`
      EPNUM_N=${EPNUM}
      if [ "${EPNUM}" = "" ]; then
        EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}\).5 .*/\1/"`
        EPNUM_N=$(( ${EPNUM%.*} + 1 ))
      fi
      if [ "${EPNUM_N}" -gt "${EP_NUMS[${cnt}]}" ]; then
        echo "new episode: ${EPNUM} (local: ${EP_NUMS[${cnt}]})"
        hit_flg=1
        # Leopard優先
        if [ "`echo \"${title}\" | grep \"Leopard\"`" != "" ]; then
          if [ `ls ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent | wc -l` -eq 1 ]; then
            rm -f ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent
          fi
          if [ `ls ${DOWNLOAD_DIR}/*Leopard*"${NAME}"*.torrent | wc -l` -eq 0 ]; then
            echo "download link: ${link}"
            echo "${title}" >> ${RESULT_FILE}
            wget --no-check-certificate --restrict-file-names=nocontrol --trust-server-names --content-disposition "${link}" -P "${DOWNLOAD_DIR}" > /dev/null
            break
          fi
        else
          if [ `ls ${DOWNLOAD_DIR}/*Leopard*"${NAME}"*.torrent | wc -l` -eq 0 -a `ls ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent | wc -l` -eq 0 ]; then
            echo "download link: ${link}"
            echo "${title}" >> ${RESULT_FILE}
            wget --no-check-certificate --restrict-file-names=nocontrol --trust-server-names --content-disposition "${link}" -P "${DOWNLOAD_DIR}" > /dev/null
            break
          fi
        fi
      fi
    fi
    (( cnt2++ ))
  done
  if [ "${hit_flg}" = "1" ]; then
    echo "${DATETIME} ${EPNUM} ${NAME}" >> ${LIST_TEMP}
  else
    echo "${LAST_UPDS[${cnt}]} ${EP_NUMS[${cnt}]} ${NAME}" >> ${LIST_TEMP}
  fi
  (( cnt++ ))
done

if [ "${POST_FLG}" = "1" ]; then
  if [ -s ${RESULT_FILE} ]; then
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "${CHANNEL}" "@here swirhen.tv auto download completed.
\`\`\`
download seeds:
`cat ${RESULT_FILE}`
\`\`\`"
  else
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "${CHANNEL}" "swirhen.tv auto download completed. (no new episode)"
  fi
fi

cd /data/share/movie/sh
cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
cp -p ${LIST_FILE} .
git commit -m 'checklist.txt update' checklist.txt
git pull
git push origin master
