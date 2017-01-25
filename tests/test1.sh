#!/bin/bash -ex

# Mostly to confirm the basics is installed and setup properly.
cd ../../voctomix

./voctocore/voctocore.py -i ../voctomix-outcasts/configs/light.ini &
sleep 5
./voctogui/voctogui.py &
../voctomix-outcasts/ingest.py &
../voctomix-outcasts/ingest.py --source-id grabber &
../voctomix-outcasts/record-timestamp.sh &
../voctomix-outcasts/generate-cut-list.py --file foo.log

