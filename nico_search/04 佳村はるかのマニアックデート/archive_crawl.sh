cd "/data/share/temp/voiceactor_nico_ch/04"*
KAI=`cat resent`
ZENKAI=`echo ${KAI} | sed "y/0123456789/０１２３４５６７８９/"`
../crawlnicoch.sh "http://ch.nicovideo.jp/search/%E4%BD%B3%E6%9D%91%E3%81%AF%E3%82%8B%E3%81%8B%E3%81%AE%E3%83%9E%E3%83%8B%E3%82%A2%E3%83%83%E3%82%AF%E3%83%87%E3%83%BC%E3%83%88%20-%E3%83%80%E3%82%A4%E3%82%B8%E3%82%A7%E3%82%B9%E3%83%88?channel_id=ch2567656&mode=s&sort=f&order=d&type=video" | grep ＃${ZENKAI} | sed "s/\"\(.*\)\" \".*＃${ZENKAI}　\(.*\)/\"\1\" \"佳村はるかのマニアックデート #${KAI} \2/" > archive_dl.sh

if [ ! -s archive_dl.sh ]; then
  ZENKAI=${KAI}
  ../crawlnicoch.sh "http://ch.nicovideo.jp/search/%E4%BD%B3%E6%9D%91%E3%81%AF%E3%82%8B%E3%81%8B%E3%81%AE%E3%83%9E%E3%83%8B%E3%82%A2%E3%83%83%E3%82%AF%E3%83%87%E3%83%BC%E3%83%88%20-%E3%83%80%E3%82%A4%E3%82%B8%E3%82%A7%E3%82%B9%E3%83%88?channel_id=ch2567656&mode=s&sort=f&order=d&type=video" | grep ＃${ZENKAI} | sed "s/\"\(.*\)\" \".*＃${ZENKAI}　\(.*\)/\"\1\" \"佳村はるかのマニアックデート #${KAI} \2/" > archive_dl.sh
fi

if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  #./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
