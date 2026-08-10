mk_raspi.sh - main script to download img, dd it to sd card, add cloud-init files
cache/ - dir to hold raspios-trixie-armhf.img.xz
network-config - cloud-init networking
user-data - main cloud-init - keyboard, users, ssh keys, commands to wget/setup HDMI test feed
dl_src.service - runs ../dl_src.sh on boot. (it would if the systemctl enable worked)
