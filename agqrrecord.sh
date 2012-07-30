# /bin/sh
# 超A&G予約録画シェルスクリプト
# require: rtmpdump,ffmpeg,いろいろ
# usage: agqrrecord.sh [番組名] [録画時間] [動画フラグ] [隔週フラグファイル名]
# 番組名: YYYYMMDD_HHMM_番組名.flv というファイルになる
# 録画時間: sec
# 動画フラグ: vなら映像付き、それ以外なら音声と見なしてエンコする
# 隔週フラグファイル名: 
#     フラグファイルがあるかどうかチェックして、なければ作成だけして録画しない
#     あれば削除して録画する
# 隔週対応
if [ "${4:-null}" != null ]; then
flgfile="/data/share/movie/98 PSP用/agqr/flg/$4"
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
filename="/data/share/movie/98 PSP用/agqr/flv/""$dt"_"$1.flv"
# パスを除いたファイル名
efilename="$dt"_"$1.flv"
# 接続失敗対策、ファイルが生成されるまで処理を繰り返す
until [ -s "$filename" ]
do
	# ランダム変数(サーバ分散対応)
	num=`expr $RANDOM % 2 + 1`
	num2=`expr $RANDOM % 2 + 1`
	num3=`expr $RANDOM % 2 + 1`
	# echo "/usr/local/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg${num2}" --app "?rtmp://fms-base${num3}.mitene.ad.jp/agqr/" --live -o "$filename" --stop $2"
	/usr/local/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg${num2}" --app "?rtmp://fms-base${num3}.mitene.ad.jp/agqr/" --live -o "$filename" --stop $2
done
# 保存フォルダへ移動
cd "/data/share/movie/98 PSP用/agqr/flv"
# 映像付きならばエンコード用のシェルを呼ぶ。音声のみならmp3エンコード
if [ $3 = v ]; then
	/data/share/movie/sh/169mp4_agqr.sh "$efilename" "/data/share/movie/98 PSP用/agqr/"
else 
	/usr/bin/wine ffmpeg.exe -i "$efilename" -acodec libmp3lame -ab 64k -ac 2 -ar 48000 "/data/share/movie/98 PSP用/agqr/$efilename.mp3"
fi
# rssフィード生成シェル
/home/swirhen/share/movie/sh/mmmpc.sh agqr "超！A&G"
/home/swirhen/share/movie/sh/mmmpc2.sh agqr "超！A&G"
# つぶやく
/home/swirhen/Shellscriptter/Shellscriptter.sh -r "【超A&G自動録画】$efilename"
