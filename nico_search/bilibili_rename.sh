#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
RENAME_LIST_FILE=${SCRIPT_DIR}/bilibili_rename_word.txt
dir=$1

DIR_PREFIXS=()
AUDIO_ENCODES=()
KEYWORDS=()
NUM_PREFIXS=()
NUM_SUFFIXS=()
PADDING_DIGITS=()
PROGRAM_NAMES=()
FILENAME_LAYOUTS=()
FOOTER_KEYWORDS=()
DELETE_KEYWORDS=()
while read DIR_PREFIX AUDIO_ENCODE KEYWORD NUM_PREFIX NUM_SUFFIX PADDING_DIGIT PROGRAM_NAME FILENAME_LAYOUT FOOTER_KEYWORD DELETE_KEYWORD
do
    DIR_PREFIXS+=( "${DIR_PREFIX}" )
    AUDIO_ENCODES+=( ${AUDIO_ENCODE} )
    KEYWORDS+=( "${KEYWORD}" )
    NUM_PREFIXS+=( "${NUM_PREFIX}" )
    NUM_SUFFIXS+=( "${NUM_SUFFIX//%/}" )
    PADDING_DIGITS+=( ${PADDING_DIGIT} )
    PROGRAM_NAMES+=( "${PROGRAM_NAME//%/ }" )
    FILENAME_LAYOUTS+=( "${FILENAME_LAYOUT//%/ }" )
    FOOTER_KEYWORDS+=( "${FOOTER_KEYWORD//%/\\ }" )
    DELETE_KEYWORDS+=( "${DELETE_KEYWORD//%/ }" )
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
        if [ "${KEYWORDS[${cnt}]}" = "" ]; then
            break
        fi

        if [[ ${filename} =~ ${KEYWORDS[${cnt}]} ]]; then
            DIR_PREFIX="${DIR_PREFIXS[${cnt}]}"
            AUDIO_ENCODE=${AUDIO_ENCODES[${cnt}]}
            NUM_PREFIX="${NUM_PREFIXS[${cnt}]}"
            NUM_SUFFIX="${NUM_SUFFIXS[${cnt}]}"
            PADDING_DIGIT=${PADDING_DIGITS[${cnt}]}
            PROGRAM_NAME="${PROGRAM_NAMES[${cnt}]}"
            FILENAME_LAYOUT="${FILENAME_LAYOUTS[${cnt}]}"
            FOOTER_KEYWORD="${FOOTER_KEYWORDS[${cnt}]}"
            DELETE_KEYWORD="${DELETE_KEYWORDS[${cnt}]}"
            hit_flg=1
            break
        fi
        (( cnt++ ))
    done
    if [ ${hit_flg} -eq 1 ]; then
        NUM=`echo ${filename} | sed "s/.*${NUM_PREFIX}\([0-9]*\)${NUM_SUFFIX}.*/\1/"`
        NUM=`printf %0${PADDING_DIGIT}d $(( 10#${NUM} ))`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##PROGRAM_NAME##/${PROGRAM_NAME}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM_PREFIX##/${NUM_PREFIXS}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM_SUFFIX##/${NUM_SUFFIX}/"`
        FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/##NUM##/${NUM}/"`
        if [ "${FOOTER_KEYWORD}" != "" ]; then
            FOOTER=`echo "${filename}" | sed "s/.*${FOOTER_KEYWORD}\(.*\)/\1/"`
            if [ "${FOOTER}" != "" -a "${FOOTER}" != "${filename}" ]; then
                FILENAME_LAYOUT+=" ${FOOTER}"
            fi
        fi
        if [ "${DELETE_KEYWORD}" != "" ]; then
            FILENAME_LAYOUT=`echo "${FILENAME_LAYOUT}" | sed "s/${DELETE_KEYWORD}//"`
        fi
        filename="${FILENAME_LAYOUT}"
    fi

    filename=`echo "${filename}" | sed "s/嘉宾/ゲスト/"`

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
    if [ "${AUDIO_ENCODE}" = "1" ]; then
        echo "/usr/bin/wine ffmpeg3.exe -i \"${filename}.mp4\" -acodec copy -map 0:1 \"${filename}.m4a\""
        if [ "${DIR_PREFIX}" != "" ]; then
            echo "mv \"${filename}.mp4\" ${DIR_PREFIX}*/mp4/"
            echo "mv \"${filename}.m4a\" ${DIR_PREFIX}*/"
        fi
    else
        if [ "${DIR_PREFIX}" != "" ]; then
            echo "mv \"${filename}.mp4\" ${DIR_PREFIX}*/"
        fi
    fi
done
