#!/usr/bin/env python3
"""
ingest.py: source client for Voctomix.

   Copyright: 2015-2020 Carl F. Karsten <carl@nextdayvideo.com>,
                        Ryan Verner <ryan@nextdayvideo.com.au>

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to
   deal in the Software without restriction, including without limitation the
   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
   sell copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.


Features:
    Retrieves audio and video-caps config from core.
      and client config
    Uses core's clock.
    Mix and match audio and video sources muxed into one stream.
    Can display video locally, including frame count and fps.
    Defaults to test audio and video sent to local core.
"""

import argparse
from pprint import pprint
import socket
import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
from gi.repository import Gst, GstNet, GObject, GLib

from lib.connection import Connection


def mk_video_src(args, videocaps):
    # make video source part of pipeline
    # args come from command line
    # videocaps come from voctocore

    if args.video_source == 'dv':
        video_src = """
            dv1394src name=videosrc {attribs} !
        dvdemux name=demux !
        queue max-size-time=4000000000 !
        dvdec !
            """

    elif args.video_source == 'hdv':
        video_src = """
            hdv1394src {attribs} name=videosrc !
        tsdemux !
        queue max-size-time=4000000000 !
        decodebin !
            """

    elif args.video_source == 'hdmi2usb':
        # https://hdmi2usb.tv
        # Note: this code works with 720p
        video_src = """
            v4l2src {attribs} name=videosrc !
                queue max-size-time=4000000000 !
        image/jpeg,width=1280,height=720 !
                jpegdec !
            """

    elif args.video_source == 'ximage':
        # startx=0 starty=0 endx=1919 endy=1079 !
        video_src = """
            ximagesrc {attribs} name=videosrc
                   use-damage=false !
            """

    elif args.video_source == 'blackmagic':
        video_src = """
            decklinkvideosrc name=videosrc {attribs} !
            """

    elif args.video_source == 'png':
        video_src = """
            multifilesrc {attribs}
                caps="image/png" !
            pngdec !
            """
        # tip: --video-attribs "loop=true"
        # tip: --video-attribs "location=sc1204a.png"

    elif args.video_source == 'file':
        video_src = """
            multifilesrc {attribs} !
            decodebin name=src
            src. !
            queue !
            """

    elif args.video_source == 'test':

        video_src = """
    videotestsrc name=videosrc {attribs} !
    """
        # things to render as text ontop of test video
        video_src += """
    clockoverlay
        text="Source: {hostname}\nCaps: {videocaps}\nAttribs: {attribs}\n"
        halignment=left line-alignment=left !
            """.format(hostname=socket.gethostname(),
                    videocaps=videocaps,
                    attribs=args.video_attribs)

    elif args.video_source == 'spacescope':
        # Stereo visualizer
        # pair up with test beep for a handy AV sync test.
        video_src = """
      audio_tee. ! queue !
    spacescope shader=none style=lines {attribs} !
           """

    if args.monitor:
        if args.debug:
            videosink="fpsdisplaysink"
        else:
            videosink="autovideosink"

        video_src += """
            tee name=t ! queue !
                    videoconvert ! {videosink} sync=false
                    t. ! queue !
            """.format(videosink=videosink)

    if args.video_elements:
        video_src += args.video_elements + " !\n"

    video_src += videocaps + " !\n"

    video_src = video_src.format(attribs=args.video_attribs)

    return video_src


