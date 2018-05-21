#!/usr/bin/env bash
# swirhen.tv auto publisher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
DOWNLOAD_DIR="${SCRIPT_DIR}/../"
LIST_FILE=${SCRIPT_DIR}/checklist.txt
LIST_FILE2=${SCRIPT_DIR}/sub_checklist.txt
LIST_TEMP=${SCRIPT_DIR}/checklist.temp
RSS_TEMP=${SCRIPT_DIR}/rss.temp
RSS_XML=${SCRIPT_DIR}/rss.xml
RSS_TEMP2=${SCRIPT_DIR}/rss2.temp
RSS_XML2=${SCRIPT_DIR}/rss2.xml
RESULT_FILE=${SCRIPT_DIR}/autodl.result
DATETIME=`date "+%Y/%m/%d-%H:%M:%S"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
URI="http://jp.leopard-raws.org/rss.php"
URI2="https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss"
PYTHON_PATH="python3"
CHANNEL="bot-open"
POST_FLG=1
LOG_FILE=${SCRIPT_DIR}/autopub_${DATETIME2}.log
FLG_FILE=${SCRIPT_DIR}/autopub_running
LEOPARD_INDEX=${SCRIPT_DIR}/leopard_index.html
#TITLE_EN_LIST_FILE=${SCRIPT_DIR}/title_en.list
#TITLE_JA_LIST_FILE=${SCRIPT_DIR}/title_ja.list
INDEX_GET=0
NEW_RESULT_FILE=${SCRIPT_DIR}/new_program_result.txt
NEW_PROGRAM_FILE=${SCRIPT_DIR}/new_program.txt

get_ja_title_list() {
#    ARG_TITLE_EN="$1"
#
#    # 日本語名対応リスト作成
#    if [ ${ENJA_LIST_GET} -eq 0 ]; then
#        curl -s -S "http://jp.leopard-raws.org/" > ${LEOPARD_INDEX}
#        cat ${LEOPARD_INDEX} | grep -A 1 "/?search" | grep "のRSS" | sed "s/.*='\(.*\)のRSS.*/\1/" > ${TITLE_EN_LIST_FILE}
#        cat ${LEOPARD_INDEX} | grep "/?search" | sed "s/.*>\(.*\)<.*/\1/" > ${TITLE_JA_LIST_FILE}
#
#        TITLE_EN_LIST=()
#        TITLE_JA_LIST=()
#        while read TITLE_EN
#        do
#            TITLE_EN_LIST+=( "${TITLE_EN}" )
#        done < ${TITLE_EN_LIST_FILE}
#
#        while read TITLE_JA
#        do
#            TITLE_JA_LIST+=( "${TITLE_JA}" )
#        done < ${TITLE_JA_LIST_FILE}
#
#        ENJA_LIST_GET=1
#    fi
#    i=0
#    for TITLE_EN in "${TITLE_EN_LIST[@]}"
#    do
#        # if [[ ${TITLE_EN} =~ ${ARG_TITLE_EN} ]]; then
#        if [ "${TITLE_EN}" = "${ARG_TITLE_EN}" ]; then
#          echo "${TITLE_JA_LIST[${i}]}"
#          break
#        fi
#        (( i++ ))
#    done

    DL_HASH=$1
    if [ ${INDEX_GET} -eq 0 ]; then
        curl -s -S "http://jp.leopard-raws.org/" > ${LEOPARD_INDEX}
        INDEX_GET=1
    fi

    TITLE_JA="`cat ${LEOPARD_INDEX} | grep "${DL_HASH}" | head -1 | sed "s/.*>\(.*\)\ -\ .*/\1/"`"

    echo "${TITLE_JA}"
}

# botから呼ばれた場合はslack postしない
if [ "$1" != "" ]; then
  POST_FLG=0
fi

end() {
#  rm -f ${LOG_FILE}
  mv ${LOG_FILE} ${SCRIPT_DIR}/logs/
  rm -f ${FLG_FILE}
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

# running flag file check
if [ -f ${FLG_FILE} ]; then
  logging "### running flag file exist. exit"
  mv ${LOG_FILE} ${SCRIPT_DIR}/logs/
  exit 1
else
  touch ${FLG_FILE}
fi

# seed download
logging "### auto publish start."
slack_post "swirhen.tv auto publish start..."

rm -f ${RESULT_FILE}

curl -s -S "${URI}" > ${RSS_TEMP}
if [ ! -s ${RSS_TEMP} ]; then
    curl -s -S "${URI2}" > ${RSS_TEMP}
fi
xmllint --format ${RSS_TEMP} > ${RSS_XML}
# URI2 対応(nyaa.si)
curl -s -S "${URI2}" > ${RSS_TEMP2}
xmllint --format ${RSS_TEMP2} > ${RSS_XML2}

LAST_UPDS=()
EP_NUMS=()
NAMES=()
NAMESJ=()
NAMES_SUB=()
DOWNLOADS=()
RESULT_END=""
END_EPISODES=()
END_EPISODES_NG=()

while read NAME
do
  NAMES_SUB+=( "${NAME}" )
done < ${LIST_FILE2}

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
  # NAMES_SUBにタイトルが存在するか
  sub_flg=0
  for NAME_SUB in "${NAMES_SUB[@]}"
  do
    if [ "${NAME}" = "${NAME_SUB}" ]; then
      sub_flg=1
      break
    fi
  done

  while :
  do
    title=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
    title2=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML2}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
    # feed end
    if [ "${title}" = "" -a "${title2}" = "" ]; then
      break
    fi
    if [ "`echo \"${title}\" | grep \"\.ts\"`" != "" ]; then
      continue
    fi

    link=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`
    link2=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML2}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`

    # fetch
    fetch_flg=0
    if [ ${sub_flg} -eq 0 -a "`echo \"${title}\" | grep \"${NAME}\"`" != "" ]; then
      fetch_flg=1
    elif [ ${sub_flg} -eq 1 -a "`echo \"${title2}\" | grep \"${NAME}\"`" != "" ]; then
      title="${title2}"
      link="${link2}"
      fetch_flg=1
    fi

    if [ ${fetch_flg} -eq 1 ]; then
