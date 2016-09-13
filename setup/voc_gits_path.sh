#!/bin/bash -ex

# git clone git://github.com/CarlFK/voctomix-outcasts.git

# put voctomix and dvsmon next to voctomix-outcasts dir
cd ../..
gitdirs=$PWD
git clone https://github.com/voc/voctomix.git
git clone git://github.com/CarlFK/dvsmon.git

# create symlinks
cd ~/bin

ln -s $gitdirs/voctomix/voctocore/voctocore.py voctocore
ln -s $gitdirs/voctomix/voctogui/voctogui.py voctogui

ln -s $gitdirs/voctomix-outcasts/ingest.py ingest

ln -s $gitdirs/voctomix-outcasts/record-timestamp.sh record-timestamp
ln -s $gitdirs/voctomix-outcasts/record-mixed-av.sh record-mixed-av
ln -s $gitdirs/voctomix-outcasts/generate-cut-list.py generate-cut-list

