#!/bin/bash

# mon_fs.sh - Voctomoix Monitor Full Screen

echo sudo apt install wmctl

# wmctrl -a "Voctomix GUI"
# wmctrl -r "Voctomix GUI" -b add,fullscreen
#
wmctrl -a "Python3"
sleep 1
wmctrl -r "Python3" -b add,fullscreen

echo sudo apt install unclutter
# unclutter -idle 0

echo wmctrl -r "Python3" -b remove,fullscreen

echo wmctrl -a "Voctomix GUI"

unclutter -idle 0
