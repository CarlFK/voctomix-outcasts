#!/bin/bash -ex

# Mostly to confirm the basics is installed and setup properly.
cd ../../voctomix

./voctocore/voctocore.py -i ../voctomix-outcasts/configs/test1.ini &
sleep 5
./voctogui/voctogui.py &
../voctomix-outcasts/ingest.py &
../voctomix-outcasts/ingest.py --source-id cam2 &
../voctomix-outcasts/ingest.py \
    --video-attribs "pattern=ball" --source-id grabber &
../voctomix-outcasts/record-timestamp.sh &
../voctomix-outcasts/generate-cut-list.py --file test1.log

