#!/usr/bin/env zsh
# @author swirhen
# usage:mkvremarge.sh [mkv file]
source /home/swirhen/.zshrc
NAME=`echo $1 | cut -d"." -f1`
FPS="23.97605"
R="24000/1001"
MP4Box -raw 1 "$1"
MP4Box -raw 2 "$1"
MP4Box -fps $FPS -add "$NAME"_track1.h264 -add "$NAME"_track2.aac -new "$2""$1.mp4"
rm "$NAME"_track1.h264
rm "$NAME"_track2.aac
