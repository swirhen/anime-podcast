# /bin/sh
# ��A&G�\��^��ăG���R�[�h�p�X�N���v�g
# require: ffmpeg
# usage: agqrrecord.sh [flv�t�@�C����] [����t���O]
# ����t���O: v�Ȃ�f���t���A����ȊO�Ȃ特���ƌ��Ȃ��ăG���R����
vidflg=$2
# �p�X���������t�@�C����
efilename="$1"
# �ۑ��t�H���_�ֈړ�
cd "/data/share/movie/98 PSP�p/agqr/flv"
# �f���t���Ȃ�΃G���R�[�h�p�̃V�F�����ĂԁB�����݂̂Ȃ�mp3�G���R�[�h
if [ $# -eq 2 ]; then
  echo "video"
    until [ -f "/data/share/movie/98 PSP�p/agqr/$efilename.mp4" ];
    do
      /data/share/movie/sh/169mp4_agqr.sh "$efilename" "/data/share/movie/98 PSP�p/agqr/" $3
    done
else 
    until [ -f "/data/share/movie/98 PSP�p/agqr/$efilename.mp3" ];
    do
      /usr/bin/wine ffmpeg.exe -i "$efilename" -acodec libmp3lame -ab 64k -ac 2 -ar 24000 "/data/share/movie/98 PSP�p/agqr/$efilename.mp3"
    done
fi

# rss�t�B�[�h�����V�F��
/data/share/movie/sh/mmmpc.sh agqr "���IA&G(+��)"
/data/share/movie/sh/mmmpc2.sh agqr "���IA&G(+��)"
