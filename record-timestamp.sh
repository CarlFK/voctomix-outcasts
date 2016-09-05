#!/bin/bash -ex 

# note: this script will crash at midnight, maybe.

dest_dir=$1
segment_time=1800

mkdir -p $dest_dir/$HOSTNAME/$(date +%Y-%m-%d)

ffmpeg \
    -i tcp://$VOC_CORE:11000 \
    -ac 2 -channel_layout 2c -aspect 16:9 \
        -map 0:v -c:v:0 mpeg2video -pix_fmt:v:0 yuv422p -qscale:v:0 2 -qmin:v:0 2 -qmax:v:0 10 -keyint_min 0 -bf:0 0 -g:0 0 -intra:0 -maxrate:0 140M \
        -map 0:a -c:a:0 mp2 -b:a:0 192k -ac:a:0 2 -ar:a:0 48000 \
        -flags +global_header -flags +ilme+ildct \
        -f segment -segment_time $segment_time \
         -segment_format mpegts \
         -strftime 1 "$dest_dir/$HOSTNAME/%Y-%m-%d/%H_%M_%S.ts"


