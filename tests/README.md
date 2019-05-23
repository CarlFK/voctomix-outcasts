Testing ingest.py (and other related bits.)

ingest.py is a client, it needs a server to connect to, like voctocore or
dummy-server.py

run ./dummy-server.py
and then ./ingest.py

A window should open and you see the gst test pattern.
That's how you know it is working.

^c dummy-server.py and run it again:
./ingest.py --video-source spacescope
./ingest.py --video-source hdmi2usb --video-attribs "device=/dev/video1"
./ingest.py --video-source file --video-attribs "location=17_58_47.ts"


