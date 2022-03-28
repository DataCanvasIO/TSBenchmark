#!/bin/bash

cd ../hyperbk
LAUNCH_CONF='../conf/launch/launch.yaml'

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

LAUNCH_CONF='../conf/launch.yaml'
nohup python ../hypertsbk/benchmark.py -f $LAUNCH_CONF >> ../log/launch.log &

exit 0
