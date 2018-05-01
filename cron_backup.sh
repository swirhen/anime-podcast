#!/usr/bin/env bash
cd /data/share/movie/sh
crontab -l > ~/Dropbox/dotfile/crontab.hmx-31seto-rev
crontab -l > crontab.backup

git commit -m 'crontab backup' crontab.backup
git pull
git push origin master
