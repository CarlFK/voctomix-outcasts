#!/bin/sh

set -euf

# 300 frames of test pattern and beeps:
/home/juser/voctomix-outcasts/ingest.py \
	--host cnt6 \
	--port 10001 \
	--video-source test \
	--video-attribs "pattern=smpte75 num-buffers=200" \
	--audio-source test \
	--audio-attribs "num-buffers=200" \
	--no-clock

# Sometimes the uvcvideo driver gets stuck waiting for the HDMI2USB firmware to
# respond but it never will. Removing the module and adding it back will reset
# these timeouts getting things working again faster.
# https://github.com/xfxf/lca2017-av/issues/33
if [ $(id -u) -eq 0 ]; then
	rmmod uvcvideo || true
	modprobe uvcvideo
fi

CMD="/home/juser/voctomix-outcasts/ingest.py
	--host cnt6
	--port 10001
	--video-source hdmi2usb
	--video-attribs device=/dev/hdmi2usb/by-num/all0/video
"

# if there is a sound card, use it.
# and dump the clock becuase of my c2 cpu is to slow :(
if [ -d /proc/asound/card1 ]; then
	CMD="$CMD
	--audio-source alsa
	--audio-attribs device=hw:1
	--no-clock
"
fi

exec $CMD
