#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" words.py

Parse a HTML page for all visible text

"""

from __future__ import division, print_function, absolute_import

import re
import sys
import logging
import codecs

from os.path import join
from threading import Thread
from queue import Queue

try:
    import lxml
    import magic
    import future
    from bs4 import BeautifulSoup as bs
except ImportError:
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def parse(thread, q, output, in_dir):
    """ Parse a HTML document for all visible text

    """
    while True:

        path = q.get()
        _logger.debug("[*] Thread {} parsing file {}".format(thread, path))

        mime = magic.from_file(path, mime=True)
        if path[-5] != ".html" or mime == 'application/pdf':
            _logger.debug("[*] Thread {}: file {} is not HTML best guess is {}"\
                    .format(thread, path, mime))
            q.task_done()

        with codecs.open(path, 'r', encoding='utf-8', errors='ignore') as html:
            try:
                soup = bs(html, 'lxml')
#            except html.parser.HTMLParseError as e:
#                _logger.error("[*] BeautifulSoup Python html.parser failed \
#                        for file {} with error:\n".format(path, e))
            except RuntimeError as e:
                _logger.error("[*] BeautifulSoup failed parsing \
                        file {} with error:\n".format(path, e))
                print(e)
                sys.exit(1)

            [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
            [s.extract() for s in soup() if re.match('<!--.*-->', str(s))]
            visible_texts = soup.get_text()

        with open(join(output, path[len(in_dir):-5] + '.txt'), 'w') as out_file:
            out_file.write(visible_texts)

        _logger.debug("[*] Thread {} finished parsing {}".format(thread, path))
        print("[*] Thread {} finished parsing {}".format(thread, path))

        q.task_done()


def sweeper(paths, threads, output, in_dir):
    """ Start threads, put paths in queue

    """
    q = Queue()

    if threads > 1:
        print("[*] Spinning up with {} threads\n".format(threads))
    else:
        print("[*] Spinning up with {} thread\n".format(threads))

    for thread_id in range(threads):
        worker = Thread(target=parse, args=(thread_id, q, output, in_dir))
        worker.setDaemon(True)
        worker.start()
    for path in paths:
        q.put(path)
    q.join()
