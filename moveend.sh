#!/bin/bash
BASE_DIR="/data/share/movie"
PSPMP4_98_DIR="${BASE_DIR}/98 PSP�p"
PSPMP4_MV_DIR="/data2/movie2/pspmp4"
ROOT_MV_DIR="/data2/movie2"
ROOT_MV_DIR_LINK="/data/share/movie/0004 �ߋ��A�ڏI����"
END_LIST_FILE=""
END_FILES=()
IFS_ORIGINAL="$IFS"
YEAR=""
QUARTER=""
TARGET=""
PRG=""
CHECK=""

# �ړ�
move_98() {
  clear
  # �e�ʃ`�F�b�N
  i=0
  SIZE=0
  for P in ${END_FILES[@]}
  do  
    if [ "${P:0:1}" = "#" ]; then
      continue
    fi
    PSIZE=`du -kc "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 | awk '{last = $0} END {print last}'  |awk '{print $1}'`
    echo "${P} : ${PSIZE} KB"
    SIZE=`expr ${SIZE} +  ${PSIZE}`
    let i++ 
  done
  echo "Total: ${SIZE} KB"
  PSPMP4_MV_DIR_AVSIZE=`df -k "${PSPMP4_MV_DIR}" | awk '{if(NR > 1) print $4}'`
  echo "${PSPMP4_MV_DIR} available: ${PSPMP4_MV_DIR_AVSIZE} KB"

  if [ ${PSPMP4_MV_DIR_AVSIZE} -gt ${SIZE} ]; then
    echo "Disk Space Check :OK"
  else
    echo "Disk Space Check :NG ${PSPMP4_MV_DIR} has no space."
    quit
  fi  
  wait_enter

  # �ړ���f�B���N�g���A�V���{���b�N�����N�쐬
  if [ ! -d "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}" ]; then
    mkdir "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}"
  fi  
  if [ ! -L "${PSPMP4_98_DIR}/${QUARTER}Q-${YEAR}" ]; then
    ln -s "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}" "${PSPMP4_98_DIR}/"
  fi  

  i=0 
  for P in ${END_FILES[@]}
  do  
    if [ "${P:0:1}" = "#" ]; then
      continue
    fi  

    if [ "${CHECK}" = "1" ]; then
      # �����`�F�b�N
      FILECOUNT=`ls -l "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 | grep -v "\\.5�b" | wc -l`
      LASTEPSODE_COUNT=`ls -l "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 | awk '{last = $0} END {print last}' | sed -e 's/.*��\(.*\)�b.*/\1/'`
      if [ ${FILECOUNT} -ne ${LASTEPSODE_COUNT} ]; then
        echo `ls -l "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4`
        echo "�ŏI�b�ƌ�����t�@�C�� :"`ls "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 | awk '{last = $0} END {print last}'`
        echo "�t�@�C���� :${FILECOUNT} ��v���܂���B"
        echo "move sure?"
        confirm
        if [ ! $? = 0 ]; then
          echo "�X�L�b�v���܂�"
          continue
        fi  
      else
         echo "${P} �����`�F�b�N�FOK"
      fi
    fi

    # �ړ�
    if [ "${PRG}" = "3" ] ; then
      echo "�ړ���������"
    elif [ "`ls -l "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"*"${P} ��"*.mp4`" = "" ]; then
      mv -v "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"
      ln -s "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"*"${P} ��"*.mp4 "${PSPMP4_98_DIR}/"
      echo "${P}: �ړ�����"
    else
      echo "���ɑ��݂��Ă��邽�߁A�ړ�����"
    fi
    let i++
  done

  echo "ALL: �ړ�����"
  quit
}

# �V���{���b�N�����N�폜
remove_98() {
  clear
  i=0
  for P in ${END_FILES[@]}
  do
    # �t�@�C���`�F�b�N
    if [ ! `find "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4 -type f` = "" ]; then
      echo `ls -l "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4`
      echo "find not symbolik link. remove sure?"
      confirm
      if [ ! $? = 0 ]; then
        echo "�X�L�b�v���܂�"
        continue
      fi
    else
      echo "${P} �t�@�C���`�F�b�N: OK"
    fi

    # �폜
    rm -v "${PSPMP4_98_DIR}/"*"${P} ��"*.mp4
    echo "${P} �V���{���b�N�����N�폜: OK"

    let i++
  done
  quit
}

