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
    read -p " (Y/N)? > " YESNO
    case "${YESNO}" in
        y | Y ) return 1;;
        n | N ) return 0;;
        * ) echo "prease input Y/N(y/n)."
        yesno
    esac
}

# yes/no 2
yesno2() {
    read -p "hit enter(Y)/N > " YESNO2
    case "${YESNO2}" in
        y | Y | "" ) return 1;;
        n | N ) return 0;;
        * ) echo "prease input enter or enter or Y/N(y/n)."
        yesno2
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

# main menu
main_menu(){
    echo "*** main menu ***"
    echo "1: ping"
    echo "2: telnet"
    echo "3: ntpdate"
    echo "4: ftp"
    echo "5: lftp"
    echo "6: tail log"
    echo "7: grep log"
    echo "please select operation."
    main_menu_i
}

# menu input
main_menu_i() {
    SELECTMENU=`plzinput`
    case "${SELECTMENU}" in
        1 ) ping_test;;
        2 ) telnet_test;;
        3 ) ntpdate_test;;
        4 ) ftp_test;;
        5 ) lftp_test;;
        6 ) tail_log;;
        7 ) grep_log;;
        * ) echo "prease input 1-7."
        main_menu_i
    esac
}

# plz continue
plzcontinue() {
    echo "continue test?"
    yesno2
    if [ "$?" -eq 1 ]; then
        main_menu
    else
        end
    fi
}

# end
end() {
    echo "end."
    exit 0
}

# ping test
ping_test () {
    echo "under construction."
    plzcontinue
}

# telnet test
telnet_test () {
    echo "under construction."
    plzcontinue
}

# ntpdate test
ntpdate_test () {
    echo "under construction."
    plzcontinue
}

# tail log
tail_log () {
    echo "under construction."
    plzcontinue
}

# grep log
grep_log () {
    echo "under construction."
    plzcontinue
}

# ftp test
ftp_test() {
    echo "under construction."
    plzcontinue
}

# lftp test
lftp_test() {
    echo "under construction."
    plzcontinue
}

# main section
echo "テストユーティリティ:"
echo "ある程度のターミナル解像度で使用してください"
echo ""

# リストファイル読み込み
# readlist

# main menu
main_menu