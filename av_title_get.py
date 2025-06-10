#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import section
import sys,re
sys.path.append(f'/home/swirhen/sh/checker/torrentsearch')
import torrentsearch as ts

# main section
if __name__ == '__main__':
    args = sys.argv
    keyword = args[1]
    
    result = ts.search_seed_ext('av', keyword)

    if len(result) == 0:
        print('No results found.')
    else:
        print(result[0][1])



