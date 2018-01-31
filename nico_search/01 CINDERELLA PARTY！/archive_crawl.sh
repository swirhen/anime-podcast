cd "/data/share/temp/voiceactor_nico_ch/01 CINDERELLA PARTY！"
KAI=`cat p_resent`
../crawlnicoch.sh "http://ch.nicovideo.jp/cinderellaparty/video" | grep ${KAI}回 | grep アーカイブ動画 | sed "s/\(第${KAI}回\).*\(CINDERELLA PARTY\).*アーカイブ動画\(.*\)/\2！ \1 \3/" > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > p_resent
fi
