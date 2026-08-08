#!/bin/bash -ex

# mkpi.sh - flashes and configs an SD card for pi

# https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2026-06-19/2026-06-18-raspios-trixie-armhf.img.xz
# https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2026-06-19/2026-06-18-raspios-trixie-armhf-lite.img.xz
# https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2026-06-19/2026-06-18-raspios-trixie-armhf_lite.img.xz


img_host=https://downloads.raspberrypi.org

# img_path=raspios_armhf/images/raspios_armhf-2026-06-19
# zip_name=2026-06-18-raspios-trixie-armhf.img.xz

img_path=raspios_lite_armhf/images/raspios_lite_armhf-2026-06-19
zip_name=2026-06-18-raspios-trixie-armhf-lite.img.xz

dev=/dev/sda
part=sda1
mnt=/media/${part}

# dir to store 400M compressed image file
cache=cache

# download the image file
# -N - don't download the same thing twice.
wget -N --directory-prefix=${cache} ${img_host}/${img_path}/${zip_name}

# decompress the image file and stream it to the sd card:
xz --decompress --stdout ${cache}/${zip_name}|sudo dd status=progress of=${dev}

pmount ${part}
cp network-config user-data ${mnt}
pumount ${part}

