#!/usr/bin/env bash
# ディレクトリリネーム用シェル
# ディレクトリを連番+スペースつきにリネームする
# 92～99、00で開始するディレクトリは無視
# shって名前のdirも無視
# 引数 "-r" をつけると先頭の連番とスペースを削除
cnt=1
for dir in *
do
    if [[ "${dir}" !=~ ^9[2-9]\|^00\|^sh && -d "${dir}" ]]; then
        NAME=`echo "${dir}" | sed "s/^[0-9][0-9]\ \(.*\)/\1/"`
        #NUM=`echo "${dir}" | sed "s/^\([0-9][0-9]\)\ .*/\1/"`
        cnt=`printf %02d ${cnt}`

        if [ $# -ne 0 -a "$1" = "-r" -a "${dir}" != "${NAME}" ]; then
            echo "# rename ${dir} -> ${NAME}"
            mv "${dir}" "${NAME}"
        elif [ "${dir}" != "${cnt} ${NAME}" ]; then
            echo "# rename ${dir} -> ${cnt} ${NAME}"
            mv "${dir}" "${cnt} ${NAME}"
        fi
    fi
    (( cnt++ ))
done
