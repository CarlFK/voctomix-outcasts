HDMI source builder

Usage:
```
git clone https://github.com/CarlFK/voctomix-outcasts
cd voctomix-outcasts/tests/gst/rpi
./mk_raspi.sh /dev/sdX
```

* mk_raspi.sh - main script to download img, dd it to sd card, add cloud-init files
* cmdline.txt - mostly to enable watching boot logs for debugging
* network-config - cloud-init networking
* user-data - main cloud-init - keyboard, users, ssh keys, commands to wget/setup HDMI test feed
* dl_src.service - runs ../dl_src.sh on boot. (it would if the systemctl enable worked)
