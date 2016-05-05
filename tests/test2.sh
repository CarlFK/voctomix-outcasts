#!/bin/bash -ex

# Mostly to confirm the basics is installed and setup properly. 
# test1.sh expects git checkouts, test2 installed on $PATH

voctocore -i /etc/voctomix/light.ini &
sleep 5
voctogui &
ingest &
sleep 1
ingest --port 10001 &
record-mixed-av &
generate-cut-list