def mk_audio_src(args, audiocaps):

    d = {
        'attribs': args.audio_attribs,
        'base_audio_attribs':
            'provide-clock=false slave-method=re-timestamp',
        'audiocaps': audiocaps,
    }

    if args.audio_source in ['dv', 'hdv']:
        # this only works if video is from DV also.
        # or some gst source that gets demux ed
        audio_src = """
            demux.audio !
                queue !
                """

    elif args.audio_source == 'file':
        # this only works if video is from ...
        # some gst source that gets demux ed, I guess.
        audio_src = """
        src. !
                queue !
                """

    elif args.audio_source == 'pulse':
        audio_src = """
                pulsesrc {attribs} {base_audio_attribs} name=audiosrc !
                queue max-size-time=4000000000 !
                """

    elif args.audio_source == 'alsa':
        audio_src = """
                alsasrc {attribs} {base_audio_attribs} name=audiosrc !
                queue max-size-time=4000000000 !
                """

    elif args.audio_source == 'blackmagic':
        audio_src = """
            decklinkaudiosrc name=audiosrc {attribs} !
            """

    elif args.audio_source == 'test':
        audio_src = """
            audiotestsrc wave=ticks freq=330 {attribs} name=audiosrc !
            """

    if args.audio_elements:
        audio_src += args.audio_elements + " !\n"

    audio_src += """
       {audiocaps} !
    tee name=audio_tee
      audio_tee. ! queue !
      """
    audio_src = audio_src.format(**d)

    return audio_src


def mk_client(core_ip, port):

    client = "tcpclientsink host={host} port={port}".format(
            host=core_ip, port=port)

    return client


def mk_pipeline(args, server_caps, core_ip):

    if args.src:
        src = args.src.format(**server_caps)

    else:
        video_src = mk_video_src(args, server_caps['videocaps'])
        audio_src = mk_audio_src(args, server_caps['audiocaps'])
        src =  """
            {video_src}
             mux.
            {audio_src}
             mux.
            matroskamux name=mux !
        """.format(video_src=video_src, audio_src=audio_src)

    client = mk_client(core_ip, args.port)

    pipeline = """
            {src}
    {client}
    """.format(src=src, client=client)

    # remove blank lines to make it more human readable
    while "\n\n" in pipeline:
        pipeline = pipeline.replace("\n\n", "\n")

    print(pipeline)

    if args.debug:
        # print something to run in a shell
        gst_cmd = "gst-launch-1.0 {}".format(pipeline)

        # escape the ! because bash
        # asl2: ! is interpreted as a command history metacharacter
        gst_cmd = gst_cmd.replace("!", " \! ")

        # remove all the \n to make it easy to cut/paste into shell
        gst_cmd = gst_cmd.replace("\n", " ")
        while "  " in gst_cmd:
            gst_cmd = gst_cmd.replace("  ", " ")
        print("-"*78)
        print(gst_cmd)
        print("-"*78)

    return pipeline

def get_server_conf(core_ip, source_id, args):

    # establish a synchronus connection to server
    conn = Connection(core_ip)

    # fetch config from server
    server_config = conn.fetch_config()

    # Pull out the configs relevant to this client
    server_conf = {
        'videocaps': server_config['mix']['videocaps'],
        'audiocaps': server_config['mix']['audiocaps']
        }

    if source_id is not None:

        # get conf from server for this source,
        d=server_config[source_id]
        if args.debug:
            pprint(d)

        # stomp all over command line values
        # this is backwards: command line should override conf file.
        for k in d:
            if args.debug:
                print('--{}="{}"'.format(k,d[k]))
            # python argparse converts a-b to a_b, so we will to too.
            args.__setattr__(k.replace("-", "_"),d[k])

    return server_conf, args


def get_clock(core_ip, core_clock_port=9998):

    clock = GstNet.NetClientClock.new(
        'voctocore', core_ip, core_clock_port, 0)

    print('obtained NetClientClock from host: {ip}:{port}'.format(
        ip=core_ip, port=core_clock_port))

    print('waiting for NetClientClock to sync...')
    clock.wait_for_sync(Gst.CLOCK_TIME_NONE)
    print('synced with NetClientClock.')

    return clock


