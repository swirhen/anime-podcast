# /bin/sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LOGFILE="${SCRIPT_DIR}/logs/daily_backup.log"
echo "# DAILY BACKUP START: `date`" > "${LOGFILE}"
# temp8(アイマス系音楽&動画)
rsync -auv --delete /data8/temp8/ /data7/backup/temp8/ >> "${LOGFILE}"
# book(本) 
rsync -auv --delete --exclude '.DAV' /data/share/book/ /data7/backup/book/ >> "${LOGFILE}"
# nico_search(ニコニコ保存系)
rsync -auv --delete --exclude '.DAV' /data8/movie8/nico_search/ /data3/backup/nico_search/ >> "${LOGFILE}"
echo "# DAILY BACKUP END: `date`" >> "${LOGFILE}"
