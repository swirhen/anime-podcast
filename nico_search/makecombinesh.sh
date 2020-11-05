#!/usr/bin/env bash
if [ $# = 0 ]; then
	echo "usage $0 [/data/share/temp/voiceactor_nico_ch/temp on date dir]"
	exit 1
fi
cd /data/share/temp/voiceactor_nico_ch
cat /dev/null > combine.sh
for d in temp/${1}/*
do
/data/share/temp/voiceactor_nico_ch/bilibili_rename.sh "${d}" >> combine.sh
done
relfilg=`grep '*/$' combine.sh`
if [ "${relfilg}" != "" ]; then
    echo "/data/share/movie/sh/nico_search/nicorelease.sh" >> combine.sh
fi
cat combine.sh
