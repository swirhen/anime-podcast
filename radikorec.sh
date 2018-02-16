#!/bin/bash
# Original1: https://gist.github.com/875864 saiten / rec_radiko.sh
# Original2: http://backslash.ddo.jp/wordpress/archives/1020 http://backslash.ddo.jp/tools/rec_radiko2.txt 

# Install: wget swftools rtmpdump ffmpeg http://d.hatena.ne.jp/zariganitosh/20130120/radiko_recoding_again

PATH=$PATH:/usr/local/bin
PYTHON_PATH="python3"
VERSION=4.0.0

# égÇ¢ï˚
show_usage() {
  echo "Usage: $COMMAND [-a] [-o bangumi_mei] [-t recording_seconds] station_ID"
  echo '       -a  Output area info(ex. 'JP13,ìåãûìs,tokyo Japan'). No recording.'
  echo '       -o  Default output_name = /data/tmp/[${station_name}]_`date +%Y%m%d-%H%M`.flv'
  echo '             "hogehoge" = /data/tmp/[JOQR]hogehoge_20130123-1700.flv'
  echo '       -t  Default recording_seconds = 30'
  echo '           60 = 1 minute, 3600 = 1 hour, 0 = go on recording until stopped(control-C)'
}

# îFèÿ
radiko_authorize() {
  echo "==== authorize ===="
  #
  # get player
  #
  if [ ! -f $playerfile ]; then
    echo $playerfile downloading...
    /usr/bin/wget -q -O $playerfile $playerurl

    if [ $? -ne 0 ]; then
      echo "failed get player"
      exit 1
    fi
  fi

  #
  # get keydata (need swftool)
  #
  if [ ! -f $keyfile ]; then
    echo $keyfile extracting...
    # swfextract -b 5 $playerfile -o $keyfile <---radikoédólïœçXì_
    /usr/bin/swfextract -b 12 $playerfile -o $keyfile

    if [ ! -f $keyfile ]; then
      echo "failed get keydata"
      exit 1
    fi
  fi

  #
  # access auth1_fms
  #
  wget -q \
       --header="pragma: no-cache" \
       --header="X-Radiko-App: pc_ts" \
       --header="X-Radiko-App-Version: $VERSION" \
       --header="X-Radiko-User: test-stream" \
       --header="X-Radiko-Device: pc" \
       --post-data='\r\n' \
       --no-check-certificate \
       --save-headers \
       https://radiko.jp/v2/api/auth1_fms -O auth1_fms_$$

  if [ $? -ne 0 ]; then
    echo "failed auth1 process"
    exit 1
  fi

  #
  # get partial key
  #
  authtoken=`perl -ne 'print $1 if(/x-radiko-authtoken: ([\w-]+)/i)' auth1_fms_$$`
  offset=`perl -ne 'print $1 if(/x-radiko-keyoffset: (\d+)/i)' auth1_fms_$$`
  length=`perl -ne 'print $1 if(/x-radiko-keylength: (\d+)/i)' auth1_fms_$$`
  partialkey=`dd if=$keyfile bs=1 skip=${offset} count=${length} 2> /dev/null | base64`

  echo "authtoken: ${authtoken}\n offset: ${offset}\n length: ${length}\n partialkey: $partialkey"
    
  #
  # access auth2_fms
  #  
  /usr/bin/wget -q \
       --header="pragma: no-cache" \
       --header="X-Radiko-App: pc_ts" \
       --header="X-Radiko-App-Version: $VERSION" \
       --header="X-Radiko-User: test-stream" \
       --header="X-Radiko-Device: pc" \
       --header="X-Radiko-Authtoken: ${authtoken}" \
       --header="X-Radiko-Partialkey: ${partialkey}" \
       --post-data='\r\n' \
       --no-check-certificate \
       https://radiko.jp/v2/api/auth2_fms -O auth2_fms_$$

  if [ $? -ne 0 -o ! -f auth2_fms_$$ ]; then
    echo "failed auth2 process"
    exit 1
  fi

  echo "authentication success"

  areaid=`/usr/bin/perl -ne 'print $1 if(/^([^,]+),/i)' auth2_fms_$$`
  echo "areaid: $areaid"  
}

