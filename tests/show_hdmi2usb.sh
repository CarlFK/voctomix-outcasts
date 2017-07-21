#!/bin/bash -ex

gst-launch-1.0 \
    v4l2src !\
     jpegdec !\
     queue ! videoconvert !\
     fpsdisplaysink sync=false

