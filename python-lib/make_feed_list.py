# -*- coding: utf-8 -*-
# make feed list
import pathlib
import re
import swirhentv_util as swiutil

current_dir = pathlib.Path(__file__).resolve().parent
SCRIPT_DIR = str(current_dir)
FILENAME = f'{SCRIPT_DIR}/../../98 PSP用/swirhentv_feed_list.txt'


if __name__ == "__main__":
    result = swiutil.get_feed_xml_list()
    result_str = ''
    for item in result:
        if not re.search('ラジオ', item[1]):
            result_str += f'{item[0]}: {item[1]}\n'
    swiutil.writefile_new(FILENAME, result_str)