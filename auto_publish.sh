#!/usr/bin/env bash
# swirhen.tv auto publisher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
DOWNLOAD_DIR="${SCRIPT_DIR}/../"
LIST_FILE=~/Dropbox/swirhentv/checklist.txt
LIST_TEMP=${SCRIPT_DIR}/checklist.temp
RSS_TEMP=${SCRIPT_DIR}/rss.temp
RSS_XML=${SCRIPT_DIR}/rss.xml
RESULT_FILE=${SCRIPT_DIR}/autodl.result
DATETIME=`date "+%Y/%m/%d-%H:%M:%S"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
#URI="https://www.nyaa.se/?page=search&cats=1_11&term=Ohys%7CLeopard&page=rss"
URI="http://jp.leopard-raws.org/rss.php"
PYTHON_PATH="/home/swirhen/.pythonbrew/pythons/Python-3.4.3/bin/python"
CHANNEL="bot-open"
POST_FLG=1
LOG_FILE=${SCRIPT_DIR}/autopub_${DATETIME2}.log

# botから呼ばれた場合はslack postしない
if [ "$1" != "" ]; then
  POST_FLG=0
fi

# 多重起動回避
if [ `ps -ef | grep $0 | grep -v grep | wc -l` -gt 1 ]; then
  echo "$0 processing..."
  exit 0
fi

end() {
  # rm -f ${LOG_FILE}
  exit 0
}

logging() {
  echo "`date '+%Y/%m/%d %H:%M:%S'` $1" >> ${LOG_FILE}
}

slack_post() {
  ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "${CHANNEL}" "$1"
}

slack_upload() {
  /usr/bin/curl -F channels="${CHANNEL}" -F file="@$1" -F title="$2" -F token=`cat token` -F filetype=text https://slack.com/api/files.upload
}

# seed download
logging "### seed download start."
slack_post "swirhen.tv auto publish start..."

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
      EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}\) .*/\1/"`
      EPNUM_N=${EPNUM}
      if [ "${#EPNUM}" -gt 3 ]; then
        EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}.5\) .*/\1/"`
        EPNUM_N=$(( ${EPNUM%.*} + 1 ))
      fi
      EPNUM_OLD_N=${EP_NUMS[${cnt}]}
      if [ "${#EPNUM_OLD_N}" -gt 3 ]; then
        EPNUM_OLD_N=$(( ${EPNUM_OLD_N%.*} + 1 ))
      fi
      if [ "${EPNUM_N}" -gt "${EPNUM_OLD_N}" ]; then
        logging "new episode: ${EPNUM} (local: ${EP_NUMS[${cnt}]})"
        hit_flg=1
        # Leopard優先
        if [ "`echo \"${title}\" | grep \"Leopard\"`" != "" ]; then
          if [ `ls ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent | wc -l` -eq 1 ]; then
            rm -f ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent
          fi
          if [ `ls ${DOWNLOAD_DIR}/*Leopard*"${NAME}"*.torrent | wc -l` -eq 0 ]; then
            logging "download link: ${link}"
            echo "${title}" >> ${RESULT_FILE}
            wget --no-check-certificate --restrict-file-names=nocontrol --trust-server-names --content-disposition "${link}" -P "${DOWNLOAD_DIR}" > /dev/null
            break
          fi
        else
          if [ `ls ${DOWNLOAD_DIR}/*Leopard*"${NAME}"*.torrent | wc -l` -eq 0 -a `ls ${DOWNLOAD_DIR}/*Ohys*"${NAME}"*.torrent | wc -l` -eq 0 ]; then
            logging "download link: ${link}"
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

cd /data/share/movie/sh
cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
cp -p ${LIST_FILE} .
git commit -m 'checklist.txt update' checklist.txt
git pull
git push origin master

if [ "${POST_FLG}" = "1" ]; then
  if [ -s ${RESULT_FILE} ]; then
    post_msg="seed download completed.
\`\`\`
download seeds:
`cat ${RESULT_FILE}`
\`\`\`"
    logging "${post_msg}"
    slack_post "${post_msg}"
  else
    post_msg="swirhen.tv auto publish completed. (no new episode)"
    slack_post "${post_msg}"
    end
  fi
fi

cd /data/share/movie

# torrent download
logging "### torrent download start."

/data/share/movie/sh/tdlstop.sh 38888 &
/usr/bin/wine aria2c.exe --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent

# movie file rename
logging "### movie file  rename start."

rm *.torrent
/data/share/movie/sh/mre.sh

# auto encode
logging "### auto encode start."

/data/share/movie/sh/169f.sh

slack_post "swirhen.tv auto publish completed."
sleep 1
slack_upload "${LOG_FILE}" "auto_publish_log_${DATETIME2}"

end