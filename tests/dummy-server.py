#!/usr/bin/env python3

import asyncio
import json

import gbulb
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
from gi.repository import Gst, GstNet


CONFIG = {
    'mix': {
        'videocaps': 'video/x-raw,format=I420,width=1280,height=720,'
                     'framerate=30000/1001,pixel-aspect-ratio=1/1',
        'audiocaps': 'audio/x-raw,format=S16LE,channels=2,'
                     'layout=interleaved,rate=48000',
    }
}


class VoctoMixProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Control connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()

        if message == 'get_config\n':
            self.transport.write(
                'server_config {}\n'
                .format(json.dumps(CONFIG)).encode('utf-8')
            )
        else:
            print('Unknown control command: {!r}'.format(message))


class NetTimeClock(object):
    def __init__(self):
        clock = Gst.SystemClock().obtain()
        self.ntp = GstNet.NetTimeProvider.new(clock, '0.0.0.0', 9998)
        print('Clock listening on UDP port {}'.format(9998))

    def stop(self):
        del self.ntp  # FIXME: How is one supposed to shut it down?


class VideoSink(object):
    def __init__(self):
        print('Listening for stream on port {}'.format(10000))
        self.pipeline = Gst.parse_launch(
            'tcpserversrc host=0.0.0.0 port=10000 ! '
            'decodebin ! videoconvert ! xvimagesink'
        )
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)


def main():
    Gst.init([])
    gbulb.install()

    clock = NetTimeClock()
    sink = VideoSink()

    loop = asyncio.get_event_loop()
    coro = loop.create_server(VoctoMixProtocol, '0.0.0.0', 9999)
    server = loop.run_until_complete(coro)

    print('Control server listening on {}'.format(
          server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    clock.stop()
    sink.stop()
    try:
        loop.run_until_complete(server.wait_closed())
    except KeyboardInterrupt:
        # Gets carried through to here under glib main loop, for some reason...
        pass
    loop.close()

if __name__ == '__main__':
    main()
