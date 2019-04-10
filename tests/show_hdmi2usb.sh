#!/bin/bash -x

gst-launch-1.0 \
    -v \
    v4l2src device=/dev/$1 !\
    decodebin !\
     queue ! videoconvert !\
     fpsdisplaysink sync=false

    # video/raw,width=1280,height=720 !\
    # video/raw,width=1280,height=960 !\
     # jpegdec !\
    # decodebin !\
    # video/x-raw, format=(string)YUY2, width=(int)1920, height=(int)1080, pixel-aspect-ratio=(fraction)1/1, interlace-mode=(string)progressive, colorimetry=(string)2:4:7:1, framerate=(fraction)5/1'
    # video/x-raw, format=YUY2, width=1920, height=1080, pixel-aspect-ratio=1/1, interlace-mode=progressive, colorimetry=2:4:7:1, framerate=5/1 !\
