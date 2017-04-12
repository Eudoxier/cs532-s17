#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" miner.py

Get links from twitter.

"""

from __future__ import division, print_function, absolute_import

import sys
import logging


from threading import Thread
from queue import Queue

try:
    import feedparser
    import requests
    import validators
except ImportError as error:
    print("[*] Error: {}".format(error))
    print("[*] Please run `pip install -r requrements.txt` "
          "before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


class Producer():
    """ Fetches URIs to be consumed.

    """
    def __init__(self, n_threads, uri_file, fetch_uris):
        self.n_threads = n_threads
        self.fetch_uris = fetch_uris
        self.uri_file = uri_file

        self.uris = []

    def run(self):
        """ Stack URIs in Queue to be processed.

        """
        queue = Queue()
        self.uris = self.get_random_uris()

        if self.n_threads > 1:
            print("[*] Spinning up with {} threads\n".format(self.n_threads))
        else:
            print("[*] Spinning up with {} thread\n".format(self.n_threads))

        for thread_id in range(self.n_threads):
            consumer = Consumer(thread_id, queue)
            worker = Thread(target=consumer.run(), args=(thread_id, queue))
            worker.setDaemon(True)
            worker.start()
        for uri in self.uris:
            queue.put(uri)
        queue.join()

    def get_random_uris(self):
        """ Fetch n random blog URIs.

        """
        while len(self.uris) < 98:
            try:
                request_uri = ('http://www.blogger.com/'
                            'next-blog?navBar=true&blogID=3471633091411211117')
                response = get_response(request_uri)
                self.uris.append(response.url)
            except:
                _logger.info('[*] Request Failed')


class Consumer():
    """ Process the URIs.

    """
    def __init__(self, thread_id, queue):
        self.thread_id = thread_id
        self.queue = queue

    def run(self):
        """ Process a URI.

        """
        uri = self.queue.get()
        print(uri)
        self.queue.task_done()


def get_response(address):
    """ Fetch page

    """
    headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64; \
            rv:45.0) Gecko/20100101 Firefox/45.0"}

    address = normalize_url(address)
    response = requests.get(address, headers=headers, timeout=0.3)
    response.raise_for_status()

    return response


def normalize_url(url):
    """ Ensure URL starts with http:// and replace bad characters

    """
    if not validators.url(url):
        url = url.strip("https://")
        url = "https://" + url
        url = url.replace(' ', '%20')

    return url
