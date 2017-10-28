    LIST="/data/share/movie/98 PSP用/list.txt"
    while read SF NAME
    do
      /home/swirhen/share/movie/sh/mmmpc.sh "${SF}" "${NAME}"
    done < ${LIST}
