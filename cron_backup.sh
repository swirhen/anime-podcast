#!/usr/bin/env bash
cd /data/share/movie/sh
crontab -l > crontab.backup

git commit -m 'crontab backup' crontab.backup
git pull
git push origin master
