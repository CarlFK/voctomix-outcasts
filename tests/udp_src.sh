#!/bin/sh

WIDTH=1280
HEIGHT=720
FRAMERATE=30

AUDIORATE=48000

gst-launch-1.0 -v\
    videotestsrc !\
        video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FRAMERATE/1,pixel-aspect-ratio=1/1 ! \
        x264enc speed-preset=ultrafast bitrate=4000 ! video/x-h264, profile=baseline !\
        h264parse !\
        mux. \
     \
     audiotestsrc !\
	queue !\
        audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=$AUDIORATE !\
        avenc_mp2 bitrate=192000 !\
        mpegaudioparse !\
	mux. \
      mpegtsmux alignment=7 name=mux !\
        video/mpegts,systemstream=true, packetsize=188 !\
	udpsink max-bitrate=5000000 ttl-mc=7 host=localhost port=21000
