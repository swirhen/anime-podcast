#!/usr/bin/env zsh
# ����G���R�[�h�p�V�F��
# ���s�����f�B���N�g���ɑ��݂���V���[�Y�n����(*�b*.mp4��)
# �����ׂăG���R�[�h���A�t�B�[�h���X�V�ATwitter�ɍ��m����
# usage 169f.sh [priority file]
# �����t�@�C���ăG���R�p�Վ��V�F��
PYTHON_PATH="python3"
source /home/swirhen/.zshrc
cd /data/share/movie/95\ recover
(
IFS=$'\n';
for a in `ls -t *�b*.(avi|mp4|mkv|wmv)`
do
  if [ -f "$a" ]; then
    error=0
    until [ -f "/data/share/movie/98 PSP�p/$a.mp4" ];
    do
      error=`expr $error + 1`
      if [ $error -gt 10 ]; then
        break;
      fi
      /data/share/movie/sh/169mp44.sh "$a" "/data/share/movie/98 PSP�p/"
    done
    time=`stat "${a}" | grep Modify | awk '{ print $2,$3 }'`
    touch -t "${time:0:4}${time:5:2}${time:8:2}${time:11:2}${time:14:2}.${time:17:2}" "/data/share/movie/98 PSP�p/${a}.mp4"
    /data/share/movie/sh/mmv.sh "$a"
    /data/share/movie/sh/mmpc.sh
  fi
done
)
