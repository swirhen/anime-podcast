#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
dir=$1

# 与えられたディレクトリ以下のパートディレクトリの数を調べる
dircnt=`ls ${dir} | wc -l`

# パートディレクトリごとにループ
for partdir in ${dir}/*
do
    # entry.jsonからtitleを取得
    title=`cat ${partdir}/entry.json | sed "s/.*title\":\"\([^\"]*\)\".*/\1/"`
    # entry.jsonからpartを取得
    part=`cat ${partdir}/entry.json | sed "s/.*part\":\"\([^\"]*\)\".*/\1/"`

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
    else
        # blvが複数ある場合はファイル名を連結
        rm -f "${filename}.list"
        for file in ${partdir}/*/*.blv
        do
            echo "file ${file}" >> "${filename}.list"
        done
        # ffmpegでconcat
        echo "/usr/bin/wine ffmpeg3.exe -f concat -i \"${filename}.list\" -c copy \"${filename}\".mp4"
    fi
done
