#!/bin/sh

# $1 - destination dir. default: ~/Videos 
# files will be $dest_dir/$date/$time.gs.ts
# (.gs to keep these apart from the files created by record-timestamp.sh)

dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)

mkdir -p $dest_dir

gst-launch-1.0 \
    tcpclientsrc host=127.0.0.1 port=4954 !\
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

