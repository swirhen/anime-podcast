# /bin/sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
LOGFILE="${SCRIPT_DIR}/logs/data_backup.log"
echo "# DAILY BACKUP2 START: `date`" > "${LOGFILE}"
rsync -auv --delete --exclude 'lost+found' /data/ /data9/ >> "${LOGFILE}"
echo "# DAILY BACKUP2 END: `date`" >> "${LOGFILE}"
