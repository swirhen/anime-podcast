cd "/data/share/temp/voiceactor_nico_ch/05"*
KAI=`cat resent`
ZENKAI=`echo ${KAI} | sed "y/0123456789/０１２３４５６７８９/"`
../crawlnicoch.sh "http://ch.nicovideo.jp/search/%E5%A4%A7%E4%B9%85%E4%BF%9D%E7%91%A0%E7%BE%8E%E3%81%AE%E3%82%8B%E3%81%BF%E3%82%8B%E3%81%BF%E3%82%8B%EF%BD%9E%E3%82%80%20-%E3%83%80%E3%82%A4%E3%82%B8%E3%82%A7%E3%82%B9%E3%83%88?channel_id=ch2567656&mode=s&sort=f&order=d&type=video" | grep ＃${ZENKAI} | sed "s/\"\(.*\)\" \".*＃${ZENKAI}　\(.*\)/\"\1\" \"大久保瑠美のるみるみる～む #${KAI} \2/" > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
