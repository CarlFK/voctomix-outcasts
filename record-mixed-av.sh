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
# files will be $dest_dir/$date/$time_000000.mov

# NB: It now chunks files, but the filename is just foo001, foo002...
# currently no support for hh_mm_ss.
# $(date +%H_%M_%S)-%06d.mov is: all files get the time this process started, followed by a segment number.

# https://gstreamer.freedesktop.org/documentation/multifile/splitmuxsink.html?gi-language=c#splitmuxsink


dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)

mkdir -p $dest_dir

exec gst-launch-1.0 \
    --eos-on-shutdown \
    tcpclientsrc host=10.20.2.7 port=11000 ! \
    \
    matroskademux name=demux \
    \
    demux. !\
        queue !\
        videoconvert !\
        x264enc speed-preset=superfast qp-min=18 psy-tune=animation key-int-max=10 tune=zerolatency ! \
        h264parse !\
        queue !\
        mux. \
    \
    demux. !\
        queue !\
        audioconvert !\
        avenc_mp2 bitrate=192000 !\
        queue !\
        mux.audio_0 \
    \
    splitmuxsink name=mux location="${dest_dir}/$(date +%H_%M_%S)-%06d.mov" max-size-time=1800000000000

# max-size-time=1800000000000 should be 30 min
# >>> 1000000000 * 60 *30
# 1800000000000

