#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
dir=$1

# 与えられたディレクトリ以下のパートディレクトリの数を調べる
dircnt=`ls ${dir} | wc -l`

# パートディレクトリごとにループ
for partdir in ${dir}/*
do
    # entry.jsonからtitleを取得
    title=`cat ${partdir}/entry.json | sed "s/.*title\":\"\([^\"]*\)\".*/\1/" | sed 's#\/##g' | sed 's#\\\#_#g'`
    # entry.jsonからpartを取得
    part=`cat ${partdir}/entry.json | sed "s/.*part\":\"\([^\"]*\)\".*/\1/" | sed 's#\/##g' | sed 's#\\\#_#g'`

    # blv保存ディレクトリの下のblvファイル数を調べる
    filecnt=`ls ${partdir}/*/*.blv | wc -l`

    # ファイル名=title
    filename="${title}"
    # 複数パートある場合はファイル名にpartを付加
    if [ ${dircnt} -ne 1 ]; then
        filename+=" ${part}"
    fi

    if [ ${filecnt} -eq 1 ]; then
        # blvが1個だけの場合
        echo "/usr/bin/wine ffmpeg3.exe -i ${partdir}/*/0.blv -c copy \"${filename}.mp4\""
    elif [ ${filecnt} -eq 0 ]; then
        # 0個の場合(普通無い)
        i=0
    else
        # blvが複数ある場合はファイル名を連結
        add=""
        # 10個以上の場合
        if [ ${filecnt} -gt 10 ]; then
            add=" ${partdir}/*/[1-9][0-9].blv"
        fi
        # ffmpegでconcat
        echo "/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i <(for file in ${partdir}/*/[0-9].blv${add}; do echo \"file '\${PWD}/\${file}'\"; done) -c copy \"${filename}.mp4\""
    fi
done
