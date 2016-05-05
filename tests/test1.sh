#!/bin/bash -ex

# Mostly to confirm the basics is installed and setup properly. 
cd ../../voctomix

./voctocore/voctocore.py -i ../voctomix-outcasts/configs/light.ini &
sleep 5
./voctogui/voctogui.py &
../voctomix-outcasts/ingest.py &
sleep 1
../voctomix-outcasts/ingest.py --port 10001 &
./example-scripts/gstreamer/record-mixed-av.sh &
./example-scripts/control-server/generate-cut-list.py
