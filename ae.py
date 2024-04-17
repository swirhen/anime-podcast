#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import os
import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(f'{str(current_dir)}/python-lib/')
import swirhentv_util as swiutil


# main section
if __name__ == '__main__':
    in_path = '/data/share/movie'
    out_path = '/data/share/movie/98 PSP用'
    args = sys.argv
    swiutil.encode_movie_in_directory(in_path, out_path)
    swiutil.move_movie(in_path)
