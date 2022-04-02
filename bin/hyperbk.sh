#!/bin/bash

cd ../tsbk
LAUNCH_CONF='../conf/launch.yaml'

while getopts 'd::f:t:' OPT; do
    echo ${OPT} "$OPTARG"
    case ${OPT} in
        d)
            echo 'TODO';;
        f)
            LAUNCH_CONF="$OPTARG";;
        ?)
            echo "Usage: `basename $0` [options] filename"
     esac
done

if [ ! -d "../log" ]; then
  mkdir ../log
fi

nohup python ../tsbk/benchmark.py -f $LAUNCH_CONF >> ../log/launch.log &

exit 0