#      EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}\) .*/\1/"`
      EPNUM=`echo "${title}" | sed "s/.*${NAME}.* - \([0-9]\{2,3\}\).*/\1/"`
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
            END_EPISODES+=( "${NAMESJ[${cnt}]}" )
          else
            logging "  抜けチェック:NG 既存エピソードファイル数(.5話を除く): ${EP_COUNT} / 最終エピソード番号: ${EPNUM}"
            END_EPISODES_NG+=( "${NAMESJ[${cnt}]}" )
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

# 新番組1話対応(Leopardのみ)
cnt2=1
new_hit_flg=0
rm -f ${NEW_RESULT_FILE}
while :
do
    title=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
    # feed end
    if [ "${title}" = "" ]; then
      break
    fi
    if [ "`echo \"${title}\" | grep \"\.ts\"`" != "" ]; then
      continue
    fi

    if [[ ${title} =~ -\ 01\ RAW ]]; then
        link=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`
        TITLE_EN=`echo ${title} | sed "s/\[Leopard-Raws\]\ \(.*\)\ -\ 01\ RAW.*/\1/"`
        DL_HASH=`echo ${link} | sed "s/.*hash=\(.*\)/\1/"`
        TITLE_JA=`get_ja_title_list "${DL_HASH}"`

        if [ "${TITLE_JA}" = "" ]; then
            TITLE_JA="${TITLE_EN}"
        fi

        if [ "`grep "${TITLE_JA}" ${NEW_PROGRAM_FILE}`" = "" ]; then
            new_hit_flg=1
            echo "${DATETIME} 0 ${TITLE_EN}|${TITLE_JA}" >> ${LIST_TEMP}
            echo "${DATETIME} 0 ${TITLE_EN}|${TITLE_JA}" >> ${LIST_FILE}
            echo "${TITLE_JA} (${TITLE_EN})" >> ${NEW_RESULT_FILE}
            echo "${TITLE_JA}" >> ${NEW_PROGRAM_FILE}
            mkdir -p "${DOWNLOAD_DIR}/${TITLE_JA}"
        fi
    fi
    (( cnt2++ ))
done

if [ ${new_hit_flg} -eq 1 ]; then
    post_msg="@here 新番組検知！
リストに追加されたので、次回ダウンロード対象となります
対象外にする場合は、リストから削除、保存ディレクトリを削除してください
\`\`\`
`cat ${NEW_RESULT_FILE}`
\`\`\`"
    logging "${post_msg}"
    slack_post "${post_msg}"
fi

cd /data/share/movie/sh
if [ `cat ${LIST_TEMP} | wc -l` -ne `cat ${LIST_FILE} | wc -l` ]; then
  slack_post "@channel !!! リスト行数が変化しました。 checklist.txt のコミットログを確認してください "
fi
cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
git commit -m 'checklist.txt update' checklist.txt
git commit -m 'new_program.txt update' new_program.txt
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
aria2c --listen-port=38888 --max-upload-limit=200K --seed-ratio=0.01 --seed-time=1 *.torrent

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
  post_mes_end="@channel 終了とみられる番組で、抜けチェックNGのため、終了リストにのみ追加(要 抜けチェック)
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
