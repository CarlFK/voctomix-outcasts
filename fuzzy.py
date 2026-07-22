
import json

import logging

import time

from pprint import pprint

from voctocore_cmds import VocCmd

logger = logging.getLogger(__name__)


def get_sources(host):

    with VocCmd(host=host) as vc:
        ret = vc.vocto_io('get_config\n')

    logger.info(f"got: {ret}")

    cmd,conf = ret.split(' ',1)
    assert cmd == "server_config"

    conf = json.loads(conf)
    pprint(conf)

    pprint(conf.keys())
    sources = conf['mix']['sources'] # 'Gst,Test'
    pprint(sources)
    sources = sources.split(',')
    pprint(sources)

    transistions = conf['transitions']

    return (transistions, sources)

def cycle_sources(host, transitions, sources):

    with VocCmd(host=host) as vc:

        while True:

            errors=set()
            for i, transition in enumerate(transitions):
                for source_a in sources:
                    for source_b in sources:
                        if source_a != source_b:
                            cmd = f"transition {transition}({source_a},{source_b})"
                            cmd += "\n"
                            ret = vc.vocto_io(cmd)
                            print(ret)
                            rets = ret.split(' ',1)
                            if rets[0] == "error":
                                logger.info(f"appending: {transition}")
                                errors.add(transition)
                                break # can we break(2)?

                time.sleep(1)

            for error in errors:
                logger.info(f"deleting: {error}")
                del(transitions[error])

def log_setup(level):
    logging.basicConfig(
        format="{asctime} {funcName}:{lineno} {levelname}: {message}",
        datefmt="%H:%M:%S",
        level=level,
        style="{",
    )


if __name__=='__main__':
    log_setup(4)
    host="10.9.2.146"
    host="localhost"

    transistions, sources = get_sources(host)
    cycle_sources(host, transistions, sources)

