#!/usr/bin/env zsh

curl "$1" | grep "http.*title.*$2" | sed "s#^.*<a href=#/data/share/movie/sh/nicodl.sh #" | sed "s/title=//"
