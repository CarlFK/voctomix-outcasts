#!/bin/sh


dest_dir=$1/$HOSTNAME/$(date +%Y-%m-%d)

mkdir -p $dest_dir

gst-launch-1.0 \
    tcpclientsrc host=127.0.0.1 port=11000 !\
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
        filesink location="$dest_dir/$HOSTNAME/$(date +%H_%M_%S).gs.ts"

