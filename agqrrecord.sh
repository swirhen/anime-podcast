#!/usr/bin/env bash
# ��A&G�\��^��p�X�N���v�g
# require: rtmpdump,ffmpeg,���낢��
# usage: agqrrecord.sh [�ԑg��] [�J�n�I�t�Z�b�g] [�^�掞��] [����t���O] [�u�T�t���O�t�@�C����]
# �ԑg��: YYYYMMDD_HHMM_�ԑg��.flv �Ƃ����t�@�C���ɂȂ�
# �J�n�I�t�Z�b�g: sec
# �^�掞��: sec
# ����t���O: v�Ȃ�f���t���A����ȊO�Ȃ特���ƌ��Ȃ��ăG���R����
# �u�T�t���O�t�@�C����: 
#     �t���O�t�@�C�������邩�ǂ����`�F�b�N���āA�Ȃ���΍쐬�������Ę^�悵�Ȃ�
#     ����΍폜���Ę^�悷��
name=$1
offset=$2
rectime=$3
vidflg=$4
recflg=$5
PYTHON_PATH="python3"
# �I�t�Z�b�g
sleep $offset
# �u�T�Ή�
if [ "${recflg:-null}" != null ]; then
flgfile="/data/share/movie/98 PSP�p/agqr/flg/$recflg"
	if [ -f "$flgfile" ]; then
		rm "$flgfile"
	else
		touch "$flgfile"
		exit
	fi
fi
# ���t����
dt=`date +"%Y%m%d_%H%M"`
# �ۑ��t�@�C����
filename="/data/share/movie/98 PSP�p/agqr/flv/""$dt"_"$name.flv"
# �p�X���������t�@�C����
efilename="$dt"_"$name.flv"
# �Ԃ₭
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "�y��A&G�����ۑ��J�n�z$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "�y��A&G�����ۑ��J�n�z$efilename"
# �ڑ����s�΍�A�t�@�C�������������܂ŏ������J��Ԃ�
until [ -s "$filename" ]
do
# �����_���ϐ�(�T�[�o���U�Ή�)
num=`expr $RANDOM % 2 + 1`
#num2=`expr $RANDOM % 2 + 1`
#num3=`expr $RANDOM % 2 + 1`
#	/usr/local/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg22" --app "?rtmp://fms-base1.mitene.ad.jp/agqr/" --live -o "$filename" --stop $rectime
	/usr/bin/rtmpdump --rtmp "rtmpe://fms${num}.uniqueradio.jp/" --playpath "aandg22" --app "?rtmp://fms-base1.mitene.ad.jp/agqr/" --live -o "$filename" --stop $rectime
done
# �ۑ��t�H���_�ֈړ�
cd "/data/share/movie/98 PSP�p/agqr/flv"
# �f���t���Ȃ�΃G���R�[�h�p�̃V�F�����ĂԁB�����݂̂Ȃ�mp3�G���R�[�h
if [ $vidflg = v ]; then
    until [ -f "/data/share/movie/98 PSP�p/agqr/$efilename.mp4" ];
    do
      /data/share/movie/sh/169mp4_agqr.sh "$efilename" "/data/share/movie/98 PSP�p/agqr/"
    done
else 
    until [ -f "/data/share/movie/98 PSP�p/agqr/$efilename.mp3" ];
    do
      /usr/bin/wine ffmpeg.exe -i "$efilename" -acodec libmp3lame -ab 64k -ac 2 -ar 24000 "/data/share/movie/98 PSP�p/agqr/$efilename.mp3"
    done
fi
# rss�t�B�[�h�����V�F��
/data/share/movie/sh/mmmpc.sh agqr "���IA&G(+��)"
#/data/share/movie/sh/mmmpc3.sh agqr "���IA&G(+��)���[�J���p"
# �Ԃ₭
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "�y��A&G�����ۑ��I���z$efilename"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "�y��A&G�����ۑ��I���z$efilename"
