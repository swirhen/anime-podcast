cd "/data/share/temp/voiceactor_nico_ch/02"*
KAI=`cat resent`
ZENKAI=`echo ${KAI} | sed "y/0123456789/０１２３４５６７８９/"`
../crawlnicoch.sh "http://ch.nicovideo.jp/search/%E3%81%BE%E3%81%A4%E3%81%84%E3%81%8C%E3%83%97%E3%83%AD%E3%83%87%E3%83%A5%E3%83%BC%E3%82%B9%20-%E3%83%80%E3%82%A4%E3%82%B8%E3%82%A7%E3%82%B9%E3%83%88?channel_id=ch2567656&mode=s&sort=f&order=d&type=video" | grep "＃${KAI}" | sed "s/\"\(.*\)\" \".*＃${KAI}\(.*\)/\"\1\" \"まついがプロデュース#${KAI}\2/"  | sed "s/  / /" > archive_dl.sh
if [ -s archive_dl.sh ]; then
  chmod +x archive_dl.sh
  ./archive_dl.sh
  expr ${KAI} + 1 > resent
fi
