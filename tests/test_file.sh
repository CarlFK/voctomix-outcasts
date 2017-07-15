# gst-launch-1.0 videotestsrc name=videosrc \! clockoverlay text="Source:twist Caps:video/x-raw,format=I420,width=1280,height=720,framerate=30000/1001,pixel-aspect-ratio=1/1 Attribs: " halignment=left line-alignment=left \! video/x-raw,format=I420,width=1280,height=720,framerate=30000/1001,pixel-aspect-ratio=1/1 \! mux. audiotestsrc name=audiosrc freq=330 \! audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 \! mux. matroskamux name=mux \! tcpclientsink host=127.0.0.1 port=10000

gst-launch-1.0 \
     videotestsrc name=videosrc  !\
            video/x-raw,format=I420,width=1280,height=720,framerate=30000/1001,pixel-aspect-ratio=1/1 !\
     avenc_mpeg2video bitrate=5000000 max-key-interval=0 !\
            queue !\
     mux. \
     audiotestsrc  name=audiosrc freq=330 ! \
            audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 ! \
     avenc_mp2 bitrate=192000 !\
            queue !\
     mux. \
            matroskamux name=mux ! \
     filesink location=test.ts

