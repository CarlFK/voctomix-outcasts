#!/bin/bash -ex

# Mostly to confirm the basics is installed and setup properly. 
# test1.sh expects git checkouts, test2 installed on $PATH

voctocore -i /etc/vocto/light.ini & \
    sleep 5; \
voctogui.py &
ingest.py &
ingest.py --port 10001 &
record-mixed-av.sh &
generate-cut-list.py
