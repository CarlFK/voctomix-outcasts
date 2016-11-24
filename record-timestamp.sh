#!/bin/bash -ex 
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


# note: this script will crash at midnight, maybe.

# $1 - destination dir. default: ~/Videos 
# files will be $dest_dir/$date/$time.ts

# dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)
dest_dir=${1:-~/Videos}

segment_time=1800  # 30 min

mkdir -p $dest_dir/$(date +%Y-%m-%d)

ffmpeg \
    -i tcp://localhost:11000 \
    -ac 2 -channel_layout 2c -aspect 16:9 \
        -map 0:v -c:v:0 mpeg2video -pix_fmt:v:0 yuv422p -qscale:v:0 2 -qmin:v:0 2 -qmax:v:0 10 -keyint_min 0 -bf:0 0 -g:0 0 -intra:0 -maxrate:0 140M \
        -map 0:a -c:a:0 mp2 -b:a:0 192k -ac:a:0 2 -ar:a:0 48000 \
        -flags +global_header -flags +ilme+ildct \
        -f segment -segment_time $segment_time \
         -segment_format mpegts \
         -strftime 1 "$dest_dir/%Y-%m-%d/%H_%M_%S.ts"


