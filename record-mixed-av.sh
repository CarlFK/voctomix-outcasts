#!/bin/sh


dest_dir=$1/$(date +%Y-%m-%d)

mkdir -p $dest_dir

	matroskademux name=demux \
	\
	demux. !\
		queue !\
		videoconvert !\
		avenc_mpeg2video bitrate=5000000 max-key-interval=0 !\
		queue !\
		mux. \
	\
	demux. !\
		queue !\
		audioconvert !\
		avenc_mp2 bitrate=192000 !\
		queue !\
		mux. \
	\
	mpegtsmux name=mux !\
		filesink location="$dest_dir/$(date +%H_%M_%S).gs.ts"

