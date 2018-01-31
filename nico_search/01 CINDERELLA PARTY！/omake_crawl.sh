cd "/data/share/temp/voiceactor_nico_ch/01 CINDERELLA PARTY！"
KAI=`cat resent`
../crawlnicoch.sh "http://ch.nicovideo.jp/cinderellaparty/video" | grep ${KAI}回 | sed "s/\(第${KAI}回\).*\(CINDERELLA PARTY\).*\(おまけ放送.*\)/\2！ \1 \3/" > omake_dl.sh
chmod +x omake_dl.sh
if [ -s omake_dl.sh ]; then
  ./omake_dl.sh
  expr ${KAI} + 1 > resent
fi

