#!/usr/bin/env python3

import asyncio
import json


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
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))

        if message == 'get_config\n':
            self.transport.write(
                'server_config {}\n'
                .format(json.dumps(CONFIG)).encode('utf-8')
            )


def main():
    loop = asyncio.get_event_loop()
    coro = loop.create_server(VoctoMixProtocol, '0.0.0.0', 9999)
    server = loop.run_until_complete(coro)

    print('Listening on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()
