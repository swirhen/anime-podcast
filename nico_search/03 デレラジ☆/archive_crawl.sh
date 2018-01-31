cd "/data/share/temp/voiceactor_nico_ch/03 デレラジ☆"
KAI=`cat resent`
../crawlnicoch.sh "http://ch.nicovideo.jp/dereradi/video" | grep ${KAI}回 | sed "s/「デレラジ.*\(${KAI}\)回アーカイブ/デレラジ☆(スター) 第\1回/" > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
