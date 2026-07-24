import json
import logging
import time

from pprint import pprint

from voctocmd import VocCmd, get_args, log_setup

logger = logging.getLogger(__name__)


def get_conf(vc):

    ret = vc.vocto_io("get_config")

    logger.debug(f"got: {ret}")

    cmd, conf = ret.split(" ", 1)
    assert cmd == "server_config"

    conf = json.loads(conf)

    return conf



def cycle_sources(vc, transitions, sources):

        while True:

            errors = set()
            for i, transition in enumerate(transitions):
                for source_a in sources:
                    for source_b in sources:
                        if source_a != source_b:
                            cmd = f"transition {transition}({source_a},{source_b})"
                            ret = vc.vocto_io(cmd)
                            logger.info(f"core says: {ret}")
                            rets = ret.split(" ", 1)
                            if rets[0] == "error":
                                logger.info(f"appending: {transition}")
                                errors.add(transition)
                                break  # can we break(2)?
                            time.sleep(1)

            # remove things that core says "error"
            for error in errors:
                logger.info(f"deleting: {error}")
                del transitions[error]


def main():

    args = get_args()

    log_setup(args.verbose)
    log_setup(args.verbose, logger)

    # I have plans for this...  maybe.
    # cmds = args.cmds
    # if args.file:
    #    cmds.extend(read_cmds(args.file))

    with VocCmd(args.host, args.port, args.timeout, args.wait_for_core) as vc:
        vc.delay = args.delay

        conf = get_conf(vc)
        logger.debug(f"{conf.keys()}")

        sources = conf["mix"]["sources"]  # 'Gst,Test'
        logger.debug(f"{sources}")
        sources = sources.split(",")
        logger.debug(f"{sources}")

        transistions = conf["transitions"]

        cycle_sources(vc, transistions, sources)


if __name__ == "__main__":
    main()
