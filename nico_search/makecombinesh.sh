#!/usr/bin/env bash
cd /data/share/temp/voiceactor_nico_ch
cat /dev/null > combine.sh
for d in temp/${1}/*
do
/data/share/temp/voiceactor_nico_ch/bilibili_rename.sh "${d}" >> combine.sh
done
cat combine.sh
