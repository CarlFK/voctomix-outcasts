#!/usr/bin/env python3

# ingest.py
"""
Source client for Voctomix.
Features:
    Retrieves audio and video-caps config from core.
    Uses core's clock.
    Mix and match audio and video sources muxed into one streem.
    Can display video locally, including frame count and fps.
    Defaults to test audio and video sent to local core.

"""

import argparse
import gi
import os
import signal
import socket
import sys

gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
from gi.repository import Gst, GstNet, GObject

# init GObject & Co. before importing local classes
GObject.threads_init()
Gst.init([])

import lib.connection as Connection


def mk_video_src(args, videocaps):
    # make video soure part of pipeline

    d={ 'attribs': args.video_attribs }

    d['monitor'] = """tee name=t ! queue !
                    videoconvert ! fpsdisplaysink sync=false 
                    t. ! queue !""" \
        if args.monitor else ""

    if args.video_source == 'dv':
        video_src = """
            dv1394src name=videosrc {attribs} !
		dvdemux name=demux !
		queue !
		dvdec !
                {monitor}
		deinterlace mode=1 !
		videoconvert !
                videorate !
                videoscale !
            """
    
    elif args.video_source == 'hdv':
        video_src = """
            hdv1394src {attribs} do-timestamp=true name=videosrc !
		tsdemux name=demux!
		queue !
		decodebin !
                {monitor}
		deinterlace mode=1 !
		videorate !
                videoscale !
		videoconvert !
            """

    elif args.video_source == 'hdmi2usb':
        # https://hdmi2usb.tv
        # Note: this code works with 720p
        video_src = """
            v4l2src {attribs} name=videosrc !
                queue !
		image/jpeg,width=1280,height=720 !
                jpegdec !
                {monitor}
                videoconvert !
                videoscale !
                videorate !
            """

    elif args.video_source == 'ximage':
        video_src = """
            ximagesrc {attribs} name=videosrc 
                   use-damage=false !
                {monitor}
		videoconvert !
                videorate !
                videoscale !
            """
                # startx=0 starty=0 endx=1919 endy=1079 !

    elif args.video_source == 'blackmagic':
        video_src = """
            decklinkvideosrc {attribs} !
                {monitor}
		videoconvert !
                videorate !
                videoscale !
            """
                # yadif !

    elif args.video_source == 'png':
        video_src = """
            multifilesrc {attribs}
                loop=1
                caps="image/png" !
            pngdec !
            videoscale !
                {monitor}
            videoconvert !
            """

    elif args.video_source == 'test':

        # things to render as text ontop of test video
        d['hostname'] = socket.gethostname()
        d['videocaps'] = videocaps

        video_src = """
            videotestsrc name=videosrc {attribs} !
                clockoverlay text="Source:{hostname}\nCaps:{videocaps}" 
                    halignment=left line-alignment=left !
                {monitor}
            """

    video_src = video_src.format( **d )

    video_src += videocaps + "!\n"

    return video_src

def mk_audio_src(args, audiocaps):

    d={ 'attribs': args.audio_attribs }

    if args.audio_source in [ 'dv', 'hdv' ]:
        # this only works if video is from DV also.
        # or some gst source that gets demux ed
        audio_src = """
            demux. !
                audioconvert !
                """

    elif args.audio_source == 'pulse':
        audio_src = """
                pulsesrc {attribs} name=audiosrc !
                """

    elif args.audio_source == 'alsa':
        audio_src = """
                alsasrc {attribs} name=audiosrc !
                """

    elif args.audio_source == 'blackmagic':
        audio_src = """
            decklinkaudiosrc {attribs} !
            """

    elif args.audio_source == 'test':
        audio_src = """
            audiotestsrc {attribs} name=audiosrc freq=330 !
            """
    audio_src = audio_src.format(**d)
        
    audio_src += audiocaps + "!\n"

    return audio_src

def mk_client(core_ip,port):

    client = "tcpclientsink host={host} port={port}".format(
            host=core_ip, port=port)

    return client


