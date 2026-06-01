#!/bin/bash -ex

key=${1}
host=${2:-localhost}

location="rtmp://a.rtmp.youtube.com/live2/x/${key}"

# ./stream_vocto.sh
# https://gstreamer.freedesktop.org/documentation/pbutils/encoding-profile.html?gi-language=python
#         video/webm:video/x-vp8+youtube-preset:audio/x-vorbis

# sudo apt install intel-media-va-driver-non-free

exec gst-launch-1.0 \
    -v \
      tcpclientsrc "host=${host}" port=15000 \
    ! matroskademux name=demux \
    ! videoconvert ! deinterlace ! videorate ! videoscale \
    ! vaapih264enc keyframe-period=5 max-bframes=0 bitrate=25000 aud=true \
    ! "video/x-h264,profile=main" \
    ! h264parse config-interval=2 \
    ! flvmux streamable=true name=mux \
    ! rtmpsink location="${location} live=1" demux. \
    ! queue \
    ! audioconvert \
    ! voaacenc bitrate=128000 \
    ! mux.

exit

 #    ! x264enc bitrate=12000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency \
    # ! x264enc bitrate=22000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency \

gst-launch-1.0 \
    -v \
    tcpclientsrc "host=${host}" port=15000 \
    ! matroskademux name=demux \
    ! queue \
    ! vaapih264enc \
      ! h264parse config-interval=2 \
      ! "video/x-h264,profile=main" \
    ! flvmux streamable=true name=mux \
    ! rtmpsink location="${location} live=1" demux. \
    ! queue \
    ! audioconvert \
    ! voaacenc bitrate=128000 \
    ! mux.

exit


