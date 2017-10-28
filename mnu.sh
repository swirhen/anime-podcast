# フォルダリネーム用シェル
# フォルダを連番(01-)にリネームする
# 95～99、00は無視
# shって名前のdirも無視
cnt=1
for a in *
do
  if [ `expr "$a" : "9[23456789]\|00\|sh$\|\+\+\+\|\["` -eq 0 -a -d "$a" ]; then
  #if [ `expr "$a" : "9[23456789]\|sh$"` -eq 0 -a -d "$a" ]; then
    name=`echo "$a" | sed "s/^[0-9][0-9].\(.*\)/\1/"`
    num=`echo "$a" | sed "s/^\([0-9][0-9]\).*/\1/"`
    if [ "$num" != "" ]; then
      if [ $# -ne 0 -a "$1" = "-r" ]; then
        echo "# rename $a -> $name"
        mv "$a" "$name"
      else
        if [ $cnt -le 9 -a "$a" != "0$cnt $name" ]; then
          echo "# rename $a -> 0$cnt $name"
          mv "$a" "0$cnt $name"
        elif [ $cnt -ge 10 -a "$a" != "$cnt $name" ]; then
          echo "# rename $a -> $cnt $name"
          mv "$a" "$cnt $name"
        fi
        cnt=`expr $cnt + 1`
      fi
    elif [ "$a" -ne "$name" ]; then
      if [ $cnt -le 9 ]; then
        echo "# rename $a -> 0$cnt $a"
        mv "$a" "0$cnt $a"
      else
        echo "# rename $a -> $cnt $a"
        mv "$a" "$cnt $a"
      fi
      cnt=`expr $cnt + 1`
    fi
  fi
done