def mk_pipeline(args, server_caps, core_ip):

    video_src = mk_video_src(args, server_caps['videocaps'])
    audio_src = mk_audio_src(args, server_caps['audiocaps'])
    
    client = mk_client(core_ip,args.port)

    pipeline = """
    {video_src}
     mux.
    {audio_src}
     mux.
            matroskamux name=mux !
    {client}
    """.format( video_src=video_src, audio_src=audio_src, client=client )

    # remove blank lines to make it more human readable
    while "\n\n" in pipeline:
        pipeline = pipeline.replace("\n\n","\n")

    print(pipeline)

    if args.debug:
        gst_cmd = "gst-launch-1.0 {}".format(pipeline)

        # escape the ! because  
        # asl2: ! is interpreted as a command history metacharacter
        gst_cmd = gst_cmd.replace("!"," \! ")

        # remove all the \n to make it easy to cut/paste into shell
        gst_cmd = gst_cmd.replace("\n"," ")
        while "  " in gst_cmd:
            gst_cmd = gst_cmd.replace("  "," ")
        print("-"*78)
        print(gst_cmd)
        print("-"*78)

    return pipeline

def get_server_caps(core_ip):

    # establish a synchronus connection to server
    Connection.establish(core_ip) 

    # fetch config from server
    server_config = Connection.fetchServerConfig()

    # Pull out the configs relevant to this client
    server_caps = {
        'videocaps': server_config['mix']['videocaps'],
        'audiocaps': server_config['mix']['audiocaps']
        }

    return server_caps

def get_clock(core_ip, core_clock_port=9998):

    clock = GstNet.NetClientClock.new( 'voctocore', 
            core_ip, core_clock_port, 0)

    print('obtained NetClientClock from host: {ip}:{port}'.format(
        ip=core_ip, port=core_clock_port) )

    print('waiting for NetClientClock to sync…')
    clock.wait_for_sync(Gst.CLOCK_TIME_NONE)

    return clock


def run_pipeline(pipeline, clock):

    print('starting pipeline...')
    senderPipeline = Gst.parse_launch(pipeline)
    senderPipeline.use_clock(clock)
    src = senderPipeline.get_by_name('src')

    def on_eos(bus, message):
        print('Received EOS-Signal')
        sys.exit(1)

    def on_error(bus, message):
        print('Received Error-Signal')
        (error, debug) = message.parse_error()
        print('Error-Details: #%u: %s' % (error.code, debug))
        sys.exit(2)


    # Binding End-of-Stream-Signal on Source-Pipeline
    senderPipeline.bus.add_signal_watch()
    senderPipeline.bus.connect("message::eos", on_eos)
    senderPipeline.bus.connect("message::error", on_error)

    print("playing...")
    senderPipeline.set_state(Gst.State.PLAYING)
 
    mainloop = GObject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print('Terminated via Ctrl-C')

    print('Shutting down...')
    senderPipeline.set_state(Gst.State.NULL)
    print('Done.')

    return

def get_args():

    parser = argparse.ArgumentParser(
            description='''Vocto-ingest Client with Net-time support.
            Gst caps are retrieved from the server.
            Run without parameters: send test av to localhost:10000
            ''')
    
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help="Also print INFO and DEBUG messages.")

    parser.add_argument( '--video-source', action='store', 
            choices=[
                'dv', 'hdv', 'hdmi2usb', 'blackmagic',
                'ximage', 'png', 'test'], 
            default='test',
            help="Where to get video from")

    parser.add_argument( '--video-attribs', action='store', 
            default='',
            help="misc video attributes for gst")

    parser.add_argument( '--audio-source', action='store', 
            choices=['dv', 'alsa', 'pulse', 'blackmagic', 'test'], 
            default='test',
            help="Where to get audio from")

    parser.add_argument( '--audio-attribs', action='store', 
            default='',
            help="misc audio attributes for gst")

    parser.add_argument('-m', '--monitor', action='store_true',
            help="fps display sink")

    parser.add_argument( '--host', action='store', 
            default='localhost',
            help="hostname of vocto core")

    parser.add_argument( '--port', action='store', 
            default='10000',
            help="port of vocto core")

    parser.add_argument('--debug', action='store_true',
            help="debugging things, like dump a  gst-launch-1.0 command")

    args = parser.parse_args()

    return args

    
def main():
    
    args = get_args()
    core_ip = socket.gethostbyname(args.host)

    server_caps = get_server_caps(core_ip)
    pipeline = mk_pipeline(args, server_caps, core_ip )

    clock = get_clock(core_ip)

    run_pipeline(pipeline, clock)


if __name__ == '__main__':
    main()
