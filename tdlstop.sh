# /bin/sh
# @author swirhen
# aria2cでダウンロードを仕掛けたtorrentシードの状態を監視して終わったら止める。
# tw.py(http://handasse.blogspot.com/2009/09/pythontwitter.html)
# を使って終わったことをtwitterに報告する
# usage:tdlstop.sh [port number]
EXT=aria2
date=`date '+%y/%m/%d %H:%M:%S'`
sleep 100
n=`ls *.${EXT} 2>/dev/null | wc -l`
if [ $n -gt 1 ]; then
  for a in *.${EXT}
  do
    filea=`echo $a | cut -d"." -f1,2`
    file="$filea(ほか`expr $n - 1`個)"
    break
  done
elif [ $n -eq 1 ]; then
  filea=`ls *.${EXT}`
  file=`echo $filea | cut -d"." -f1,2`
fi
echo "$fileの栽培監視を開始"
while true
do
  pid=`ps -ef | grep port=$1 | grep -v grep | awk '{print $2}'`
  if [ "${pid:-null}" = null ]; then
    if [ `ls *.${EXT} 2>/dev/null | wc -l` -gt 0  ]; then
      echo -e "\n### watching aria2c(port=$1) end - pid lost###"
      exit
    else
      echo -e "\n### watching aria2c(port=$1) end###"
      /home/swirhen/Shellscriptter/Shellscriptter.sh -r "@swirhen 栽培完了:$date 開始のファイル: $file"
      exit
    fi
#  else
#    if [ `ls *.${EXT} 2>/dev/null | wc -l` -gt 0  ]; then
#      echo "\n### watching aria2c(port=$1) ###"
#      sleep 5
#    else
#      kill $pid
#      sleep 2
#      kill $pid
#      echo "\n### watching aria2c(port=$1) end###"
#      /data/share/movie/tw.py "@swirhen 栽培完了:$date 開始のファイル: $file"
#      exit
#    fi
  else
    echo -e "\n### watching aria2c(port=$1) ###"
    sleep 5
  fi
done
