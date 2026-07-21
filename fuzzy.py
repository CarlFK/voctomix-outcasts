
import json

import logging

import time

from pprint import pprint

from voctocore_cmds import VocCmd

logger = logging.getLogger(__name__)


def get_sources():

    with VocCmd() as vc:
        ret = vc.vocto_io(b'get_config\n')

    logger.info(f"got: {ret}")

    ret = ret[14:]
    sc = json.loads(ret)
    pprint(sc)

    sources = sc['mix']['sources'] # 'Gst,Test'
    pprint(sources)
    sources = sources.split(',')
    pprint(sources)

    return sources

def cycle_sources(sources):

    with VocCmd() as vc:

        while True:

            for source in sources:
                cmd = f"transition fs({source})"
                cmd += "\n"
                cmd = cmd.encode()
                ret = vc.vocto_io(cmd)
                print(ret)
                time.sleep(1)


def log_setup(level):
    logging.basicConfig(
        format="{asctime} {funcName}:{lineno} {levelname}: {message}",
        datefmt="%H:%M:%S",
        level=level,
        style="{",
    )


if __name__=='__main__':
    log_setup(4)
    sources = get_sources()
    cycle_sources(sources)

