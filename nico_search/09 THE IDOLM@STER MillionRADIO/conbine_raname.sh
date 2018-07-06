#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
dir=$1

# 与えられたディレクトリ以下のパートディレクトリの数を調べる
dircnt=`ls ${dir} | wc -l`

# パートディレクトリごとにループ
for partdir in ${dir}/*
do
    # entry.jsonからtitleを取得
    title=`cat ${partdir}/entry.json | sed "s/.*title\":\"\(.*\)\",\"time.*/\1\n/"`
    # entry.jsonからpartを取得
    part=`cat ${partdir}/entry.json | sed "s/.*part\":\"\(.*\)\",\"vid.*/\1\n/"`

    # blv保存ディレクトリの下のblvファイル数を調べる
    filecnt=`ls ${partdir}/*/*.blv | wc -l`

    # ファイル名=title
    filename="${title}"
    # 複数パートある場合はファイル名にpartを付加
    if [ ${dircnt} -ne 1 ]; then
        filename+=" ${part}"
    fi

    if [ ${filecnt} -eq 1 ]; then
        # blvが1個だけの場合はリネーム
        echo "mv ${partdir}/*/0.blv \"${filename}\".mp4"
        # mv ${partdir}/*/0.blv "${filename}".mp4
    else
        # blvが複数ある場合はファイル名を連結
        files=""
        for file in ${partdir}/*/*.blv
        do
            if [ "${files}" = "" ]; then
                files="${file}"
            else
                files+="|${file}"
            fi
        done
        # ffmpegでconcat
        echo "/usr/bin/wine ffmpeg3.exe -i \"concat:${files}\" -c copy \"${filename}\".mp4"
        # /usr/bin/wine ffmpeg3.exe -i "concat:${files}" -c copy "${filename}".mp4
    fi
done