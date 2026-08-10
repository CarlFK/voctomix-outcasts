#!/bin/bash -ex

# These paramters are for a Raspberry Pi Zero:
randr_cmd=${1:-wlr-randr}
output=${2:-HDMI-A-1}
res0=${3:-1920x1080@30}
res1=${4:-1920x1080@24}
audio_fmt=${5:-F64LE}

# for my x86 box:
# ./dl_src.sh xrandr HDMI-1 1920x1080 1920x1080i S16LE

# play a tone and flip video modes between valid (decklinkvideosrc mode=1080p30)
# and about anything else.  like 1080i, or @24, or 720p.

gst-launch-1.0 audiotestsrc ! audio/x-raw,format=${audio_fmt} ! alsasink &

export DISPLAY=:0

while true; do
    ${randr_cmd} --output ${output} --mode ${res0}
    sleep 2
    ${randr_cmd} --output ${output} --mode ${res1}
    sleep 2
done

# somehow this kills the backgrounded audiotestsrc
wait
