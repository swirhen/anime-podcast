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
URI2="http://jp.leopard-raws.org/rss.php"
URI="https://nyaa.si/?q=Ohys-Raws&f=0&c=1_4&page=rss"
PYTHON_PATH="python3"
CHANNEL="bot-open"
POST_FLG=1
LOG_FILE=${SCRIPT_DIR}/autopub_${DATETIME2}.log
FLG_FILE=${SCRIPT_DIR}/autopub_running
LEOPARD_INDEX=${SCRIPT_DIR}/leopard_index.html
INDEX_GET=0
NEW_RESULT_FILE=${SCRIPT_DIR}/new_program_result.txt
NEW_RESULT_FILE_NG=${SCRIPT_DIR}/new_program_result_ng.txt
NEW_PROGRAM_FILE=${SCRIPT_DIR}/new_program.txt

# 新番組日本語名取得
get_ja_title_list() {
    DL_HASH=$1
    if [ ${INDEX_GET} -eq 0 ]; then
        curl -s -S "http://jp.leopard-raws.org/" > ${LEOPARD_INDEX}
        INDEX_GET=1
    fi

    TITLE_JA="`cat ${LEOPARD_INDEX} | grep "${DL_HASH}" | head -1 | sed "s/.*>\(.*\)\ -\ .*/\1/"`"

    echo "${TITLE_JA}"
}

get_ja_title_list2() {
    TITLE_EN=$1

    # 取得した英語タイトルの "-" をスペースに変換、"："、"."、"!" を削除、3ワード分を取得
    SEARCH_WORD=`echo "${TITLE_EN}" | sed "s/-/ /g" |  sed "s/-\|\!\|：\|\.//g" | sed "s/(.*)//" | awk '{print $1,$2,$3}' | sed "s/ \+$//"`
    # スペースを+に変換したものも取得
    SEARCH_WORD_ENC=`echo "${SEARCH_WORD}" | sed "s/ /+/g"`
    # 2ワードぶん取得したもの
    SEARCH_WORD2=`echo "${TITLE_EN}" | sed "s/-/ /g" |  sed "s/-\|\!\|：\|\.//g" | sed "s/(.*)//" | awk '{print $1,$2}' | sed "s/ \+$//"`
    # スペースを+に変換したものも取得
    SEARCH_WORD_ENC2=`echo "${SEARCH_WORD2}" | sed "s/ /+/g"`

    # しょぼいカレンダーを検索、結果から日本語タイトルを抽出
    TITLE_JA=`curl -s "http://cal.syoboi.jp/find?sd=0&kw=${SEARCH_WORD_ENC}" | grep "キーワード.*${SEARCH_WORD}" | head -1 |  sed "s/<small.*small>//" | sed "s/<\/a>.*//" | sed "s/.*>//"`

    if [ "${TITLE_JA}" = "" ]; then
        TITLE_JA=`curl -s "http://cal.syoboi.jp/find?sd=0&kw=${SEARCH_WORD_ENC2}" | grep "キーワード.*${SEARCH_WORD2}" | head -1 |  sed "s/<small.*small>//" | sed "s/<\/a>.*//" | sed "s/.*>//"`
    fi

    echo "${TITLE_JA}"
}

