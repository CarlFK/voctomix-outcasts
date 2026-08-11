#!/bin/bash -ex

# dl_play.sh - sends decklinkvideosrc to screen, decklinkaudiosrc to speakers.

gst-launch-1.0  \
 -vv \
 decklinkvideosrc device-number=0 mode=1080p30 \
 ! fakesink \
 decklinkaudiosrc device-number=0 \
 ! autoaudiosink
