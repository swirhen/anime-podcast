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
for a in *.avi *.mp4 *.mkv *.wmv
do
  if [ -f "$a" ]; then
    LIST=/data/share/movie/name.lst
    while read SF NAME
    do
    ext=`echo $a | sed "s/.*\.\(.*\)/\1/"`
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9]\?$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-1][0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-1][0-9][0-9]\?$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9].5\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9].5$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    done < ${LIST}
  fi
done
for a in *.avi *.mp4 *.mkv *.wmv
do
  if [ -f "$a" ]; then
    LIST=/data/share/movie/name2.lst
    while read SF NAME
    do
    ext=`echo $a | sed "s/.*\.\(.*\)/\1/"`
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9]\?$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-1][0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-1][0-9][0-9]\?$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    nn=`echo $a | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9].5\)$SFX2.*/\1/"`
    fsf=`echo $a | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9].5$SFX2.*/\1/"`
      if [ "$fsf" == "$SF" ]; then
        if [ ! -e "$a".aria2 ]; then
          if [ "$a" != "${NAME} 第$nn話.$ext" ]; then
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            mv "$a" "${NAME} 第$nn話.$ext"
          else
            echo "# rename $a -> ${NAME} 第$nn話.$ext"
            echo "# 変更後のファイル名が同じ"
          fi
        else
          echo "# $a 成育中！"
        fi
        break
      fi
    done < ${LIST}
  fi
done
