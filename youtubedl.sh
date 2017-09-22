source /home/swirhen/.zshrc

nowdir=`pwd`
DATETIME=`date "+%Y%m%d%H%M"`

mkdir /data/tmp/${DATETIME}
cd /data/tmp/${DATETIME}
python /data/share/movie/sh/youtube-dl "$1"
if [ -f *.f*.webm ]; then
  name=`ls *.*.mp4`
  ffm3 -i *.*.mp4 -i *.*.webm -vcodec copy -acodec aac ${nowdir}/${name}"
else
  mv *.*.mp4 ${nowdir}
fi
