#!/bin/bash -ex

fname=$(mktemp --suffix=.ts)

# 20 seconds * 30fps
nb=$((2*300))

# I don't understand how to make this stop at 20 sec, this is close
# The resulting file has more audio over the last video frame repeated, I guess.
nb2=$((2*441))
nb2=441

gst-launch-1.0  \
    -v \
    --eos-on-shutdown \
  v4l2src device=/dev/v4l/grabber num-buffers=${nb} \
  ! video/x-raw,framerate=30/1 \
  ! queue \
  ! videoconvert \
  ! avenc_mpeg2video \
  ! queue \
 ! mux. \
 alsasrc device=hw:W30 num-buffers=${nb2}  \
  ! queue \
  ! audioconvert \
  ! avenc_mp2 \
  ! queue \
  ! mux. \
  mpegtsmux name=mux \
  ! filesink location="${fname}"

ls -la ${fname}
gst-play-1.0 ${fname}

