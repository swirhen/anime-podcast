#!/usr/bin/env bash
# swirhen.tv auto publisher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
DOWNLOAD_DIR="${SCRIPT_DIR}/../"
LIST_FILE=${SCRIPT_DIR}/checklist.txt
LIST_TEMP=${SCRIPT_DIR}/checklist.temp
RSS_TEMP=${SCRIPT_DIR}/rss.temp
RSS_XML=${SCRIPT_DIR}/rss.xml
RESULT_FILE=${SCRIPT_DIR}/autodl.result
DATETIME=`date "+%Y/%m/%d-%H:%M:%S"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
#URI="https://www.nyaa.se/?page=search&cats=1_11&term=Ohys%7CLeopard&page=rss"
URI="http://jp.leopard-raws.org/rss.php"
PYTHON_PATH="python3"
CHANNEL="bot-open"
POST_FLG=1
LOG_FILE=${SCRIPT_DIR}/autopub_${DATETIME2}.log

# botから呼ばれた場合はslack postしない
if [ "$1" != "" ]; then
  POST_FLG=0
fi

end() {
#  rm -f ${LOG_FILE}
  mv ${LOG_FILE} ${SCRIPT_DIR}/logs/
  exit 0
}

logging() {
  echo "`date '+%Y/%m/%d %H:%M:%S'` $1" >> ${LOG_FILE}
}

slack_post() {
  ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "${CHANNEL}" "$1"
}

slack_upload() {
  /usr/bin/curl -F channels="${CHANNEL}" -F file="@$1" -F title="$2" -F token=`cat ${SCRIPT_DIR}/token` -F filetype=text https://slack.com/api/files.upload
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
NAMESJ=()
DOWNLOADS=()
RESULT_END=""
END_EPISODES=()
END_EPISODES_NG=()

while read LAST_UPD EP_NUM NAME
do
  if [ "${LAST_UPD}" != "Last" ]; then
    LAST_UPDS+=( "${LAST_UPD}" )
    EP_NUMS+=( "${EP_NUM}" )
    NAMES+=( "${NAME%%\|*}" )
    NAMESJ+=( "${NAME#*\|}" )
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
    if [ "`echo \"${title}\" | grep \"\.ts\"`" != "" ]; then
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
        if [ "${EPNUM}" = "${EPNUM_OLD_N}" ]; then
          break
        fi
        EPNUM_OLD_N=${EPNUM_OLD_N%.*}
      fi
      if [ "${EPNUM_N}" -gt "${EPNUM_OLD_N}" ]; then
        logging "new episode: ${EPNUM} (local: ${EP_NUMS[${cnt}]})"
        hit_flg=1
        echo "${title}" >> ${RESULT_FILE}
        DOWNLOADS+=( "${link}" )
        # END Episode
        if [ "`echo \"${title}\" | grep \"END\"`" != "" ]; then
          EP_COUNT=`find ${DOWNLOAD_DIR}/*"${NAMESJ[${cnt}]}"/ -regextype posix-basic -regex ".*第[^\.]*話.*" | wc -l`
          (( EP_COUNT++ ))
          logging "# 終了とみられるエピソード: ${title}"
          if [ ${EPNUM} -eq ${EP_COUNT} ]; then
            logging "  抜けチェック:OK 既存エピソードファイル数(.5話を除く): ${EP_COUNT} / 最終エピソード番号: ${EPNUM}"
            END_EPISODES+=( "${NAMESJ}" )
          else
            logging "  抜けチェック:NG 既存エピソードファイル数(.5話を除く): ${EP_COUNT} / 最終エピソード番号: ${EPNUM}"
            END_EPISODES_NG+=( "${NAMESJ}" )
          fi
        fi
        break
      fi
    fi
    (( cnt2++ ))
  done
  if [ "${hit_flg}" = "1" ]; then
    echo "${DATETIME} ${EPNUM} ${NAME}|${NAMESJ[${cnt}]}" >> ${LIST_TEMP}
  else
    echo "${LAST_UPDS[${cnt}]} ${EP_NUMS[${cnt}]} ${NAME}|${NAMESJ[${cnt}]}" >> ${LIST_TEMP}
  fi
  (( cnt++ ))
