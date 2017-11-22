#!/usr/bin/env bash
# 音泉くろーらー
# http://www.onsen.ag/app/programs.xml をクロールして更新あったら報告
# temp 以下に最新回数をidをファイル名に保存
# download 以下にidのファイルがあったらagqr向けにダウンロード
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
DOWNLOAD_DIR="${SCRIPT_DIR}/../../98 PSP用/agqr"
TEMP_DIR="${SCRIPT_DIR}/temp"
XML_URI="http://www.onsen.ag/app/programs.xml"
PYTHON_PATH="python3"
CHANNEL="bot-open"
RSS_TEMP=${SCRIPT_DIR}/onsen.temp
RSS_XML=${SCRIPT_DIR}/onsen.xml
RSS_OLD=${SCRIPT_DIR}/onsen.old
RESULT_FILE=${SCRIPT_DIR}/onsen.result
SWTV_URI="http://swirhen.tv/movie/pspmp4/agqr/"
T_WDAY=`date "+%w"`

slack_post() {
  ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "${CHANNEL}" "$1"
}

slack_upload() {
  /usr/bin/curl -F channels="${CHANNEL}" -F file="@$1" -F title="$2" -F token=`cat ${SCRIPT_DIR}/../token` -F filetype=text https://slack.com/api/files.upload
}

end() {
  mv ${RSS_XML} ${RSS_OLD}
  rm -f ${RESULT_FILE}
  exit 0
}

rm -f ${RESULT_FILE}

curl -s -S "${XML_URI}" > ${RSS_TEMP}
xmllint --format ${RSS_TEMP} > ${RSS_XML}

if [ "`diff ${RSS_XML} ${RSS_OLD}`" = "" ]; then
  if [ "${1:0:1}" != "f" ]; then
    end
  fi
fi

cnt=1
while :
do
  progid=`echo "cat /programs/program[${cnt}]/@id" | xmllint --shell "${RSS_XML}" | grep id= | sed "s/.*id=\"\(.*\)\"/\1/"`
  title=`echo "cat /programs/program[${cnt}]/title" | xmllint --shell "${RSS_XML}" | grep "<title>" | sed "s#<title>\(.*\)</title>#\1#"`
  wday=`echo "cat /programs/program[${cnt}]/wday" | xmllint --shell "${RSS_XML}" | grep "<wday>" | sed "s#<wday>\(.*\)</wday>#\1#"`
  movie_url=`echo "cat /programs/program[${cnt}]/movie_url" | xmllint --shell "${RSS_XML}" | grep "<movie_url>" | sed "s#<movie_url>\(.*\)</movie_url>#\1#"`
  android_url=`echo "cat /programs/program[${cnt}]/android_url" | xmllint --shell "${RSS_XML}" | grep "<android_url>" | sed "s#<android_url>\(.*\)</android_url>#\1#"`
  movie=`echo "cat /programs/program[${cnt}]/category/movie" | xmllint --shell "${RSS_XML}" | grep "<movie>" | sed "s#<movie>\(.*\)</movie>#\1#"`
  up_date=`echo "cat /programs/program[${cnt}]/up_date" | xmllint --shell "${RSS_XML}" | grep "<up_date>" | sed "s#<up_date>\(.*\) .*</up_date>#\1#"`
  program_number=`echo "cat /programs/program[${cnt}]/program_number" | xmllint --shell "${RSS_XML}" | grep "<program_number>" | sed "s#<program_number>\(.*\)</program_number>#\1#"`
  if [ "${movie}" = "1" ]; then
    download_url="${movie_url}"
    ext=${movie_url##*.}
  else
    download_url="${android_url}"
    ext=${android_url##*.}
  fi
  filename="[音泉] ${title} #${program_number} (${up_date}).${ext}"
  if [ "${title}" = "" ]; then
    break
  fi
  # 曜日チェック
  if [ "${1:1:1}" != "w" -a "${T_WDAY}" != "${wday}" ]; then
    (( cnt++ ))
    continue
  fi
  # 更新チェック
  if [ "`cat ${TEMP_DIR}/${progid}`" = "${program_number}" ]; then
    (( cnt++ ))
    continue
  fi
  # ダウンロードチェック
  dlflg=0
  if [ -f "${DOWNLOAD_DIR}/${progid}" ]; then
    dlflg=1
  fi

  echo "[${cnt}] ${progid} : ${title}"
  echo "wday : ${wday}"
  echo "movie : ${movie}"
  echo "program_number : ${program_number}"
  echo "up_date : ${up_date}"
  echo "android_url : ${android_url}"
  echo "movie_url : ${movie_url}"
  echo "filename : ${filename}"

  # ダウンロード
  if [ ${dlflg} -eq 1 ]; then
    curl "${download_url}" -o "${filename}"
    echo "${title} #${program_number} : ${SWTV_URI}${filename}" >> ${RESULT_FILE}
  else
    echo "${title} #${program_number} : ${download_url}" >> ${RESULT_FILE}
  fi

  echo "${program_number}" > "${TEMP_DIR}/${progid}"
  (( cnt++ ))
done

  if [ -s ${RESULT_FILE} ]; then
    post_msg="[音泉 更新チェック] 更新がありました
\`\`\`
`cat ${RESULT_FILE}`
\`\`\`"
    slack_post "${post_msg}"
  fi

end
