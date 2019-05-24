# /bin/sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LOGFILE="${SCRIPT_DIR}/logs/daily_backup.log"
echo "# DAILY BACKUP START: `date`" > "${LOGFILE}"
rsync -auv --delete /data8/temp8/ /data7/backup/temp8/ >> "${LOGFILE}"
rsync -auv --delete --exclude '.DAV' /data/share/book/ /data7/backup/book/ >> "${LOGFILE}"
rsync -auv --delete --exclude '.DAV' --exclude='v20*' /data/share/temp/ /data7/backup/temp/ >> "${LOGFILE}"
rsync -auv --delete --exclude '.DAV' /data8/movie8/ /data3/backup/ >> "${LOGFILE}"
echo "# DAILY BACKUP END: `date`" >> "${LOGFILE}"
