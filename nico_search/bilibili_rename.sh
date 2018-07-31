#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
RENAME_LIST_FILE=${SCRIPT_DIR}/bilibili_rename_word.txt
dir=$1

KEYWORDS=()
NUM_PREFIXS=()
NUM_SUFFIXS=()
PADDING_DIGITS=()
PROGRAM_NAMES=()
FILENAME_LAYOUTS=()
FOOTER_KEYWORDS=()
while read KEYWORD NUM_PREFIX NUM_SUFFIX PADDING_DIGIT PROGRAM_NAME FILENAME_LAYOUT FOOTER_KEYWORD
do
    KEYWORDS+=( "${KEYWORD}" )
    NUM_PREFIXS+=( "${NUM_PREFIX}" )
    NUM_SUFFIXS+=( "${NUM_SUFFIX}" )
    PADDING_DIGITS+=( ${PADDING_DIGIT} )
    PROGRAM_NAMES+=( "${PROGRAM_NAME//_/ }" )
    FILENAME_LAYOUTS+=( "${FILENAME_LAYOUT//%/ }" )
    FOOTER_KEYWORDS+=( "${FOOTER_KEYWORD}" )
done < ${RENAME_LIST_FILE}

# 与えられたディレクトリ以下のパートディレクトリの数を調べる
dircnt=`ls "${dir}" | wc -l`

# パートディレクトリごとにループ
for partdir in "${dir}"/*
do
    # entry.jsonからtitleを取得
    title=`cat "${partdir}"/entry.json | sed "s/.*title\":\"\([^\"]*\)\".*/\1/" | sed 's#\/##g' | sed 's#\\\#_#g'`
    # entry.jsonからpartを取得
    part=`cat "${partdir}"/entry.json | sed "s/.*part\":\"\([^\"]*\)\".*/\1/" | sed 's#\/##g' | sed 's#\\\#_#g'`

    # blv保存ディレクトリの下のblvファイル数を調べる
    filecnt=`ls "${partdir}"/*/*.blv | wc -l`

    # ファイル名=title
    filename="${title}"
    # 複数パートある場合はファイル名にpartを付加
    if [ ${dircnt} -ne 1 ]; then
        filename+=" ${part}"
    fi

    cnt=0
    hit_flg=0
    while :
    do
        if [[ ${filename} =~ ${KEYWORDS[${cnt}]} ]]; then
            NUM_PREFIX="${NUM_PREFIXS[${cnt}]}"
            NUM_SUFFIX="${NUM_SUFFIXS[${cnt}]}"
            PADDING_DIGIT="${PADDING_DIGITS[${cnt}]}"
            PROGRAM_NAME="${PROGRAM_NAMES[${cnt}]}"
            FILENAME_LAYOUT="${FILENAME_LAYOUTS[${cnt}]}"
            FOOTER_KEYWORD="${FOOTER_KEYWORDS[${cnt}]}"
            hit_flg=1
            break
        fi
        (( cnt++ ))
    done
    if [ ${hit_flg} -eq 1 ]; then
        NUM=`echo ${filename} | sed "s/.*${NUM_PREFIX}\([0-9]*\)${NUM_SUFFIX}.*/\1/"`
        NUM=`printf %0${PADDING_DIGIT}d ${NUM}`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##PROGRAM_NAME##/${PROGRAM_NAME}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM_PREFIX##/${NUM_PREFIXS}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM_SUFFIX##/${NUM_SUFFIX}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM##/${NUM}/"`
        if [ "${FOOTER_KEYWORD}" != "" ]; then
            FOOTER=`echo ${filename} | sed "s/.*${FOOTER_KEYWORD}\(.*\)/\1/"`
            FILENAME_LAYOUT+="${FOOTER}"
        fi
        filename="${FILENAME_LAYOUT}"
    fi

    if [ ${filecnt} -eq 1 ]; then
        # blvが1個だけの場合
        echo "/usr/bin/wine ffmpeg3.exe -i \"${partdir}\"/*/0.blv -c copy \"${filename}.mp4\""
    elif [ ${filecnt} -eq 0 ]; then
        # 0個の場合(普通無い)なにもしない
        i=0
    else
        rm -f "${filename}.list"
        for file in `eval echo "${partdir}"/*/{0..$(( filecnt - 1 ))}.blv`
        do
            echo "file ${file}" >> "${filename}.list"
        done
        # ffmpegでconcat
        echo "/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i \"${filename}.list\" -c copy \"${filename}.mp4\"; rm -f \"${filename}.list\""
    fi
done
