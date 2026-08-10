#!/bin/bash -ex

# mkpi.sh - flashes and configs an SD card for pi

# 3 part:
# 1. init - define source and destination, make sure destination isn't mounted.
# 2. download and burn to destination
# 3. copy clound-init files to destination

# part 1:

# source:
# https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2026-06-19/2026-06-18-raspios-trixie-armhf.img.xz
# https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2026-06-19/2026-06-18-raspios-trixie-armhf-lite.img.xz

img_host=https://downloads.raspberrypi.org

img_path=raspios_armhf/images/raspios_armhf-2026-06-19
zip_name=2026-06-18-raspios-trixie-armhf.img.xz

# img_path=raspios_lite_armhf/images/raspios_lite_armhf-2026-06-19
# zip_name=2026-06-18-raspios-trixie-armhf-lite.img.xz

# Destination
# cash dir to store 1.3 gig img.xz
cache=cache

# dev of SD card to image (Danger Will Robinson!)
dev=/dev/sda
part=sda1
# where pmount will mount it
mnt=/media/${part}

if [ ! -b "${dev}" ]; then
      echo "error: ${dev} is not a block device."
      exit
fi

if findmnt --source /dev/${part}; then
      echo "error: ${dev} has mounted fs's."
      exit
fi

# part 2:
#
# download the image file
# -N - don't download the same thing twice.
wget -N --directory-prefix=${cache} ${img_host}/${img_path}/${zip_name}

# decompress the image file and stream it to the sd card:
xz --decompress --stdout ${cache}/${zip_name}|sudo dd status=progress bs=4M of=${dev}

# part 3:
#
pmount ${part}

# clout-init config - networking, users, apt install...
cp network-config user-data ${mnt}

# copy this script so later we know what built the image
cp $0 ${mnt}

pumount ${part}
