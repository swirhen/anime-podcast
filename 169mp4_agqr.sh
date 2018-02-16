# /bin/sh
# @author swirhen
# ffmpeg��������PSP�₠���ق�ނ��̂ǂ���������
# wine��������windows�΂�̂΂��Ȃ�������Ă��܂���
# �Ԃ񂩂ق����� ����[A&G����悤 �Ă��Ƃ����񂱂΁[�����
# usage:169mp4_agqr.sh [infile] [out directory]

# �ǂ炢�Ԃ��������ǂ����̂Ƃ���tmp���Ă����Ȃ΂���ɂ�����
# ���������ł��ꂭ�Ƃ肩�� �h���C�u���͂񂾂�
tmp=`readlink -f "$PWD"`
drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
# �����傭���������Ă�����Ă�΂��� ������
if [ "${2:-null}" != null -o "${2:-null}" != "" ]; then
  tmp=`readlink -f "$2"`
  drive=`expr "$tmp" : "\/\(data.\?\)\/.*"`
fi
# �킩��Ȃ��΂����� /data
if [ ${drive:-null} = null ] ; then
  drive=data
fi
# ���񂱂���
/usr/bin/wine ffmpeg.exe -i "$1" $3 $4 -vcodec copy -f mp4 -acodec libfaac -ac 2 -ar 24000 -ab 64k -threads 0 /$drive/tmp/"$1".mp4
# MP4Box�� faststart���������ɂ���
#sleep 5
#/usr/local/bin/MP4Box -ipod -par 1=1:1 /$drive/tmp/"$1".mp4 -out /$drive/tmp/"$1"_mod.mp4
#rm /$drive/tmp/"$1".mp4
#sleep 5
/bin/mv -v /$drive/tmp/"$1".mp4 "$2""$1".mp4
