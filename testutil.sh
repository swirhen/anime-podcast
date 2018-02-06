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
            y | Y ) return 1;;
            n | N ) return 0;;
            * ) echo "prease imput Y or N(y or n)."
            yesno
        esac
    done
}

echo "start,"
yesno
YNANSWER="$?"

echo "YNANSWER: ${YNANSWER}"
