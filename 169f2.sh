#!/usr/bin/env zsh
# ����G���R�[�h�p�V�F��
PYTHON_PATH="python3"
source /home/swirhen/.zshrc
if [ -f "$1" ]; then
  /data/share/movie/sh/169mp44.sh "$1" "/data/share/movie/98 PSP�p/"
  /data/share/movie/sh/mmpc.sh
  /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "�ypublish�z$1.mp4"
  ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "�ypublish�z$1.mp4"
fi
