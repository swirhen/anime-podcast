#!/bin/bash
# 動画リネーム用シェル
# リネーム用リストにはリネーム元ファイルの検索文字と正式な作品名を
# tabで繋げて記述すること
# 第1引数(省略可)はリネーム元ファイルの話数数字の前の文字を入力する。デフォルトは半角スペース。
# 第2引数(省略可)はリネーム元ファイルの話数数字の後の文字を入力する。デフォルトは半角スペースもしくは、第1引数が指定されている場合は第1引数。
SFX1=" "
SFX2=" "
if [ $# -eq 1 ]; then  # 引数が1個
SFX1=$1
SFX2=$1
fi
if [ $# -eq 2 ]; then  # 引数が2個
SFX1=$1
SFX2=$2
fi
LIST=/data/share/movie/checklist.txt
NAME_LST1=()
FILE_LST=()
while read DUMMY DUMMY LINE
do
  if [ "${LINE}" != "" ]; then
    NAME_LST1+=( "${LINE}" )
  fi
done < ${LIST}
while read -r FILENAME
do
  FILE_LST+=( "${FILENAME:2}" )
done < <(find . -maxdepth 1 -type f \( -name \*.mp4 -o -name \*.wmv -o -name \*.mkv -o -name *.avi \))

for FILE_NAME in "${FILE_LST[@]}"
do
  for LINE in "${NAME_LST1[@]}"
  do
    SF="${LINE%%\|*}"
    NAME="${LINE#*\|}"
    ext=`echo $FILE_NAME | sed "s/.*\.\(.*\)/\1/"`

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9]\?$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} 第$nn話.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          mv "$FILE_NAME" "${NAME} 第$nn話.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          echo "# 変更後のファイル名が同じ"
        fi
      else
        echo "# $FILE_NAME 成育中！"
      fi
      break
    fi

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-1][0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-1][0-9][0-9]\?$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} 第$nn話.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          mv "$FILE_NAME" "${NAME} 第$nn話.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          echo "# 変更後のファイル名が同じ"
        fi
      else
        echo "# $FILE_NAME 成育中！"
      fi
      break
    fi

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9].5\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9].5$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} 第$nn話.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          mv "$FILE_NAME" "${NAME} 第$nn話.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} 第$nn話.$ext"
          echo "# 変更後のファイル名が同じ"
        fi
      else
        echo "# $FILE_NAME 成育中！"
      fi
      break
    fi
  done
done
