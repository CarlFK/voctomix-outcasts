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

# $1 - destination dir. default: ~/Videos/date
# files will be $dest_dir/$date/$time_000000.mov

# $2 - voctoocore host

# $3 - size of files in minutes - default 30 min.

# NB: It chunks files, but the filename is just foo001, foo002...
# currently no support for hh_mm_ss.
# $(date +%H_%M_%S)-%06d.mov is: all files get the time this process started, followed by a segment number.

# https://gstreamer.freedesktop.org/documentation/multifile/splitmuxsink.html?gi-language=c#splitmuxsink

dest_dir=${1:-~/Videos}/$(date +%Y-%m-%d)
vocto_host=${2:-localhost}
file_min=${3:-30}

size_time=$(( ${file_min}*60*1000000000 ))
# max-size-time=1800000000000 should be 30 min
# >>> 1000000000 * 60 *30
# 1800000000000

mkdir -p $dest_dir

exec gst-launch-1.0 \
    -v \
    --eos-on-shutdown \
    tcpclientsrc host=${vocto_host} port=11000 \
    ! matroskademux name=demux \
    demux. \
        ! queue \
        ! videoconvert \
        ! x264enc speed-preset=superfast qp-min=18 psy-tune=animation key-int-max=10 tune=zerolatency \
        ! h264parse \
        ! queue \
        ! mux. \
    demux. \
        ! queue \
        ! audioconvert \
        ! avenc_ac3 bitrate=192000 \
        ! queue \
        ! mux.audio_0 \
    splitmuxsink name=mux \
        use-robust-muxing=true \
        muxer-factory=matroskamux \
          muxer-properties="properties,streamable=true" \
        location="${dest_dir}/$(date +%H_%M_%S)-%06d.mov" \
        max-size-time=${size_time}

#        muxer-factory=qtmux \
#          async-finalize=true \
#          muxer-properties="properties,streamable=true" \
#          muxer-properties="properties,streamable=true,reserved-moov-update-period=10000000000,reserved-max-duration=10000000000,reserved-prefill=true" \

#        muxer-properties="properties,streamable=true,reserved-prefill=true" \

#        muxer-factory=matroskamux \
#          muxer-properties="properties,streamable=true" \

# example from https://gstreamer.freedesktop.org/documentation/multifile/splitmuxsink.html
#  gst-launch-1.0 -e v4l2src num-buffers=500 ! video/x-raw,width=320,height=240 ! videoconvert ! queue ! timeoverlay ! x264enc key-int-max=10 ! h264parse ! splitmuxsink location=video%02d.mkv max-size-time=10000000000 muxer-factory=matroskamux muxer-properties="properties,streamable=true"

# https://gstreamer.freedesktop.org/documentation/isomp4/qtmux.html
# To enable robust muxing mode, set the reserved-moov-update-period and reserved-max-duration property.
#  "Robust Prefill Muxing"
#  reserved-moov-update-period and reserved-prefill properties.

# reserved-moov-update-period (18446744073709551615) When used with reserved-max-duration, periodically updates the index tables with information muxed so far.
# reserved-max-duration (18446744073709551615) When set to a value > 0, reserves space for index tables at the beginning of the file.
# reserved-prefill (false) Prefill samples table of reserved duration:
# start-gap-threshold (0) Threshold for creating an edit list for gaps at the start in nanoseconds
