#!/bin/bash -ex

gst-launch-1.0 \
    v4l2src device=/dev/video1 !\
     jpegdec !\
     queue ! videoconvert !\
     fpsdisplaysink sync=false

