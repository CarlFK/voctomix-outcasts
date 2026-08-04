#!/bin/bash -ex

gst-launch-1.0 audiotestsrc ! autoaudiosink &

while true; do
    xrandr --output HDMI-3 --mode 1920x1080
    sleep 2
    xrandr --output HDMI-3 --mode 1920x1080i
    sleep 2
done
