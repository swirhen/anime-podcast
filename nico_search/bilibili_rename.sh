#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
RENAME_LIST_FILE=${SCRIPT_DIR}/bilibili_rename_word.txt
NICO_LIST_FILE=${SCRIPT_DIR}/nico_rename_word.txt
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
    KEYWORDS+=( "${KEYWORD//%/\\ }" )
    NUM_PREFIXS+=( "${NUM_PREFIX}" )
    NUM_SUFFIXS+=( "${NUM_SUFFIX//%/}" )
    PADDING_DIGITS+=( ${PADDING_DIGIT} )
    PROGRAM_NAMES+=( "${PROGRAM_NAME//%/ }" )
    FILENAME_LAYOUTS+=( "${FILENAME_LAYOUT//%/ }" )
    FOOTER_KEYWORDS+=( "${FOOTER_KEYWORD//%/\\ }" )
    DELETE_KEYWORDS+=( "${DELETE_KEYWORD//%/ }" )
done < ${RENAME_LIST_FILE}

NICO_DIR_PREFIXS=()
NICO_KEYWORDS=()
NICO_SED_STRS=()
while read DIR_PREFIX KEYWORD AUDIO_ENCODE SED_STR
do
    NICO_DIR_PREFIXS+=( "${DIR_PREFIX}" )
    NICO_KEYWORDS+=( "${KEYWORD}" )
    NICO_SED_STRS+=( "${SED_STR}" )
    NICO_AUDIO_ENCODES+=( "${AUDIO_ENCODE}" )
done < ${NICO_LIST_FILE}

# にこきゃっしゅ
if [ "${dir: -3}" = "mp4" ]; then
    jsonfile="${dir%.*}.json"
    title=`cat "${jsonfile}" | jq ".videoTitle" | sed "s/\"//g"`

    cnt=0
    hit_flg=0
    while :
    do
        if [ "${NICO_KEYWORDS[${cnt}]}" = "" ]; then
            break
        fi

        if [[ ${title} =~ ${NICO_KEYWORDS[${cnt}]} ]]; then
            DIR_PREFIX="${NICO_DIR_PREFIXS[${cnt}]}"
            SED_STR="${NICO_SED_STRS[${cnt}]}"
            AUDIO_ENCODE=${NICO_AUDIO_ENCODES[${cnt}]}
            hit_flg=1
            break
        fi
        (( cnt++ ))
    done

    if [ ${hit_flg} -eq 1 ]; then
        if [ "${SED_STR}" != "" ]; then
            title=`echo "${title}" | sed "y/０１２３４５６７８９　/0123456789 /" | sed "${SED_STR}"`
        else
            title=`echo "${title}" | sed "y/０１２３４５６７８９　/0123456789 /"`
        fi
        if [ "${AUDIO_ENCODE}" = "1" ]; then
            echo "mv \"${dir}\" \"${title}.mp4\""
            echo "/usr/bin/wine ffmpeg3.exe -i \"${title}.mp4\" -acodec copy -map 0:1 \"${title}.m4a\""
            echo "mv \"${title}.mp4\" ${DIR_PREFIX}*/mp4/"
            echo "mv \"${title}.m4a\" ${DIR_PREFIX}*/"
        else
            echo "mv \"${dir}\" \"${title}.mp4\""
            echo "mv \"${title}.mp4\" ${DIR_PREFIX}*/"
        fi
    else
        echo "mv \"${dir}\" \"${title}.mp4\""
    fi

    exit 0
elif [ "${dir: -4}" = "json" ]; then
    exit 0
elif [ "${dir: -4}" = ".thm" ]; then
    exit 0
elif [ "${dir: -4}" = ".xml" ]; then
    exit 0
fi

# 与えられたディレクトリ以下のパートディレクトリの数を調べる
dircnt=`ls "${dir}" | wc -l`

# パートディレクトリごとにループ
for partdir in "${dir}"/*
do
    # entry.jsonからtitleを取得
    title=`cat "${partdir}"/entry.json | jq ".title" | sed "s/\"//g" | sed 's#\/##g' | sed 's#\\\#_#g'`
    # entry.jsonからpartを取得
    part=`cat "${partdir}"/entry.json | jq ".page_data.part" | sed "s/\"//g" | sed 's#\/##g' | sed 's#\\\#_#g'`

    # blv保存ディレクトリの下のblvファイル数を調べる
    filecnt=`ls "${partdir}"/*/*.blv | wc -l`
    # blv保存ディレクトリの下のvideo.m4sファイル数を調べる
    filecnt2=`ls "${partdir}"/*/video.m4s | wc -l`

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

    filename=`echo "${filename}" | sed "s/嘉宾/ゲスト/g" | sed "s/:/：/g"`

    if [ ${filecnt} -eq 1 ]; then
        # blvが1個だけの場合
        echo "/usr/bin/wine ffmpeg3.exe -i \"${partdir}\"/*/0.blv -c copy \"${filename}.mp4\""
    elif [ ${filecnt} -eq 0 ]; then
        # 0個の場合(普通無い)新形式の可能性
        if [ ${filecnt2} -eq 1 ]; then
            # ffmpegでmux
            echo "/usr/bin/wine ffmpeg3.exe -i \"${partdir}\"/*/video.m4s -i \"${partdir}\"/*/audio.m4s -c copy \"${filename}.mp4\""
        else
            # TODO 2個以上の時(あるのか？)
            continue
        fi
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
