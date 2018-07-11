#!/usr/bin/env zsh
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
        # 0個の場合(普通無い)なにもしない
        i=0
    else
#        files="${partdir}/*/[0-9].blv"
#        if [ ${filecnt} -le 10 ]; then
#            files+=" ${partdir}/*/[1-9][0-9].blv"
#        fi
#        rm -f "${filename}.list"
#        for file in ${files}
#        do
#            echo "file ${file}" >> "${filename}.list"
#        done
        for file in ${partdir}/*/{0..$(( filecnt - 1 ))}.blv
        do
            echo "file ${file}" >> "${filename}.list"
        done
        # ffmpegでconcat
        echo "/usr/bin/wine ffmpeg3.exe -safe 0 -f concat -i \"${filename}.list\" -c copy \"${filename}.mp4\"; rm -f \"${filename}.list\""
    fi
done
