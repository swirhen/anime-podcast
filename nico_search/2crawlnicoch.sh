#!/usr/bin/env zsh

 curl "$1" | grep "<a title" | sed "s#.*<a title=\"\(.*\)\" href=\"\(.*\)\" data-href.*#/data/share/movie/sh/nicodl.sh \"http://www.nicovideo.jp\2\" \"\1\"#"
