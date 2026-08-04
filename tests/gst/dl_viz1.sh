#!/bin/bash -ex

gst-launch-1.0  \
 -v \
 decklinkvideosrc device-number=0 mode=1080p30 \
 ! fakesink  \
 decklinkaudiosrc device-number=0 \
 ! tee name=t \
  ! queue \
  ! volume volume=.2  \
  ! autoaudiosink  \
 t. \
  ! queue \
  ! wavescope style=color-dots \
  ! clockoverlay \
  ! videoconvert \
  ! autovideosink \
&

# full screen the gst window
sleep 1
wmctrl -r "gst-launch-1.0" -b add,fullscreen

# ^c to kill gst-launch
wait


