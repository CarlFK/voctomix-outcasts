#!/bin/bash -x

gst-launch-1.0 \
            videotestsrc name=videosrc ! \
     mux. \
            audiotestsrc  name=audiosrc ! \
     mux. \
            matroskamux streamable=true name=mux ! \
    tcpserversink host=127.0.0.1 port=4954  


