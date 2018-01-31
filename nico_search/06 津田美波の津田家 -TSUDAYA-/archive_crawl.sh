cd "/data/share/temp/voiceactor_nico_ch/06"*
KAI=`cat resent`
ZENKAI=`echo ${KAI} | sed "y/0123456789/０１２３４５６７８９/"`
../crawlnicoch.sh "http://ch.nicovideo.jp/search/%E6%B4%A5%E7%94%B0%E5%AE%B6%20-%E3%83%80%E3%82%A4%E3%82%B8%E3%82%A7%E3%82%B9%E3%83%88?channel_id=ch2567656&mode=s&sort=f&order=d&type=video" | grep ＃${ZENKAI} | sed "s/\"\(.*\)\" \".*＃${ZENKAI}　\(.*\)/\"\1\" \"津田美波の津田家 -TSUDAYA-#${KAI} \2/" > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
