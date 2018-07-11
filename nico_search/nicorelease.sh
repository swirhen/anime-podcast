#!/usr/bin/env bash
rm -f /data/share/movie/98\ PSP用/nico/*.mp4
rm -f /data/share/movie/98\ PSP用/nico_imas/*.mp4
ln -s /data/share/movie/sh/nico_search/0[^1389]*/*.mp4 /data/share/movie/98\ PSP用/nico/.
ln -s /data/share/movie/sh/nico_search/{01,03,08,09}*/*.mp4 /data/share/movie/98\ PSP用/nico_imas/.
/data/share/movie/sh/mmmpc.sh nico "ニコニコチャンネルの声優さん動画"
/data/share/movie/sh/mmmpc.sh nico_imas "ニコニコチャンネルの声優さん動画(アイマス公式系)"
