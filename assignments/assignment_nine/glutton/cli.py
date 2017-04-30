#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

CLI for glutton.py

"""

from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import time

from glutton import Hungery

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def main(args):
    """ Setup logs, gather args, and start the mining.

    """

    args = parse_args(args)
    setup_logs(args.loglevel)

    _logger.info("Starting main()")
    try:
        glutton = Hungery(args.threads,
                          args.out,
                          args.pickle,
                          args.new,
                          args.entries)

        #  Cook up and eat the data
        glutton.eat(args.uris)
    except KeyboardInterrupt:
        _logger.info("Recieved Keyboard Interrupt")
        print("[*] Keyboard Interrupt... Aborting")

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
        description="Fetch blog data.")
    logs = parser.add_mutually_exclusive_group()

    parser.add_argument(
        '-t',
        '--threads',
        nargs='?',
        type=int,
        default=1,
        const=1,
        help="Number of threads to use",
        action='store')
    parser.add_argument(
        '-u',
        '--uris',
        nargs='+',
        type=str,
        help="Direct link to a feed to process",
        action='store')
    parser.add_argument(
        '-e',
        '--entries',
        nargs='?',
        type=int,
        default=100,
        const=100,
        help="Limit the number of feed entries to process",
        action='store')
    parser.add_argument(
        '-o',
        '--out',
        type=str,
        default='../data/wordcount.dat',
        help="Where to store the wordcount data.",
        action='store')
    parser.add_argument(
        '-p',
        '--pickle',
        type=str,
        default='../data/word_counts.pkl',
        help="Where to store the pickled word matrix.",
        action='store')
    parser.add_argument(
        '-n',
        '--new',
        default=False,
        help="Fetch new list of URIs.",
        action='store_true')
    logs.add_argument(
        '-v',
        '--verbose',
        nargs='?',
        dest='loglevel',
        help='set loglevel to DEBUG',
        default=logging.INFO,
        const=logging.DEBUG)

    args = parser.parse_args(args)
    if not args.uris:
        parser.error('\n[*] No URI(s) provided.')

    return args


def setup_logs(loglevel=logging.INFO):
    """ Set up logger to be used between all modules.

    Set logging root and file handler configuration to default to
    ``DEBUG`` and write output to ``main.log``. Set console
    handler to default to ``ERROR``.

    """
    logfile = '../main.log'
    with open(logfile, 'w') as log:
        log.write('Init Logger')

    logging.basicConfig(level=loglevel, filename='../main.log',
                        filemode='a')
    _logger.setLevel(loglevel)

    # create file handler which logs messages
    fh = logging.FileHandler('../main.log')
    fh.setLevel(loglevel)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


if __name__ == "__main__":

    start = time.time()
    main(sys.argv[1:])
    print("[*] Ran for {} seconds".format(time.time() - start))
    sys.exit(0)
