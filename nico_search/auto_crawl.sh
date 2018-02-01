#!/usr/bin/env bash
# ニコニコチャンネル or 検索 オートクロール
# リストから検索URL(チャンネルの場合はビデオリスト、検索の場合は検索URL)をクロールして、キーワードと話数指定で最新話数があったら
# ダウンロードして保存、ニコニコのフィードにリリースする
# リスト形式：
# 最終更新 最新回数+1 検索URL 検索キーワード 保存ディレクトリ連番 回数プレフィクス 回数サフィクス sed文言
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LIST_FILE=${SCRIPT_DIR}/checklist.txt
LIST_TEMP=${SCRIPT_DIR}/checklist.temp
DATETIME=`date "+%Y/%m/%d-%H:%M:%S"`
DATETIME2=`date "+%Y%m%d%H%M%S"`
PYTHON_PATH="python3"
CHANNEL="bot-sandbox"
NICODL_CMD="/data/share/movie/sh/nicodl.sh"
POST_FLG=1
LOG_FILE=${SCRIPT_DIR}/autocrawl_${DATETIME2}.log
FLG_FILE=${SCRIPT_DIR}/autocrawl_running
DL_SH=${SCRIPT_DIR}/dl.sh

end() {
#    mv ${LOG_FILE} ${SCRIPT_DIR}/logs/
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
    end
else
    touch ${FLG_FILE}
fi

# リストから各種変数を読み込む
LAST_UPDS=()
EP_NUMS=()
URLS=()
KEYWORDS=()
SAVE_DIR_NUMS=()
NUM_PREFIXS=()
NUM_SUFFIXS=()
SED_STRS=()

echo "Last Update: ${DATETIME}" > ${LIST_TEMP}
while read LAST_UPD EP_NUM URL KEYWORD SAVE_DIR_NUM NUM_PREFIX NUM_SUFFIX SED_STR
do
    if [ "${LAST_UPD}" != "Last" ]; then
        LAST_UPDS+=( "${LAST_UPD}" )
        EP_NUMS+=( "${EP_NUM}" )
        URLS+=( "${URL}" )
        KEYWORDS+=( "${KEYWORD}" )
        SAVE_DIR_NUMS+=( "${SAVE_DIR_NUM}" )
        NUM_PREFIXS+=( ${NUM_PREFIX} )
        NUM_SUFFIXS+=( ${NUM_SUFFIX} )
        SED_STRS+=( "${SED_STR}" )
    fi
done < ${LIST_FILE}

cnt=0
dl_flg=0
while :
do
    if [ "${LAST_UPDS[${cnt}]}" = "" ]; then
        break
    fi
#    echo "LAST_UPDS: ${LAST_UPDS[${cnt}]}"
#    echo "EP_NUMS: ${EP_NUMS[${cnt}]}"
#    echo "URLS: ${URLS[${cnt}]}"
#    echo "KEYWORDS: ${KEYWORDS[${cnt}]}"
#    echo "SAVE_DIR_NUMS: ${SAVE_DIR_NUMS[${cnt}]}"
#    echo "NUM_PREFIXS: ${NUM_PREFIXS[${cnt}]}"
#    echo "NUM_SUFFIXS: ${NUM_SUFFIXS[${cnt}]}"
#    echo "SED_STRS: ${SED_STRS[${cnt}]}"
    LAST_UPD="${LAST_UPDS[${cnt}]}"
    EP_NUM=${EP_NUMS[${cnt}]}
    URL="${URLS[${cnt}]}"
    KEYWORD="${KEYWORDS[${cnt}]}"
    SAVE_DIR_NUM="${SAVE_DIR_NUMS[${cnt}]}"
    NUM_PREFIX=${NUM_PREFIXS[${cnt}]}
    NUM_SUFFIX=${NUM_SUFFIXS[${cnt}]}
    SED_STR="${SED_STRS[${cnt}]}"
    if [ "${NUM_PREFIX}" != "|" ]; then
        EPNUM=${NUM_PREFIX}${EP_NUM}
    else
        EPNUM=${EP_NUM}
    fi
    if [ "${NUM_SUFFIX}" != "|" ]; then
        EPNUM=${EPNUM}${NUM_SUFFIX}
    fi

    # curlでURLからクロールする
    if [ "${URL:8:2}" = "ww" ]; then
        curl -sS "${URL}" | grep ".*a title.*${KEYWORD}" | sed "s#^.*<a.*title=\"\(.*\)\".*href=\"\(.*\)?ref.*#${NICODL_CMD} \"http://www.nicovideo.jp\2\" \"\1\"#" | grep "${EPNUM}" | sed "${SED_STR}" > ${DL_SH}
    else
        curl -sS "${URL}" | grep "http.*title.*${KEYWORD}" | sed "s#^.*<a href=#${NICODL_CMD} #" | sed "s/title=//" | grep "${EPNUM}" | sed "${SED_STR}" > ${DL_SH}
    fi

    # dl.shが吐かれたらdl.shを実行
    # 最新話数をインクリメントして、tempリストに吐き出す(最終更新を更新)
    # 吐かれていなければインクリメントせずに吐き出す
    if [ -s ${DL_SH} ]; then
        dl_flg=1
        chmod +x ${DL_SH}
        ${DL_SH}
        mv *"${KEYWORD}"*.mp4 "${SCRIPT_DIR}/${SAVE_DIR_NUM}"*
        (( EP_NUM++ ))
        echo "${DATETIME} ${EP_NUM} ${URL} ${KEYWORD} ${SAVE_DIR_NUM} ${NUM_PREFIX} ${NUM_SUFFIX} ${SED_STR}" >> ${LIST_TEMP}
    else
        echo "${LAST_UPD} ${EP_NUM} ${URL} ${KEYWORD} ${SAVE_DIR_NUM} ${NUM_PREFIX} ${NUM_SUFFIX} ${SED_STR}" >> ${LIST_TEMP}
    fi
    (( cnt++ ))
done

cd ${SCRIPT_DIR}
if [ ${dl_flg} -eq 1 ]; then
    cat ${LIST_TEMP} | sort -r > ${LIST_FILE}
    git commit -m 'checklist.txt update' checklist.txt
    git pull
    git push origin master
fi

end