#!/bin/bash
# ���惊�l�[���p�V�F��
# ���l�[���p���X�g�ɂ̓��l�[�����t�@�C���̌��������Ɛ����ȍ�i����
# tab�Ōq���ċL�q���邱��
# ��1����(�ȗ���)�̓��l�[�����t�@�C���̘b�������̑O�̕�������͂���B�f�t�H���g�͔��p�X�y�[�X�B
# ��2����(�ȗ���)�̓��l�[�����t�@�C���̘b�������̌�̕�������͂���B�f�t�H���g�͔��p�X�y�[�X�������́A��1�������w�肳��Ă���ꍇ�͑�1�����B
SFX1=" "
SFX2=" "
if [ $# -eq 1 ]; then  # ������1��
SFX1=$1
SFX2=$1
fi
if [ $# -eq 2 ]; then  # ������2��
SFX1=$1
SFX2=$2
fi
LIST=/data/share/movie/checklist.txt
NAME_LST1=()
FILE_LST=()
while read DUMMY DUMMY2 LINE
do
  if [ "${LINE}" != "" ]; then
    NAME_LST1+=( "${LINE}" )
  fi
done < ${LIST}
while read -r FILENAME
do
  FILE_LST+=( "${FILENAME:2}" )
done < <(find . -maxdepth 1 -type f \( -name \*.mp4 -o -name \*.wmv -o -name \*.mkv -o -name *.avi \))

for FILE_NAME in "${FILE_LST[@]}"
do
  for LINE in "${NAME_LST1[@]}"
  do
    SF="${LINE%%\|*}"
    NAME="${LINE#*\|}"
    ext=`echo $FILE_NAME | sed "s/.*\.\(.*\)/\1/"`

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9]\?$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} ��$nn�b.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          mv "$FILE_NAME" "${NAME} ��$nn�b.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          echo "# �ύX��̃t�@�C����������"
        fi
      else
        echo "# $FILE_NAME ���璆�I"
      fi
      break
    fi

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-1][0-9][0-9]\?\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-1][0-9][0-9]\?$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} ��$nn�b.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          mv "$FILE_NAME" "${NAME} ��$nn�b.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          echo "# �ύX��̃t�@�C����������"
        fi
      else
        echo "# $FILE_NAME ���璆�I"
      fi
      break
    fi

    nn=`echo $FILE_NAME | sed -e "s/.*${SF}.*$SFX1\([0-9][0-9].5\)$SFX2.*/\1/"`
    fsf=`echo $FILE_NAME | sed -e "s/.*\(${SF}\).*$SFX1[0-9][0-9].5$SFX2.*/\1/"`
    if [ "$fsf" == "$SF" ]; then
      if [ ! -e "$FILE_NAME".aria2 ]; then
        if [ "$FILE_NAME" != "${NAME} ��$nn�b.$ext" ]; then
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          mv "$FILE_NAME" "${NAME} ��$nn�b.$ext"
        else
          echo "# rename $FILE_NAME -> ${NAME} ��$nn�b.$ext"
          echo "# �ύX��̃t�@�C����������"
        fi
      else
        echo "# $FILE_NAME ���璆�I"
      fi
      break
    fi
  done
done
