#!/bin/bash -ex

gst-launch-1.0  \
 -v \
 decklinkvideosrc device-number=0 mode=1080p30 \
 ! fakesink  \
 decklinkaudiosrc device-number=0 \
  ! queue \
  ! audioconvert \
  ! volume volume=.2  \
  ! autoaudiosink