# ò^âπ
radiko_record() {
  echo "==== recording ===="
  #
  # get stream-url
  #
  channel_xml=`/usr/bin/wget -q "http://radiko.jp/v2/station/stream/${channel}.xml" -O -`
  stream_url=`echo $channel_xml | sed 's/^\(<?xml .*\)[Uu][Tt][Ff]8\(.* ?>\)/\1UTF-8\2/' | /usr/bin/xpath -e "//url/item[1]/text()" 2>/dev/null`
  stream_url_parts=(`echo ${stream_url} | perl -pe 's!^(.*)://(.*?)/(.*)/(.*?)$/!$1://$2 $3 $4!'`)

  #
  # get authtoken
  #
  authtoken=`perl -ne 'print $1 if(/x-radiko-authtoken: ([\w-]+)/i)' auth1_fms_$$`

  #
  # rtmpdump
  #
  echo "save as '$output'"
  echo "rtmpdump -r ${stream_url_parts[0]}
--app ${stream_url_parts[1]}
--playpath ${stream_url_parts[2]}
-W $playerurl
-C S: -C S: -C S: -C S:$authtoken
--live
--stop ${rectime:=30}
--flv ${output}"
 nohup rtmpdump -r ${stream_url_parts[0]} \
           --app ${stream_url_parts[1]} \
           --playpath ${stream_url_parts[2]} \
           -W $playerurl \
           -C S:"" -C S:"" -C S:"" -C S:$authtoken \
           --live \
           --stop "${rectime:=30}" \
           --flv "${output}" &
  pid=$!
}

# à¯êîâêÕ
COMMAND=`basename $0`
while getopts aho:t: OPTION
do
  case $OPTION in
    a ) OPTION_a="TRUE" ;;
    o ) OPTION_o="TRUE" ; VALUE_o="$OPTARG" ;;
    t ) OPTION_t="TRUE" ; VALUE_t="$OPTARG" ;;
    * ) show_usage ; exit 1 ;;
  esac
done

shift $(($OPTIND - 1)) #écÇËÇÃîÒÉIÉvÉVÉáÉìÇ»à¯êîÇÃÇ›Ç™ÅA$@Ç…ê›íËÇ≥ÇÍÇÈ

if [ $# = 0 -a "$OPTION_a" != "TRUE" ]; then
  show_usage ; exit 1
fi

# ÉIÉvÉVÉáÉìèàóù
channel=$1

if [ "$OPTION_o" = "TRUE" ]; then
   pgmname="$VALUE_o"
fi

if [ "$OPTION_t" = "TRUE" ]; then
  rectime=$VALUE_t
fi

cd /data/tmp ; wdir=`pwd`

station_name=`curl -s "http://radiko.jp/v2/api/program/station/today?station_id=$channel" |/usr/bin/xpath -e "//station/name/text()" 2>/dev/null`
output="${wdir}/${fname:=[${station_name}]${pgmname}_`date +%Y%m%d-%H%M`}.flv"

# playerurl=http://radiko.jp/player/swf/player_2.0.1.00.swf <---radikoédólïœçXì_
#playerurl=http://radiko.jp/player/swf/player_$VERSION.swf
playerurl=http://radiko.jp/apps/js/flash/myplayer-release.swf
playerfile=./player.swf
keyfile=./authkey.jpg

if [ "$OPTION_a" = "TRUE" ]; then
  radiko_authorize
  if [ $? = 0 ]; then
    cat auth2_fms_$$|grep -e '^\w\+'
  fi
else
# Ç¬Ç‘Ç‚Ç≠
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "ÅyRadikoé©ìÆò^âπäJénÅz${station_name} ${pgmname}"
#/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "ÅyRadikoé©ìÆò^âπäJénÅz${fname}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "ÅyRadikoé©ìÆò^âπäJénÅz${fname}"

#until [ -f "${output}" ];
#do
#  radiko_authorize && radiko_record
#done

radiko_authorize
if [ $? = 0 ]; then
  radiko_record
fi

sleep ${rectime}
sleep 30

kill ${pid}

/usr/bin/wine ffmpeg.exe -y -t ${rectime} -i "${output}" -acodec copy "/data/share/movie/98 PSPóp/agqr/${fname}.m4a"

rm -f "${output}"

# rssÉtÉBÅ[Éhê∂ê¨ÉVÉFÉã
/data/share/movie/sh/mmmpc.sh agqr "í¥ÅIA&G(+Éø)"
# Ç¬Ç‘Ç‚Ç≠
/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "ÅyRadikoé©ìÆò^âπèIóπÅz${station_name} ${pgmname}"
#/home/swirhen/tiasock/tiasock_common.sh "#Twitter@t2" "ÅyRadikoé©ìÆò^âπèIóπÅz${fname}"
${PYTHON_PATH} /home/swirhen/sh/slackbot/swirhentv/post.py "bot-open" "ÅyRadikoé©ìÆò^âπèIóπÅz${fname}"
fi

rm -f auth1_fms_$$
rm -f auth2_fms_$$
