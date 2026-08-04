gst-launch-1.0  \
    -v \
    --eos-on-shutdown \
 decklinkvideosrc device-number=0 mode=1080p30 \
 ! fakesink  \
 decklinkaudiosrc device-number=0 \
 ! tee name=t \
  ! queue \
  ! audioconvert \
  ! avenc_mp2 \
  ! queue \
  ! mux. \
 t. \
  ! queue \
  ! wavescope style=color-dots \
  ! videoconvert \
  ! avenc_mpeg2video \
  ! queue \
  ! mux. \
  mpegtsmux name=mux \
  ! filesink location="$(mktemp --suffix=.ts)"

