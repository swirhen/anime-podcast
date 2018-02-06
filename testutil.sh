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

# yes/no
yesno() {
    echo -n " (Y/N)"
    while read YESNO
    do
        case "${YESNO}" in
            y | Y ) echo "y";;
            n | N ) echo "n";;
            * ) echo "prease imput Y or N(y or n)."
            yesno
        esac
    done
}

echo "start,"
YNANSWER=`yesno`
YNANSWER="$?"

echo "YNANSWER: ${YNANSWER}"
