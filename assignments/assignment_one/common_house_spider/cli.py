#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

Main program for the PDF web crawler. For example.

"""

from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import time
import doctest


from crawler import sweeper

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def main(args):
    """ Setup logs, gather args, and start the crawl.

    """
    setup_logs()
    _logger.debug("Starting main()")

    args = parse_args(args)
    addresses = args.addresses 

    if args.infile:
        for address in args.infile:
            addresses.append(address.strip())

    print("[*] Crawling pages: {}".format(addresses))

    try:
        sweeper(addresses, args.threads)
    except KeyboardInterrupt:
        sys.exit(2)

    _logger.debug("All done, shutting down.")
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
        description="Find all PDF links from a given webpage.")

    parser.add_argument(
        '-t',
        '--threads',
        nargs='?',
        type=int,
        default=1,
        const=1,
        help="Number of threads to use",
        action='store'),
    parser.add_argument(
        '-f',
        '--infile',
        nargs='?',
        type=argparse.FileType('r'),
        default=None,
        help="Read addresses to search from file.",
        action='store'),
    parser.add_argument(
        'addresses',
        nargs='+',
        type=str,
        help="Webpage addresses")

    return parser.parse_args(args)


def setup_logs():
    """ Set up logger to be used between all modules.

    Set logging root and file handler configuration to default to
    ``DEBUG`` and write output to ``main.log``. Set console
    handler to default to ``ERROR``.

    """
    logging.basicConfig(level=logging.DEBUG, filename='../main.log',
                        filemode='w')
    _logger.setLevel(logging.DEBUG)

    # create file handler which logs messages
    fh = logging.FileHandler('../main.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


if __name__ == "__main__":

    start = time.time()
    main(sys.argv[1:])
    print("[*] PDF links discovered in {} seconds".format(time.time() - start))
    sys.exit(0)
