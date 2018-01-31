cd "/data/share/temp/voiceactor_nico_ch/09"*
KAI=`cat archive`
../crawlnicoch.sh "http://ch.nicovideo.jp/MillionRADIO/video" | grep ${KAI}回 > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > archive
fi
