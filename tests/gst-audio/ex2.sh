#!/bin/bash -ex

filename=/home/carl/temp/geebee/dv/room1/2026-08-18/19_37_33-000008.mkv


gst-launch-1.0 -v \
    filesrc location=${filename} ! matroskademux ! avdec_ac3 ! audioconvert ! deinterleave name=d \
  d.src_0 ! queue ! audioconvert ! wavenc ! filesink location="channel_0.wav" \
  d.src_1 ! queue ! audioconvert ! wavenc ! filesink location="channel_1.wav" \
  d.src_2 ! queue ! audioconvert ! wavenc ! filesink location="channel_2.wav" \
  d.src_3 ! queue ! audioconvert ! wavenc ! filesink location="channel_3.wav" \
  d.src_4 ! queue ! audioconvert ! wavenc ! filesink location="channel_4.wav" \
  d.src_5 ! queue ! audioconvert ! wavenc ! filesink location="channel_5.wav"

