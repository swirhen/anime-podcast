# /bin/sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LOGFILE="${SCRIPT_DIR}/logs/daily_backup.log"
echo "# DAILY BACKUP START: `date`" > "${LOGFILE}"
# book(本) 
#rsync -auv --delete --exclude '.DAV' /data/share/book/ /data7/backup/book/ >> "${LOGFILE}"
# sqlite DB file
cp -p /data/share/movie/sh/nyaa_movie_feed.db /home/swirhen/Dropbox/sqlite_db_backup/
#cp -p /data/share/movie/sh/python-lib/swirhentv_feed.db /home/swirhen/Dropbox/sqlite_db_backup/

echo "# DAILY BACKUP END: `date`" >> "${LOGFILE}"
