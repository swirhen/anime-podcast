#!/usr/bin/env zsh
source /home/swirhen/.zshrc

nowdir=`pwd`
DATETIME=`date "+%Y%m%d%H%M"`

mkdir /data/tmp/${DATETIME}
cd /data/tmp/${DATETIME}
python /data/share/movie/sh/youtube-dl "$1"
if [ `ls *.f*.webm | wc -l` -gt 0 ]; then
  if [ `ls *.f*.webm | wc -l` -eq 2 ]; then
    name=`ls *.f*.webm | head -1`
    name2=`ls *.f*.webm | tail -1`
    ffm3 -i "${name}" -i "${name2}" -vcodec copy -acodec copy ${nowdir}/"${name}".mkv
  else
    name=`ls *.*.mp4`
    ffm3 -i *.*.mp4 -i *.*.webm -vcodec copy -acodec copy ${nowdir}/"${name}".mkv
  fi
else
  if [ `ls *.f*.m4a | wc -l` -eq 1 ]; then
    name=`ls *.*.mp4`
    ffm3 -i *.*.mp4 -i *.*.m4a -vcodec copy -acodec copy ${nowdir}/"${name}"
  else
    mv *.*.mp4 ${nowdir}
  fi
fi
cd ${nowdir}
rm -rf /data/tmp/${DATETIME}