cd "/data/share/temp/voiceactor_nico_ch/01 CINDERELLA PARTY！"
KAI=$1
../crawlnicoch.sh "http://ch.nicovideo.jp/cinderellaparty/video" | grep ${KAI}回 | grep アーカイブ動画 | sed "s/\(第${KAI}回\).*\(CINDERELLA PARTY\).*アーカイブ動画\(.*\)/\2！ \1 \3/"
../crawlnicoch.sh "http://ch.nicovideo.jp/cinderellaparty/video" | grep ${KAI}回 | grep おまけ | sed "s/\(第${KAI}回\).*\(CINDERELLA PARTY\).*\(おまけ放送.*\)/\2！ \1 \3/"