# �ړ�(���[�g)
move_root() {
  clear
  # �e�ʃ`�F�b�N
  i=0
  SIZE=0
  for P in ${END_FILES[@]}
  do
    PSIZE=`du -kc "${BASE_DIR}/"*"${P}/" | awk '{last = $0} END {print last}' | awk '{print $1}'`
    echo "${P} : ${PSIZE} KB"
    SIZE=`expr ${SIZE} +  ${PSIZE}`
    let i++
  done
  echo "Total: ${SIZE} KB"
  ROOT_MV_DIR_AVSIZE=`df -k "${ROOT_MV_DIR}" | awk '{if(NR > 1) print $4}'`
  echo "${ROOT_MV_DIR} available: ${ROOT_MV_DIR_AVSIZE} KB"

  if [ ${ROOT_MV_DIR_AVSIZE} -gt ${SIZE} ]; then
    echo "Disk Space Check :OK"
  else
    echo "Disk Space Check :NG ${ROOT_MV_DIR} has no space."
    quit
  fi
  wait_enter

  # �ړ���f�B���N�g���쐬
  FIND_ROOT_MV_DIR=`ls -d "${ROOT_MV_DIR}/"*"${YEAR}-Q${QUARTER}�I����"`
  if [ "${FIND_ROOT_MV_DIR}" = "" ]; then
    LASTNUM=`ls -lr "${ROOT_MV_DIR}/"0[0-9][0-9]* | head -1 | sed -e 's/.*\(0[0-9][0-9]\)\ .*/\1/'`
    LASTNUM=`expr ${LASTNUM} + 1`
    LASTNUM=`printf '%03d' ${LASTNUM}`
    ROOT_MK_DIR="${ROOT_MV_DIR}/${LASTNUM} ${YEAR}-Q${QUARTER}�I����"
    mkdir "${ROOT_MK_DIR}"
  else
    ROOT_MK_DIR="${FIND_ROOT_MV_DIR}"
  fi

  i=0
  for P in ${END_FILES[@]}
  do
    if [ "${P:0:1}" = "#" ]; then
      continue
    fi
    mv -v "${BASE_DIR}/"*"${P}/" "${ROOT_MK_DIR}/"
    echo "${P}: �ړ�����"
  done
  ln -s "${ROOT_MK_DIR}" "${ROOT_MV_DIR_LINK}/"

  echo "ALL: �ړ�����"

  # �č̔�
  cd "${ROOT_MK_DIR}/"
  /data/share/movie/sh/mnu.sh

  quit
}

year() {
  echo "Year? (YYYY)"
  echo "q: quit"
  echo -n "> "
  while read YEAR; do
      if [[ "${YEAR}" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
        break
      elif [ "${YEAR}" = "q" ]; then
        quit
      else
        echo "Year is not valid."
        year
      fi
  done
}

quarter() {
  echo "Quarter? (1-4)"
  echo "q: quit"
  echo -n "> "
  while read QUARTER; do
      if [[ "${QUARTER}" =~ ^[1-4]$ ]]; then
        break
      elif [ "${QUARTER}" = "q" ]; then
        quit
      else
        echo "Quarter is not valid."
        quarter
      fi
  done
}

target() {
  echo "Target?"
  echo "1: root(${BASE_DIR}) 2:pspmp4(${PSPMP4_98_DIR})"
  echo "q: quit"
  echo -n "> "
  while read TARGET; do
    case "${TARGET}" in
      1 | 2 ) break;;
      q | Q ) quit;;
      * ) echo "Target is not valid."
      target
    esac
  done
}

prg() {
  echo "Progress?"
  echo "1: move end program 2: remove symbolic link 3: check only"
  echo "q: quit"
  echo -n "> "
  while read PRG; do
    case "${PRG}" in
      1 | 2 | 3 ) break;;
      q | Q ) quit;;
      * ) echo "Progress is not valid."
      target
    esac
  done
}

check() {
  echo "Check missing program?"
  echo "0: off 1: on"
  echo "q: quit"
  echo -n "> "
  while read CHECK; do
    case "${CHECK}" in
      0 | 1 ) break;;
      q | Q ) quit;;
      * ) echo "Check is not valid."
      check
    esac
  done
}

# y/n���͑҂����
confirm() {
  echo -n "> "
  while read CONFIRM; do
    case "${CONFIRM}" in
      "y" | "Y" ) return 0;;
      "n" | "N" | "" ) return 1;;
      * )
      echo "y/n����͂��Ă��������B(Enter�݂̂�No)"
      echo -n "> ";;
    esac
  done
}

# ���͑҂����
wait_enter() {
  echo "(Enter�ő��s���܂�)"
  echo -n "> "
  while read CONFIRM; do
    case "${CONFIRM}" in
      * ) break;;
    esac
  done
}

# �I��
quit() {
  # ���Ƃ��܂�
  IFS="$IFS_ORIGINAL"
  exit
}
# main
clear
if [ "$1" = "" ]; then
  year
else
  YEAR=$1
fi

if [ "$2" = "" ]; then
  quarter
else
  QUARTER=$2
fi

if [ "$3" = "" ]; then
  target
else
  TARGET=$3
fi

if [ "${TARGET}" = "2" ]; then
  prg
  if [ ! "${PRG}" = "2" ]; then
    check
  fi
fi

# �I�����X�g�t�@�C���̑���
END_LIST_FILE="${BASE_DIR}/end_${YEAR}Q${QUARTER}.txt"
if [ ! -s "${END_LIST_FILE}" ]; then
  echo "${END_LIST_FILE} is not found."
  quit
fi

# �I�����X�g�t�@�C���ǂݍ���
IFS="|"
while read P
do
  END_FILES+=("${P}")
done < "${END_LIST_FILE}"

if [ "${TARGET}" = "1" ]; then
  move_root
elif [ "${TARGET}" = "2" ]; then
  if [ "${PRG}" = "1" ]; then
    move_98
  elif [ "${PRG}" = "2" ]; then
    remove_98
  elif [ "${PRG}" = "3" ]; then
    move_98
  fi
fi
