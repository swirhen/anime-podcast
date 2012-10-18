# /bin/sh
# 超A&G予約録画用スクリプト
# require: rtmpdump,ffmpeg,いろいろ
# usage: agqrrecord.sh [番組名] [開始オフセット] [録画時間] [動画フラグ] [隔週フラグファイル名]
# 番組名: YYYYMMDD_HHMM_番組名.flv というファイルになる
# 開始オフセット: sec
# 録画時間: sec
# 動画フラグ: vなら映像付き、それ以外なら音声と見なしてエンコする
# 隔週フラグファイル名: 
#     フラグファイルがあるかどうかチェックして、なければ作成だけして録画しない
#     あれば削除して録画する
name=$1
offset=$2
rectime=$3
vidflg=$4
recflg=$5
# オフセット
sleep $offset
# 隔週対応
if [ "${recflg:-null}" != null ]; then
flgfile="/data/share/movie/98 PSP用/agqr/flg/$recflg"
	if [ -f "$flgfile" ]; then
		rm "$flgfile"
	else
		touch "$flgfile"
		exit
	fi
fi
# 日付時刻
dt=`date +"%Y%m%d_%H%M"`
# 保存ファイル名
filename="/data/share/movie/98 PSP用/agqr/flv/""$dt"_"$name.flv"
# パスを除いたファイル名
efilename="$dt"_"$name.flv"
# つぶやく
/home/swirhen/Shellscriptter/Shellscriptter.sh -r "【超A&G自動保存開始】$efilename"
# 接続失敗対策、ファイルが生成されるまで処理を繰り返す
until [ -s "$filename" ]
do
	# ランダム変数(サーバ分散対応)
	num=`expr $RANDOM % 2 + 1`
#	num2=`expr $RANDOM % 2 + 1`
	num3=`expr $RANDOM % 2 + 1`
#num1=1
num2=2
#num3=1
	# echo "/usr/local/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg${num2}" --app "?rtmp://fms-base${num3}.mitene.ad.jp/agqr/" --live -o "$filename" --stop $2"
	/usr/local/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg${num2}" --app "?rtmp://fms-base${num3}.mitene.ad.jp/agqr/" --live -o "$filename" --stop $rectime
done
# 保存フォルダへ移動
cd "/data/share/movie/98 PSP用/agqr/flv"
# 映像付きならばエンコード用のシェルを呼ぶ。音声のみならmp3エンコード
if [ $vidflg = v ]; then
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp4" ];
    do
      /data/share/movie/sh/169mp4_agqr.sh "$efilename" "/data/share/movie/98 PSP用/agqr/"
    done
else 
    until [ -f "/data/share/movie/98 PSP用/agqr/$efilename.mp3" ];
    do
      /usr/bin/wine ffmpeg.exe -i "$efilename" -acodec libmp3lame -ab 64k -ac 2 -ar 24000 "/data/share/movie/98 PSP用/agqr/$efilename.mp3"
    done
fi
# rssフィード生成シェル
/home/swirhen/share/movie/sh/mmmpc.sh agqr "超！A&G(+α)"
/home/swirhen/share/movie/sh/mmmpc2.sh agqr "超！A&G(+α)"
# つぶやく
/home/swirhen/Shellscriptter/Shellscriptter.sh -r "【超A&G自動保存終了】$efilename"
