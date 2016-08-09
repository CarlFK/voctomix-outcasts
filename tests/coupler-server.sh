#!/bin/bash -ex
# dummy-server.sh
# something for vocto clients to connect to, 
# displays stream in a local window

gst-launch-1.0 \
    tcpserversrc host=0.0.0.0 port=4953 ! \
    tcpserversink host=0.0.0.0 port=4954 
