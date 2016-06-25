# Voctomix-Outcasts

Components used with Voctomix.

# Getting started / Demo:
Install the dependencies listed here:
https://github.com/voc/voctomix#installation
```
git clone https://github.com/voc/voctomix.git
git clone https://github.com/CarlFK/voctomix-outcasts.git
cd voctomix-outcasts
cd tests
./test1.sh
```
You should see the gui with 2 bouncing ball test feeds.
It is saving to foo.ts and logging cuts to cut-list.log.

# Production

Voctomix is a small set of components that need to be assembled and configured with additional components.  We try to make all of this open and public, but in general everyone needs to define a system appropriate to their needs. For example, not everyone does a live stream so there is no point in expecting a streaming server to be available. 

That said, here are things used in production:
https://github.com/CarlFK/dvsmon/blob/master/vocto-prod1.py
https://anonscm.debian.org/git/debconf-video/debconf-video.git/tree/src/hdmi2usb/hdmi2usb.py
and I think there are some udev rules around there too.

