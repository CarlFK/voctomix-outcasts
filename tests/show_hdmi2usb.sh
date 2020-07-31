#!/bin/bash -x

gst-launch-1.0 \
    -v \
     v4l2src device=$1 ! jpegdec ! autovideosink sync=false