end() {
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

# main section

# botから呼ばれた場合はslack postしない
if [ "$1" != "" ]; then
  POST_FLG=0
fi

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
err=`cat "${RSS_TEMP}" | grep "Server Error"`
if [ ! -s ${RSS_TEMP} ]; then
    curl -s -S "${URI2}" > ${RSS_TEMP}
elif [ "${err}" != "" ]; then
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
END_EPISODES=()
END_EPISODES_NG=()

# サブチェックリスト(nyaaからも取得するリスト)
while read NAME
do
  NAMES_SUB+=( "${NAME}" )
done < ${LIST_FILE2}

# チェックリストの取得
while read LAST_UPD EP_NUM NAME
do
  if [ "${LAST_UPD}" != "Last" ]; then
    LAST_UPDS+=( "${LAST_UPD}" )
    EP_NUMS+=( "${EP_NUM}" )
    NAMES+=( "${NAME%%\|*}" )
    NAMESJ+=( "${NAME#*\|}" )
  fi
done < ${LIST_FILE}

# リストチェック＆seedダウンロード処理開始：tempリストに日時を出力
echo "Last Update: ${DATETIME}" > ${LIST_TEMP}

# チェックリストの行ごとにループ
cnt=0
for NAME in "${NAMES[@]}"
do
  cnt2=1
  hit_flg=0
  # サブリストに同名タイトルが存在するか：存在する場合はsub_flgを立てる
  sub_flg=0
  for NAME_SUB in "${NAMES_SUB[@]}"
  do
    if [ "${NAME}" = "${NAME_SUB}" ]; then
      sub_flg=1
      break
    fi
  done

  # 取得したRSSをループ(leoとnyaa同時に回す)
  while :
  do
    # <title>タグ内取得
    title=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`
    title2=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML2}" | grep title | sed "s#<title>\(.*\)</title>#\1#" | sed "s/^      //"`

    # titleが空白になったらループ終了
    if [ "${title}" = "" -a "${title2}" = "" ]; then
      break
    fi

    # linkタグ内取得
    link=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`
    link2=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML2}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`

    # titleと一致するかどうかチェック
    fetch_flg=0
    if [ ${sub_flg} -eq 0 -a "`echo \"${title}\" | grep \"${NAME}\"`" != "" ]; then
        if [ "`echo \"${title}\" | grep \"Overlord III Special\"`" = "" ]; then
            fetch_flg=1
        fi
    elif [ ${sub_flg} -eq 1 -a "`echo \"${title2}\" | grep \"${NAME}\"`" != "" ]; then
      title="${title2}"
      link="${link2}"
      fetch_flg=1
    fi

    # 一致した場合、titleから話数の数値を取得
    if [ ${fetch_flg} -eq 1 ]; then
      EPNUM=`echo "${title}" | sed "s/.*${NAME}.* - \([0-9.]\{2,5\}\).*/\1/"`
      EPNUM_N=${EPNUM}

      # 取得した文字列が3桁より多い場合、.5話の可能性がある(0d.5 が4桁。d.5 の可能性は一旦考えない)
      if [ "${#EPNUM}" -gt 3 ]; then
        EPNUM=`echo "${title}" | sed "s/.*${NAME}.* \([0-9]\{2,3\}.5\) .*/\1/"`

        # 4桁以上の場合は取得エラーとみなして処理しない(ddd.5の可能性は一旦考えない)
        if [ "${#EPNUM}" -gt 4 ]; then
          (( cnt2++ ))
          continue
        fi

        # 整数に丸めるため、.5を省いて+1する
        EPNUM_N=$(( 10#${EPNUM%.*} + 1 ))
      fi

      # リストに保存されている旧話数との比較
      EPNUM_OLD_N=${EP_NUMS[${cnt}]}

      # 保存されている旧話数も.5を含む場合があるので、3桁以上の場合は.5を取り払う
      if [ "${#EPNUM_OLD_N}" -gt 3 ]; then
        if [ "${EPNUM}" = "${EPNUM_OLD_N}" ]; then
          break
        fi
        EPNUM_OLD_N=${EPNUM_OLD_N%.*}
      fi

      # 新話数 - 旧話数の差分が1のとき、新規エピソードとする
      if [ $(( 10#$EPNUM_N - 10#$EPNUM_OLD_N )) -eq 1 ]; then
        hit_flg=1
      # あいまいモード：何か引数がある場合、1以上なら新規エピソードとする
      elif [ $1 != "" -a $(( 10#$EPNUM_N - 10#$EPNUM_OLD_N )) -ge 1 ]; then
        hit_flg=1
      fi

      if [ ${hit_flg} -eq 1 ]; then
        logging "new episode: ${EPNUM} (local: ${EP_NUMS[${cnt}]})"
        hit_flg=1
        echo "${title}" >> ${RESULT_FILE}
        DOWNLOADS+=( "${link}" )

        # titleに「END」が含まれるときは終了作品チェックを行う
        if [ "`echo \"${title}\" | grep \"END\"`" != "" ]; then
          # 既に取得済みのファイル数(.5話等の話数を含まず) + 1 = 総話数
          EP_COUNT=`find ${DOWNLOAD_DIR}/*"${NAMESJ[${cnt}]}"/ -regextype posix-basic -regex ".*第[^\.]*話.*" | grep -v "第00話" |wc -l`
          (( EP_COUNT++ ))

          # ファイル個数と最終話数の個数が一致：抜け無しリストに入れる　一致しない場合は抜けありリストへ
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

  # 新規エピソードがある場合、最新話数と最終取得日時を更新して、tempリストへ追加
  # 無い場合は元のリストの行をそのまま追加
  if [ "${hit_flg}" = "1" ]; then
    echo "${DATETIME} ${EPNUM} ${NAME}|${NAMESJ[${cnt}]}" >> ${LIST_TEMP}
  else
    echo "${LAST_UPDS[${cnt}]} ${EP_NUMS[${cnt}]} ${NAME}|${NAMESJ[${cnt}]}" >> ${LIST_TEMP}
  fi
  (( cnt++ ))
done

# 新番組1話対応
cnt2=1
new_hit_flg=0
new_hit_flg_ng=0
rm -f ${NEW_RESULT_FILE}
rm -f ${NEW_RESULT_FILE_NG}

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

    # titleリストを精査して、「 - 01 」を含むものを探す
    if [[ ${title} =~ -\ 01\  ]]; then
#        link=`echo "cat /rss/channel/item[${cnt2}]" | xmllint --shell "${RSS_XML}" | grep link | sed "s#<link>\(.*\)</link>#\1#" | sed "s/^      //" | sed "s/amp;//"`
#        TITLE_EN=`echo ${title} | sed "s/\[Leopard-Raws\]\ \(.*\)\ -\ 01\ RAW.*/\1/"`
#        DL_HASH=`echo ${link} | sed "s/.*hash=\(.*\)/\1/"`
        TITLE_EN=`echo ${title} | sed "s/\[.*\]\ \(.*\)\ -\ 01\ .*/\1/"`

        # 新重複対策(TITLE_ENをリストに入れるようにした)
        if [ "`grep "${TITLE_EN}" ${NEW_PROGRAM_FILE}`" = "" ]; then
#            TITLE_JA=`get_ja_title_list "${DL_HASH}"`
            TITLE_JA=`get_ja_title_list2 "${TITLE_EN}"`

            # 日本語タイトルが取得できていたら、新番組取得済リストへ追加
            if [ "${TITLE_JA}" != "" ]; then
                # 旧しくみの重複対策(NEWリストを日本語タイトルでgrep)は残す
                # チェックリスト(tempと実体両方)に次回取得のためのレコードを追加
                if [ "`grep "${TITLE_JA}" ${NEW_PROGRAM_FILE}`" = "" ]; then
                    new_hit_flg=1
                    echo "${DATETIME} 0 ${TITLE_EN}|${TITLE_JA}" >> ${LIST_TEMP}
                    echo "${DATETIME} 0 ${TITLE_EN}|${TITLE_JA}" >> ${LIST_FILE}
                    echo "${TITLE_JA} (${TITLE_EN})" >> ${NEW_RESULT_FILE}
                    echo "${TITLE_EN}" >> ${NEW_PROGRAM_FILE}
                    mkdir -p "${DOWNLOAD_DIR}/${TITLE_JA}"
                fi
            else
                # 日本語タイトルが取得できなかった1話は何もしないが報告だけする
                new_hit_flg_ng=1
                echo "${TITLE_EN}" >> ${NEW_RESULT_FILE_NG}
            fi
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

if [ ${new_hit_flg_ng} -eq 1 ]; then
    post_msg="@here 新番組検知！
検知しましたが、日本語タイトルが検索で取得できなかったので、何もしませんでした
手動追加を検討してください
\`\`\`
`cat ${NEW_RESULT_FILE_NG}`
\`\`\`"
    logging "${post_msg}"
    slack_post "${post_msg}"
fi

# 何らかのエラーで途中で処理が途切れたりして、チェックリスト実体とtempに行数の差が出てしまった場合、警告
cd /data/share/movie/sh
if [ `cat ${LIST_TEMP} | wc -l` -ne `cat ${LIST_FILE} | wc -l` ]; then
  slack_post "@channel !!! リスト行数が変化しました。 checklist.txt のコミットログを確認してください "
fi

# 処理の終わったtempリストをソートし、実体に上書き→gitコミット
cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
git commit -m 'checklist.txt update' checklist.txt
git commit -m 'new_program.txt update' new_program.txt
git pull
git push origin master

# seedダウンロード処理終了を報告(まだ実際にseed取得はしてない)
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

# seedダウンロード・seed育成処理開始
cd /data/share/movie

for DL_LINK in "${DOWNLOADS[@]}"
do
  logging "download link: ${DL_LINK}"
  wget --no-check-certificate --restrict-file-names=nocontrol --trust-server-names --content-disposition "${DL_LINK}" -P "${DOWNLOAD_DIR}" > /dev/null
done

end

# seed育成
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

# 終了エピソードがある場合、終了リストの編集
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
