#!/usr/bin/env bash
# swirhen.tv 新番組追加用シェル
# 引数に1話のファイルの英語タイトルを与えると
# http://jp.leopard-raws.org/ の現在放送中番組を検索して日本語タイトルを取得する
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"

ARG_TITLE_EN="$1"

LEOPARD_INDEX=${SCRIPT_DIR}/leopard_index.html
curl -s -S "http://jp.leopard-raws.org/" > ${LEOPARD_INDEX}

TITLE_EN_LIST_FILE=${SCRIPT_DIR}/title_en.list
TITLE_JA_LIST_FILE=${SCRIPT_DIR}/title_ja.list

cat ${LEOPARD_INDEX} | grep -A 1 "/?search" | grep "のRSS" | sed "s/.*='\(.*\)のRSS.*/\1/" > ${TITLE_EN_LIST_FILE}
cat ${LEOPARD_INDEX} | grep "/?search" | sed "s/.*>\(.*\)<.*/\1/" > ${TITLE_JA_LIST_FILE}

TITLE_EN_LIST=()
TITLE_JA_LIST=()

while read TITLE_EN
do
    TITLE_EN_LIST+=( "${TITLE_EN}" )
done < ${TITLE_EN_LIST_FILE}

while read TITLE_JA
do
    TITLE_JA_LIST+=( "${TITLE_JA}" )
done < ${TITLE_JA_LIST_FILE}

i=0
hit_flg=0
for TITLE_EN in "${TITLE_EN_LIST[@]}"
do
    # if [[ ${TITLE_EN} =~ ${ARG_TITLE_EN} ]]; then
    if [ "${TITLE_EN}" = "${ARG_TITLE_EN}" ]; then
      hit_flg=1
      echo "${TITLE_JA_LIST[${i}]}"
      break
    fi
    (( i++ ))
done

if [ ${hit_flg} -eq 0 ]; then
    echo "not found"
fi