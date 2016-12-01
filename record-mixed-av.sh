#!/bin/sh
# Copyright: 2015,2016    Carl F. Karsten <carl@nextdayvideo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# $1 - destination dir. default: ~/Videos 
# files will be $dest_dir/$date/$time.gs.ts
# (.gs to keep these apart from the files created by record-timestamp.sh)

dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)

mkdir -p $dest_dir

gst-launch-1.0 \
    tcpclientsrc host=localhost port=11000 !\
    \
    matroskademux name=demux \
    \
    demux. !\
        queue !\
        videoconvert !\
        avenc_mpeg2video bitrate=5000000 max-key-interval=0 !\
        queue !\
        mux. \
    \
    demux. !\
        queue !\
        audioconvert !\
        avenc_mp2 bitrate=192000 !\
        queue !\
        mux. \
    \
    mpegtsmux name=mux !\
        filesink location="$dest_dir/$(date +%H_%M_%S).gs.ts"