def run_pipeline(pipeline, clock, audio_delay=0, video_delay=0):

    def on_eos(bus, message):
        print('Received EOS-Signal')
        sys.exit(0)

    def on_error(bus, message):
        print('Received Error-Signal')
        (error, debug) = message.parse_error()
        print('Error-Details: #%u: %s' % (error.code, debug))
        sys.exit(2)

    print('starting pipeline...')
    senderPipeline = Gst.parse_launch(pipeline)
    if clock is not None:
        senderPipeline.use_clock(clock)

    # Delay video/audio if required
    NS_TO_MS = 100000

    if video_delay > 0:
        print('Adjusting video sync: [{} milliseconds]'.format(video_delay))
        video_delay = video_delay * NS_TO_MS
        videosrc = senderPipeline.get_by_name('videosrc')
        videosrc.get_static_pad('src').set_offset(video_delay)

    if audio_delay > 0:
        print('Adjusting audio sync: [{} milliseconds]'.format(audio_delay))
        audio_delay = audio_delay * NS_TO_MS
        audiosrc = senderPipeline.get_by_name('audiosrc')
        audiosrc.get_static_pad('src').set_offset(audio_delay)

    # Binding End-of-Stream-Signal on Source-Pipeline
    senderPipeline.bus.add_signal_watch()
    senderPipeline.bus.connect("message::eos", on_eos)
    senderPipeline.bus.connect("message::error", on_error)

    print("playing...")
    senderPipeline.set_state(Gst.State.PLAYING)

    mainloop = GLib.MainLoop()
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
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='''Vocto-ingest Client with Net-time support.
            Gst caps are retrieved from the server.
            Run without parameters: send test av to localhost:10000
            ''')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="Also print INFO and DEBUG messages.")

    parser.add_argument('--source-id', action='store',
            help="get config from server using this id.")

    parser.add_argument(
        '--src', action='store', default='',
        help="gst source pipeline")

    parser.add_argument(
        '--video-source', action='store',
        choices=[
            'dv', 'hdv', 'udp_h264', 'hdmi2usb', 'blackmagic',
            'ximage', 'png', 'file', 'test', 'spacescope'],
        default='test',
        help="Where to get video from")

    parser.add_argument(
        '--video-attribs', action='store', default='',
        help="misc video attributes for gst")

    parser.add_argument(
        '--video-delay', action='store',
        default=0,
        type=int,
        help="delay video by this many milliseconds")

    parser.add_argument(
        '--video-elements', action='store',
        default='videoconvert ! deinterlace ! videorate ! videoscale',
        help="gst video elments after src.")

    parser.add_argument(
        '--audio-source', action='store',
        choices=['dv', 'hdv', 'file',
            'alsa', 'pulse', 'blackmagic', 'test', ],
        default='test',
        help="Where to get audio from")

    parser.add_argument(
        '--audio-attribs', action='store',
        default='',
        help="misc audio attributes for gst")

    parser.add_argument(
        '--audio-delay', action='store',
        default=0,
        type=int,
        help="delay audio by this many milliseconds")

    parser.add_argument(
        '--audio-elements', action='store',
        default="audioconvert ! audioresample ! audiorate",
        help="gst audio elments after src.")

    parser.add_argument(
        '-m', '--monitor', action='store_true',
        help="local display sink")

    parser.add_argument(
        '--host', action='store',
        default='localhost',
        help="hostname of vocto core")

    parser.add_argument(
        '--port', action='store',
        default='10000',
        help="port of vocto core")

    parser.add_argument(
        '--no-clock', action='store_true',
        help="Don't use core's clock. (danger)")

    parser.add_argument(
        '--debug', action='store_true',
        help="debugging things, like dump a  gst-launch-1.0 command")

    args = parser.parse_args()

    return args


def main():

    Gst.init([])

    args = get_args()
    core_ip = socket.gethostbyname(args.host)

    server_caps, args = get_server_conf(core_ip, args.source_id, args)

    pipeline = mk_pipeline(args, server_caps, core_ip)

    if args.no_clock:
        clock = None
    else:
        clock = get_clock(core_ip)

    run_pipeline(pipeline, clock, args.audio_delay, args.video_delay)


if __name__ == '__main__':
    main()
