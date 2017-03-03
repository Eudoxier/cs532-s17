#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

Main program for the PDF web crawler. For example.

TODO:
    * Implement -f flag for working from a file instead of stream
    * Implement -q to suppress output to STDOUT

"""

from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import time

from miner import Miner

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def main(args):
    """ Setup logs, gather args, and start the mining.

    """
    setup_logs()
    _logger.info("Starting main()")

    args = parse_args(args)

    if args.infile:
        miner = Miner(args.keywords, args.count, args.infile)
    else:
        miner = Miner(args.keywords, args.count)
        miner.run()

    _logger.info("All done, shutting down.")
    logging.shutdown()


def parse_args(args):
    """ Parse command line parameters.

    :return: command line parameters as :obj:`airgparse.Namespace`
    Args:
        args ([str]): List of strings representing the command line arguments.

    Returns:
        argparse.Namespace: Simple object with a readable string
        representation of the argument list.

    """
    parser = argparse.ArgumentParser(
        description="Filter streaming tweets by keywords.")

    parser.add_argument(
        '-f',
        '--infile',
        type=str,
        default=None,
        help="Input file instead of stream.",
        action='store'),
    parser.add_argument(
        '-c',
        '--count',
        default=1000,
        type=int,
        help="Number of tweets to get with the filters applied.",
        action='store'),
    parser.add_argument(
        '-q',
        '--quiet',
        default=False,
        help="Suppress output.",
        action='store_true'),
    parser.add_argument(
        '-k',
        '--keys',
        nargs=1,
        type=str,
        default="auth.keys",
        help="File containing OAuth twitter credentials.",
        action='store'),
    parser.add_argument(
        'keywords',
        nargs='+',
        type=str,
        help="Keywords to filter tweets with.")

    return parser.parse_args(args)


def setup_logs():
    """ Set up logger to be used between all modules.

    Set logging root and file handler configuration to default to
    ``DEBUG`` and write output to ``main.log``. Set console
    handler to default to ``ERROR``.

    """
    logging.basicConfig(level=logging.INFO, filename='../main.log',
                        filemode='w')
    _logger.setLevel(logging.INFO)

    # create file handler which logs messages
    fh = logging.FileHandler('../main.log')
    fh.setLevel(logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


if __name__ == "__main__":

    start = time.time()
    main(sys.argv[1:])
    print("[*] Ran for {} seconds".format(time.time() - start))
    _logger.info("[*] Ran for {} seconds".format(time.time() - start))
    sys.exit(0)