done

cd /data/share/movie/sh
if [ `cat ${LIST_TEMP} | wc -l` -ne `cat ${LIST_FILE} | wc -l` ]; then
  slack_post "@here !!! リスト行数が変化しました。 checklist.txt のコミットログを確認してください "
fi
cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
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
    logging "${post_msg}"
    slack_post "${post_msg}"
    end
  fi
fi

cd /data/share/movie

for DL_LINK in "${DOWNLOADS[@]}"
do
  logging "download link: ${DL_LINK}"
  wget --no-check-certificate --restrict-file-names=nocontrol --trust-server-names --content-disposition "${DL_LINK}" -P "${DOWNLOAD_DIR}" > /dev/null
done

# torrent download
logging "### torrent download start."

/data/share/movie/sh/tdlstop.sh 38888 &
/usr/bin/wine aria2c.exe --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent

# movie file rename
logging "### movie file  rename start."

rm *.torrent
/data/share/movie/sh/mre.sh

logging "renamed movie files:"
ls *話.mp4 >> ${LOG_FILE}

# auto encode
logging "### auto encode start."

/data/share/movie/sh/169f.sh

# end episodes list modify
ENDLIST_FILE=`find /data/share/movie/end*  -mtime -30 | tail -1`
if [ "${ENDLIST_FILE}" = "" ]; then
  ENDLIST_FILE_LAST=`find /data/share/movie/end* | sort | tail -1`
  ENDLIST_LAST_YEAR=`echo ${ENDLIST_FILE_LAST} | sed "s/.*end_\(....\)Q.*/\1/"`
  ENDLIST_LAST_NUM=`echo ${ENDLIST_FILE_LAST} | sed "s/.*Q\(.\).*/\1/"`
  if [ `expr ${ENDLIST_LAST_NUM} + 1` -eq 5 ]; then
    ENDLIST_FILE=`echo ${ENDLIST_FILE_LAST} | sed "s/\(.*end_\).*/\1$((++ENDLIST_LAST_YEAR))Q1.txt/"`
  else
    ENDLIST_FILE=`echo ${ENDLIST_FILE_LAST} | sed "s/\(.*end_....Q\).*/\1$((++ENDLIST_LAST_NUM)).txt/"`
  fi
fi

if [ ${#END_EPISODES[@]} -ne 0 ]; then
  post_mes_end="# 終了とみられる番組で、抜けチェックOKのため、終了リストに追加/チェックリストから削除
\`\`\`"
  for END_EPISODE in "${END_EPISODES[@]}"
  do
    post_mes_end+="
${END_EPISODE}"
    sed -i -e "/${END_EPISODE}/d" "${LIST_FILE}"
    echo "${END_EPISODE}" >> ${ENDLIST_FILE}
  done

  post_mes_end+="
\`\`\`"
  sleep 1
  slack_post "${post_mes_end}"

  cd /data/share/movie/sh
  git commit -m 'checklist.txt update: end episodes delete' checklist.txt
  git pull
  git push origin master
fi

if [ ${#END_EPISODES_NG[@]} -ne 0 ]; then
  post_mes_end="# 終了とみられる番組で、抜けチェックNGのため、終了リストにのみ追加(要 抜けチェック)
\`\`\`"
  for END_EPISODE_NG in "${END_EPISODES_NG[@]}"
  do
    post_mes_end+="
${END_EPISODE_NG}"
    echo "${END_EPISODE_NG}" >> ${ENDLIST_FILE}
  done
  post_mes_end+="
\`\`\`"
  sleep 1
  slack_post "${post_mes_end}"
fi

logging "### all process completed."
slack_post "swirhen.tv auto publish completed."
sleep 1
slack_upload "${LOG_FILE}" "auto_publish_log_${DATETIME2}"

end
