#!/bin/bash -x

dev=${1:-/dev/video0}

gst-launch-1.0 \
    -v \
     v4l2src device=${dev} ! jpegparse ! decodebin3 ! \
     autovideosink sync=false

     # v4l2src device=${dev} ! jpegparse ! vaapidecodebin ! \
