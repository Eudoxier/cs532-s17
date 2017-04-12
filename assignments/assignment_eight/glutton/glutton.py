#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" glutton.py

I eat blog feeds.

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


class Chef():
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

        if not self.fetch_uris:
            self.read_uris()

        if self.fetch_uris or len(self.uris) != 100:
            self.get_random_uris()
            self.write_uris()

        if self.n_threads > 1:
            print("[*] Spinning up with {} threads\n".format(self.n_threads))
        else:
            print("[*] Spinning up with {} thread\n".format(self.n_threads))

        queue = Queue()
        for thread_id in range(self.n_threads):
            glutton = Glutton(thread_id, queue)
            worker = Thread(target=glutton.process_uri,
                            args=())
            worker.setDaemon(True)
            worker.start()
        for uri in self.uris:
            queue.put(uri)
        queue.join()

    def get_random_uris(self):
        """ Fetch n random blog URIs.

        """

        _logger.info("Fetching random URIs")

        # Add the two non-random URIs requested
        non_random_uris = ['http://f-measure.blogspot.com/',
                           'http://ws-dl.blogspot.com/']
        self.uris += non_random_uris

        while len(self.uris) < 100:
            try:
                request_uri = ('http://www.blogger.com/'
                               'next-blog?navBar=true&blogID='
                               '3471633091411211117')
                response = get_response(request_uri)
                self.uris.append(response.url)
                self.uris = list(set(self.uris))
            except requests.exceptions.RequestException as error:
                _logger.warning('[*] Request Failed\n{}'.format(error))

        for uri in non_random_uris:
            assert uri in self.uris

    def read_uris(self):
        _logger.info("Reading URIs from file {}".format(self.uri_file))
        with open(self.uri_file, 'r') as infile:
            self.uris = [line.strip() for line in infile]

    def write_uris(self):
        _logger.info("Writing URIs to {}".format(self.uri_file))
        with open(self.uri_file, 'w') as outfile:
            for line in self.uris:
                outfile.write("{}\n".format(line))


class Glutton():
    """ I eat the blog data.

    """
    def __init__(self, thread_id, queue):
        self.thread_id = thread_id
        self.queue = queue

    def process_uri(self):
        """ Process URIs.

        """
        while True:
            uri = self.queue.get()
            _logger.info("Thread {} Processing URI {}".format(self.thread_id,
                                                              uri))
            self.queue.task_done()

    def parse_feed(self, uri):
        """ Parse a blog RSS or Atom feed.

        """
        pass


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
