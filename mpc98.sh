    LIST="/data/share/movie/98 PSP用/list.txt"
    while read SF NAME
    do
      /data/share/movie/sh/mmmpc.sh "${SF}" "${NAME}"
    done < ${LIST}
