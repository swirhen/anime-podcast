#!/usr/bin/env zsh
rm -f /data/share/movie/98\ PSP用/nico/*.mp4
rm -f /data/share/movie/98\ PSP用/nico_imas/*.mp4
ln -s /data8/movie8/nico_search/0[^1389]*/*.mp4 /data/share/movie/98\ PSP用/nico/.
ln -s /data8/movie8/nico_search/1[0-9]*/*.mp4 /data/share/movie/98\ PSP用/nico/.
ln -s /data8/movie8/nico_search/2[1-3]*/*.mp4 /data/share/movie/98\ PSP用/nico/.
ln -s /data8/movie8/nico_search/99*/*.mp4 /data/share/movie/98\ PSP用/nico/.
ln -s /data8/movie8/nico_search/{01,03,08,09,98}*/*.mp4 /data/share/movie/98\ PSP用/nico_imas/.
ln -s /data8/movie8/nico_search/20*/mp4/*.mp4 /data/share/movie/98\ PSP用/nico_imas/.
python3 /data/share/movie/sh/mmmpc.py nico "声優バラエティ動画"
python3 /data/share/movie/sh/mmmpc.py nico_imas "声優バラエティ動画(アイマス公式系)"
find /data/share/movie/98\ PSP用/agqr/ -type l -exec rm {} \;
ln -s /data8/movie8/nico_search/(0[^1389]|[1-9][0-9])*/*.m4a /data/share/movie/98\ PSP用/agqr/
ln -s /data8/movie8/nico_search/20*/*.mp4 /data/share/movie/98\ PSP用/agqr/
/data/share/movie/sh/agqrrelease.sh
