#!/usr/bin/env bash
# 各種疎通テストユーティリティ
# 機能予定
# ping
# telnet
# ntpdate
# 各種多段sshから同様のテスト
# ログのテール
# ログのgrep
# tmux-xpanesが入っていればマルチペイン化

# グローバル関数
SELECTMENU=0

# yes/no
yesno() {
    read -p " (Y/N)? >" YESNO
    case "${YESNO}" in
        y | Y ) return 1;;
        n | N ) return 0;;
        * ) echo "prease input Y/N(y/n)."
        yesno
    esac
}

# hit enter key
plzenter() {
    read -p "hit enter key."
}

plzinput() {
    read -p "> " INPUT
    echo "${INPUT}"
}

# main menu.
main_menu() {
    SELECTMENU=`plzinput`
    case "${SELECTMENU}" in
        1 | 2 | 3 | 4 | 5 | 6 | 7 ) return ${SELECTMENU};;
        * ) echo "prease input 1-7."
        main_menu
    esac
}

# ping test
ping_test () {
    echo "under construction."
}

# telnet test
telnet_test () {
    echo "under construction."
}

# ntpdate test
ntpdate_test () {
    echo "under construction."
}

# tail log
tail_log () {
    echo "under construction."
}

# grep log
grep_log () {
    echo "under construction."
}

# ftp test
ftp_test() {
    echo "under construction."
}

# lftp test
lftp_test() {
    echo "under construction."
}

# main section
echo "テストユーティリティ:"
echo "ある程度のターミナル解像度で使用してください"

# リストファイル読み込み
# readlist

# main menu
echo "*** main menu ***"
echo "1: ping"
echo "2: telnet"
echo "3: ntpdate"
echo "4: ftp"
echo "5: lftp"
echo "6: tail log"
echo "7: grep log"
echo "please select operation."
main_menu

case "${SELECTMENU}" in
    1 ) ping_test;;
    2 ) telnet_test;;
    3 ) ntpdate_test;;
    4 ) ftp_test;;
    5 ) lftp_test;;
    6 ) tail_log;;
    7 ) grep_log;;
    # それ以外無いはず
esac

echo "end."