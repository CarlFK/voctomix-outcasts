#!/bin/bash -x

# core server
gst-launch-1.0 \
    tcpserversrc host=127.0.0.1 port=4953 ! \
    queue ! matroskaparse ! \
    tcpserversink host=127.0.0.1 port=4954  \
& srv=$!
sleep 1
function finish {
  kill $srv 2> /dev/null
}
trap finish EXIT

# test source client
gst-launch-1.0 \
            videotestsrc name=videosrc ! \
     mux. \
            audiotestsrc  name=audiosrc ! \
     mux. \
            matroskamux streamable=true name=mux ! \
    tcpclientsink host=127.0.0.1 port=4953 \
&

# file sink client
gst-launch-1.0 \
    tcpclientsrc host=127.0.0.1 port=4954 !\
	matroskademux name=demux \
	demux. !\
		queue !\
		videoconvert !\
		avenc_mpeg2video bitrate=5000000 max-key-interval=0 !\
		queue !\
		mux. \
	demux. !\
		queue !\
		audioconvert !\
		avenc_mp2 bitrate=192000 !\
		queue !\
		mux. \
	mpegtsmux name=mux !\
		filesink location="/tmp/test.ts"
