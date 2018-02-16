#!/usr/bin/env zsh
# ����G���R�[�h�p�V�F��
# ���s�����f�B���N�g���ɑ��݂���V���[�Y�n����(*�b*.mp4��)
# �����ׂăG���R�[�h���A�t�B�[�h���X�V�ATwitter�ɍ��m����
# usage 169f.sh [priority file]
PYTHON_PATH="python3"
source /home/swirhen/.zshrc
cd /data/share/movie
(
IFS=$'\n';
for a in `ls -rt *�b*.(avi|mp4|mkv|wmv)`
do
  if [ -f "$a" ]; then
    error=0
    until [ -f "/data/share/movie/98 PSP�p/$a.webm" ];
    do
      error=`expr $error + 1`
      if [ $error -gt 10 ]; then
        break;
      fi
      /data/share/movie/sh/169mp45.sh "$a" "/data/share/movie/98 PSP�p/"
    done
    /data/share/movie/sh/mmpc.sh
    #/data/share/movie/sh/mmpc3.sh
    /data/share/movie/sh/mmv.sh "$a"
    sleep 3
    /home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "�ypublish�z$a.webm"
    ${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "�ypublish�z$a.webm"
  fi
done
)
