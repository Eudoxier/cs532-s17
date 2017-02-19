#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

Main program for the word soup.

"""

from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import time

from os import listdir
from os.path import isfile, isdir, join

from words import sweeper

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def main(args):
    """ Setup logs, gather args, and start the search.

    """
    setup_logs()
    _logger.debug("Starting main()")

    args = parse_args(args)

    if args.infile is not None:
        path = args.infile
        if isfile(path):
            sweeper(path, args.threads)
        else:
            _logger.error("[*] Error: file {} not found".format(path))
            print("[*] Aborting: file {} not found.".format(path))
            sys.exit(1)

    elif args.directory is not None:
        path = args.directory
        if isdir(path):
            paths = [f for f in listdir(path) if isfile(join(path, f))]
            sweeper(paths, args.threads)
        else:
            _logger.error("[*] Error: directory {} not found".format(path))
            print("[*] Aborting: directory {} not found.".format(path))
            sys.exit(1)

    else:
        _logger.error("Main fell through.")
        print("[*] Error: Something went terribly wrong "
              "because this message is impossible to reach."
             )
        sys.exit(1)

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
    source=parser.add_mutually_exclusive_group()
    parser.add_argument(
        '-t',
        '--threads',
        nargs='?',
        type=int,
        default=1,
        const=1,
        help="Number of threads to use",
        action='store'),
    source.add_argument(
        '-d',
        '--directory',
        type=str,
        default=None,
        help="Path to a directory with files to parse",
        action='store'),
    source.add_argument(
        '-f',
        '--infile',
        nargs='?',
        type=str,
        default=None,
        help="Path to a single file to parse",
        action='store')

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
    print("[*] Finished in {} seconds".format(time.time() - start))
    sys.exit(0)
