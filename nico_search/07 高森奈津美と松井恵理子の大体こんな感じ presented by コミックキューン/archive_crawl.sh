cd "/data/share/temp/voiceactor_nico_ch/07"*
a=`date +%w`
if [ "$a" = "4" ]; then
  KAI=`cat resent`
  ../crawlnicoch.sh "http://ch.nicovideo.jp/voice-style/video" | grep "高森奈津美と松井恵理子の大体こんな感じ" | grep ${KAI}回 | grep -v おまけ動画 > archive_dl.sh
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
