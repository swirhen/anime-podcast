    LIST="/data/share/movie/98 PSP—p/list.txt"
    while read SF NAME
    do
      /data/share/movie/sh/mmmpc.sh "${SF}" "${NAME}"
    done < ${LIST}
