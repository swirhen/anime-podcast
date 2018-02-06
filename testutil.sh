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
    read -p " (Y/N)?" YESNO
    case "${YESNO}" in
        y | Y ) return 1;;
        n | N ) return 0;;
        * ) echo "prease input Y or N(y or n)."
        yesno
    esac
}

plzenter() {
    read -p "hit enter key."
}

echo "start,"
yesno
YNANSWER="$?"

echo "YNANSWER: ${YNANSWER}"

plzenter

echo "end."