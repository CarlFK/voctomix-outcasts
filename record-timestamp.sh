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


# note: this script will crash at midnight.
# [segment @ 0x13bb960] Failed to open segment '.../2017-02-07/00_17_55.ts'
# av_interleaved_write_frame(): No such file or directory


# $1 - destination dir. default: ~/Videos
# files will be $dest_dir/$date/$time.ts

# dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)
dest_dir=${1:-~/Videos}

segment_time=1800  # 30 min

mkdir -p $dest_dir/$(date +%Y-%m-%d)

exec ffmpeg \
    -nostdin -y \
    -analyzeduration 10000 \
    -thread_queue_size 512 \
    -i tcp://localhost:11000?timeout=3000000 \
    -aspect 16:9 \
    -map 0:v -c:v:0 mpeg2video -pix_fmt:v:0 yuv420p -qscale:v:0 4 -qmin:v:0 4 -qmax:v:0 4 -keyint_min:v:0 5 -bf:v:0 0 -g:v:0 5 -me_method:v:0 dia \
    -map 0:a -c:a mp2 -b:a 384k -ac:a 2 -ar:a 48000 \
    -flags +global_header \
        -f segment -segment_time $segment_time \
         -segment_format mpegts \
         -strftime 1 "$dest_dir/%Y-%m-%d/%H_%M_%S.ts"

