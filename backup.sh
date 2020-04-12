# /bin/sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LOGFILE="${SCRIPT_DIR}/logs/daily_backup.log"
echo "# DAILY BACKUP START: `date`" > "${LOGFILE}"
# temp8($B%"%$%^%97O2;3Z(B&$BF02h(B)
rsync -auv --delete /data8/temp8/ /data7/backup/temp8/ >> "${LOGFILE}"
# book($BK\(B) 
rsync -auv --delete --exclude '.DAV' /data/share/book/ /data7/backup/book/ >> "${LOGFILE}"
# nico_search($B%K%3%K%3J]B87O(B)
rsync -auv --delete --exclude '.DAV' /data8/movie8/nico_search/ /data3/backup/nico_search/ >> "${LOGFILE}"
echo "# DAILY BACKUP END: `date`" >> "${LOGFILE}"
