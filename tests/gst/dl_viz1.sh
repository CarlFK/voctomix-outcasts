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

# (05:02:17 PM) Earnestly: (And btw, if you need to send window commands, xdotool has --sync for many of it's operations, like search, so you don't have to rely on a sleep delay)

# ^c to kill gst-launch
wait


