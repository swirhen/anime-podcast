#!/bin/bash
BASE_DIR="/data/share/movie"
PSPMP4_98_DIR="${BASE_DIR}/98 PSP用"
PSPMP4_MV_DIR="/data2/movie2/pspmp4"
ROOT_MV_DIR="/data2/movie2"
ROOT_MV_DIR_LINK="/data/share/movie/0004 過去連載終了分"
END_LIST_FILE=""
END_FILES=()
IFS_ORIGINAL="$IFS"
YEAR=""
QUARTER=""
TARGET=""
PRG=""
CHECK=""

# 移動
move_98() {
  clear
  # 容量チェック
  i=0
  SIZE=0
  for P in ${END_FILES[@]}
  do  
    if [ "${P:0:1}" = "#" ]; then
      continue
    fi
    PSIZE=`du -kc "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 | awk '{last = $0} END {print last}'  |awk '{print $1}'`
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

  # 移動先ディレクトリ、シンボリックリンク作成
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
      # 抜けチェック
      FILECOUNT=`ls -l "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 | grep -v "\\.5話" | wc -l`
      LASTEPSODE_COUNT=`ls -l "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 | awk '{last = $0} END {print last}' | sed -e 's/.*第\(.*\)話.*/\1/'`
      if [ ${FILECOUNT} -ne ${LASTEPSODE_COUNT} ]; then
        echo `ls -l "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4`
        echo "最終話と見られるファイル :"`ls "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 | awk '{last = $0} END {print last}'`
        echo "ファイル個数 :${FILECOUNT} 一致しません。"
        echo "move sure?"
        confirm
        if [ ! $? = 0 ]; then
          echo "スキップします"
          continue
        fi  
      else
         echo "${P} 抜けチェック：OK"
      fi
    fi

    # 移動
    if [ "${PRG}" = "3" ] ; then
      echo "移動処理無し"
    elif [ "`ls -l "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"*"${P} 第"*.mp4`" = "" ]; then
      mv -v "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"
      ln -s "${PSPMP4_MV_DIR}/${QUARTER}Q-${YEAR}/"*"${P} 第"*.mp4 "${PSPMP4_98_DIR}/"
      echo "${P}: 移動完了"
    else
      echo "既に存在しているため、移動無し"
    fi
    let i++
  done

  echo "ALL: 移動完了"
  quit
}

# シンボリックリンク削除
remove_98() {
  clear
  i=0
  for P in ${END_FILES[@]}
  do
    # ファイルチェック
    if [ ! `find "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 -type f` = "" ]; then
      echo `ls -l "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4`
      echo "find not symbolik link. remove sure?"
      confirm
      if [ ! $? = 0 ]; then
        echo "スキップします"
        continue
      fi
    else
      echo "${P} ファイルチェック: OK"
    fi

    # 削除
    size=`du -cb "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4 | tail -1 | awk '{print $1}'`
    if [ ${size} -eq 0 ]; then
        rm -v "${PSPMP4_98_DIR}/"*"${P} 第"*.mp4
        echo "${P} シンボリックリンク削除: OK"
    else
        echo "${P} 合計サイズが0でないのでシンボリックリンクではない: 削除しません"
    fi

    let i++
  done
  quit
}

# 移動(ルート)
move_root() {
  clear
  # 容量チェック
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

  # 移動先ディレクトリ作成
  FIND_ROOT_MV_DIR=`ls -d "${ROOT_MV_DIR}/"*"${YEAR}-Q${QUARTER}終了分"`
  if [ "${FIND_ROOT_MV_DIR}" = "" ]; then
    LASTNUM=`ls -lr "${ROOT_MV_DIR}/"0[0-9][0-9]* | head -1 | sed -e 's/.*\(0[0-9][0-9]\)\ .*/\1/'`
    LASTNUM=`expr ${LASTNUM} + 1`
    LASTNUM=`printf '%03d' ${LASTNUM}`
    ROOT_MK_DIR="${ROOT_MV_DIR}/${LASTNUM} ${YEAR}-Q${QUARTER}終了分"
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
    echo "${P}: 移動完了"
  done
  ln -s "${ROOT_MK_DIR}" "${ROOT_MV_DIR_LINK}/"

  echo "ALL: 移動完了"

  # 再採番
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

# y/n入力待ち状態
confirm() {
  echo -n "> "
  while read CONFIRM; do
    case "${CONFIRM}" in
      "y" | "Y" ) return 0;;
      "n" | "N" | "" ) return 1;;
      * )
      echo "y/nを入力してください。(EnterのみはNo)"
      echo -n "> ";;
    esac
  done
}

# 入力待ち状態
wait_enter() {
  echo "(Enterで続行します)"
  echo -n "> "
  while read CONFIRM; do
    case "${CONFIRM}" in
      * ) break;;
    esac
  done
}

# 終了
quit() {
  # あとしまつ
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

# 終了リストファイルの存在
END_LIST_FILE="${BASE_DIR}/end_${YEAR}Q${QUARTER}.txt"
if [ ! -s "${END_LIST_FILE}" ]; then
  echo "${END_LIST_FILE} is not found."
  quit
fi

# 終了リストファイル読み込み
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
