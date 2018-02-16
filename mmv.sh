#!/usr/bin/env zsh
# ���惊�l�[���p�V�F��
# usage: ./rename.sh �^����t�@�C���Q ���l�[���p���X�g
# ���l�[���p���X�g�ɂ̓��l�[�����ƃt�@�C���̌��������Ɛ����ȍ�i����
# tab�Ōq���ċL�q���邱��
LIST=/data/share/movie/checklist.txt
cnt=0
while read DUMMY DUMMY2 LINE
do
  if [ ${cnt} != 0 ]; then
    NAME="${LINE#*\|}"
    nn=`echo $1 | sed -e "s/\(${NAME}\).*\.mp4/\1/"`
    if [ "$nn" != "$1" ]; then
      echo "# move $1"
      mv -v "$1" /data/share/movie/*"${NAME}"/.
      break
    fi
  fi
  (( cnt++ ))
done < ${LIST}
