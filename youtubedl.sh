#!/usr/bin/env zsh
source /home/swirhen/.zshrc

nowdir=`pwd`
DATETIME=`date "+%Y%m%d%H%M"`

mkdir /data/tmp/${DATETIME}
cd /data/tmp/${DATETIME}
python /data/share/movie/sh/youtube-dl "$1"
if [ -f *.f*.webm ]; then
  if [ `ls *.f*.webm | wc -l` -eq 2 ]; then
    name=`ls *.f*.webm | head -1`
    name2=`ls *.f*.webm | tail -1`
    ffm3 -i "${name}" -i "${name2}" -vcodec copy -acodec aac ${nowdir}/"${name}".mp4
  else
    name=`ls *.*.mp4`
    ffm3 -i *.*.mp4 -i *.*.webm -vcodec copy -acodec aac ${nowdir}/"${name}"
  fi
else
  mv *.*.mp4 ${nowdir}
fi
cd ${nowdir}
#rm -rf /data/tmp/${DATETIME}