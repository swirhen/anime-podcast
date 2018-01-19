# /bin/sh
# 超A&G予約録画再エンコード用スクリプト
# require: ffmpeg
# usage: agqrrecord.sh [flvファイル名] [動画フラグ]
# 動画フラグ: vなら映像付き、それ以外なら音声と見なしてエンコする
vidflg=$2
# パスを除いたファイル名
efilename="$1"
# 保存フォルダへ移動
cd "/data/share/movie/98 PSP用/agqr/flv"
# 映像付きならばエンコード用のシェルを呼ぶ。音声のみならmp3エンコード
if [ $# -eq 2 ]; then
  echo "video"
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp4" ];
    do
      /data/share/movie/sh/169mp4_agqr.sh "$efilename" "/data/share/movie/98 PSP用/agqr/" $3
    done
else 
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp3" ];
    do
      /usr/bin/wine ffmpeg.exe -i "$efilename" -acodec libmp3lame -ab 64k -ac 2 -ar 24000 "/data/share/movie/98 PSP用/agqr/$efilename.mp3"
    done
fi

# rssフィード生成シェル
/data/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"
/data/share/movie/sh/mmmpc2.sh agqr "超！A&G(+α)"
