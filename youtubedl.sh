#!/usr/bin/env zsh
source /home/swirhen/.zshrc

nowdir=`pwd`
DATETIME=`date "+%Y%m%d%H%M"`

mkdir /data/tmp/${DATETIME}
cd /data/tmp/${DATETIME}
youtube-dl "$1"
if [ `ls *.webm | wc -l` -gt 0 ]; then
  if [ `ls *.webm | wc -l` -eq 2 ]; then
    name=`ls *.webm | head -1`
    name2=`ls *.webm | tail -1`
    ffm3 -i "${name}" -i "${name2}" -vcodec copy -acodec copy ${nowdir}/"${name%-*}".mkv
  elif [ `ls *.webm | wc -l` -eq 1 ]; then
    name=`ls *.webm`
    mv ${name} ${nowdir}/${name%-*}.webm
  else
    name=`ls *.*.mp4`
    ffm3 -i *.*.mp4 -i *.*.webm -vcodec copy -acodec copy ${nowdir}/"${name%-*}".mkv
  fi
else
  name=`ls *.mp4`
  if [ `ls *.f*.m4a | wc -l` -eq 1 ]; then
    ffm3 -i *.*.mp4 -i *.*.m4a -vcodec copy -acodec copy ${nowdir}/"${name%-*}".mp4
  else
    mv ${name} ${nowdir}/${name%-*}.mp4
  fi
fi
cd ${nowdir}
rm -rf /data/tmp/${DATETIME}
