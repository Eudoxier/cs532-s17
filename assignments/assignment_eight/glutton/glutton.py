#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" glutton.py

I eat blog feeds.

"""

from __future__ import division, print_function, absolute_import

import re
import sys
import logging

from threading import Thread
from queue import Queue

try:
    import feedparser
    import requests
    import validators
    from bs4 import BeautifulSoup as bs
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
    def __init__(self, n_threads, blog_uri_file, feed_uri_file, fetch_new_uris):
        self.n_threads = n_threads
        self.fetch_new_uris = fetch_new_uris
        self.blog_uri_file = blog_uri_file
        self.blog_uris = []
        self.feed_uri_file = feed_uri_file
        self.feed_uris = []

    def run(self):
        """ Stack URIs in Queue to be processed.

        """

        if not self.fetch_new_uris:
            self.read_blog_uris()
            self.read_feed_uris()
            if len(self.feed_uris) != 100:
                print("[*] Did not read enough feed URIs...")
                print("[*] Attempting blog URI fallback...")
                if len(self.blog_uris) != 100:
                    print("[*] Did not read enough blog URIs...")
                    print("[*] Fetching new URIs")

        if self.fetch_new_uris or len(self.feed_uris) != 100:
            self.get_random_uris()
            self.write_blog_uris()

            self.multitask(self.get_feed_uris)
            self.write_feed_uris()

        glutton = Glutton(self.n_threads, self.feed_uris)
        glutton.run()

    def multitask(self, function, *args, **kwargs):
        """ Variable function multiprocessing.

        """
        queue = Queue()
        for thread_id in range(self.n_threads):
            worker = Thread(target=function,
                            args=(thread_id, queue, args, kwargs))
            worker.setDaemon(True)
            worker.start()
        for uri in self.blog_uris:
            queue.put(uri)
        queue.join()

    def get_random_uris(self):
        """ Fetch n random blog URIs.

        """

        _logger.info("Fetching random URIs")

        # Add the two non-random URIs requested
        non_random_uris = ['http://f-measure.blogspot.com/',
                           'http://ws-dl.blogspot.com/']
        self.blog_uris += non_random_uris

        while len(self.blog_uris) < 100:
            try:
                request_uri = ('http://www.blogger.com/next-blog?navBar=true&bl'
                               'ogID=3471633091411211117')
                response = get_response(request_uri)
                if response is not None:
                    self.blog_uris.append(response.url)
                    self.blog_uris = list(set(self.blog_uris))
                    print("[*] Collected {} blog URIs"
                          .format(len(self.blog_uris)))
            except requests.exceptions.RequestException as error:
                _logger.warning('[*] Request Failed\n{}'.format(error))

        for uri in non_random_uris:
            assert uri in self.blog_uris

    def read_blog_uris(self):
        """ Read saved blog URIs from file.

        """
        _logger.info("Reading blog URIs from file {}"
                     .format(self.blog_uri_file))
        with open(self.blog_uri_file, 'r') as infile:
            self.blog_uris = [line.strip() for line in infile]

    def write_blog_uris(self):
        """ Save blog URIs to file.

        """
        _logger.info("Writing blog URIs to {}".format(self.blog_uri_file))
        with open(self.blog_uri_file, 'w') as outfile:
            for line in self.blog_uris:
                outfile.write("{}\n".format(line))

    def get_feed_uris(self):
        """ Parse feed URIs out of HTML pages.

        """
        _logger.info("Getting blog feed URIs")

        for uri in self.blog_uris:

            print("[*] Looking for feed URI for {}...".format(uri))
            _logger.debug("Getting RSS/Atom feed URI from {}".format(uri))
            response = get_response(uri)
            html = response.html

            try:
                soup = bs(html, 'lxml')
            except RuntimeError as error:
                _logger.warning("[*] BeautifulSoup failed parsing \
                                file {} with error:\n{}".format(uri, error))

            feed_rss_uri = soup.find('link', type='application/rss+xml')
            feed_atom_uri = soup.find('link', type='application/atom+xml')
            if feed_rss_uri is not '':
                _logger.debug("Adding RSS URI {}".format(feed_rss_uri))
                self.feed_uris.append(feed_rss_uri)
            elif feed_atom_uri is not '':
                _logger.debug("Adding Atom URI {}".format(feed_atom_uri))
                self.feed_uris.append(feed_atom_uri)
            else:
                _logger.warning("Failed to find feed URI for {}".format(uri))
                print("[*] Failed to find feed URI for {}...".format(uri))

    def read_feed_uris(self):
        """ Read feed URIs from file.

        """
        _logger.info("Reading feed URIs from file {}"
                     .format(self.blog_uri_file))
        with open(self.feed_uri_file, 'r') as infile:
            self.feed_uris = [line.strip() for line in infile]

    def write_feed_uris(self):
        """ Save blog URIs to file.

        """
        _logger.info("Writing feed URIs to {}".format(self.feed_uri_file))
        with open(self.feed_uri_file, 'w') as outfile:
            for line in self.feed_uris:
                outfile.write("{}\n".format(line))


class Glutton():
    """ I eat the blog data.

    """
    def __init__(self, n_threads, uris):
        self.n_threads = n_threads
        self.uris = uris
        self.uris_processed = 0

    def run(self):
        """ The Gluttons main loop.

        """
        if self.n_threads > 1:
            print("[*] Spinning up with {} threads".format(self.n_threads))
            _logger.info("[*] Spinning up with {} threads"
                         .format(self.n_threads))
        else:
            print("[*] Spinning up with {} thread".format(self.n_threads))
            _logger.info("[*] Spinning up with {} thread"
                         .format(self.n_threads))

        self.multitask(self.process_uri)

    def multitask(self, function, *args, **kwargs):
        """ Variable function multiprocessing.

        """
        queue = Queue()
        for thread_id in range(self.n_threads):
            worker = Thread(target=function,
                            args=(thread_id, queue, args, kwargs))
            worker.setDaemon(True)
            worker.start()
        for uri in self.uris:
            queue.put(uri)
        queue.join()

    def process_uri(self, thread_id, queue, *args, **kwargs):
        """ Process URIs.

        """
        while True:
            uri = queue.get()
            _logger.info("Thread {} Processing URI {}".format(thread_id,
                                                              uri))
            self.get_word_counts(thread_id, uri)

            self.uris_processed += 1
            print("[*] Processed URI number {}".format(self.uris_processed))
            queue.task_done()

    def get_word_counts(self, thread_id, uri):
        """ Parse HTML for all visible text

        """
        feed_dict = feedparser.parse(uri)
        _logger.debug("{}".format(feed_dict.feed))
        word_counts = {}

        for entry in feed_dict.entries:
            _logger.debug("Thread {} Processing blog entry {}"
                          .format(thread_id, entry.title))
            if 'summary' in entry:
                summary = entry.summary
            else:
                summary = entry.description

            words = self.get_words(thread_id, uri,
                                   (entry.title + ' ' + summary))
            for word in words:
                _logger.debug("Thread {} found instance of word {} in {}"
                              .format(thread_id, word, entry.title))
                word_counts.setdefault(word, 0)
                word_counts[word] += 1

        try:
            feed_dict.feed.title
        except AttributeError as error:
            _logger.warning("URI {} has no blog title\n{}".format(uri, error))

        return(getattr(feed_dict.feed, 'title', 'Unknown'), word_counts)

    def get_words(self, thread_id, uri, html):
        """ Parse a HTML document for all visible text

        """

        _logger.debug("[*] Thread {} parsing uri {} HTML"
                      .format(thread_id, uri))

        try:
            soup = bs(html, 'lxml')
        except RuntimeError as error:
            _logger.warning("[*] BeautifulSoup failed parsing \
                            file {} with error:\n".format(uri, error))

        [s.extract() for s in soup(
            ['style', 'script', '[document]', 'head', 'title'])]
        [s.extract() for s in soup() if re.match('<!--.*-->', str(s))]
        visible_texts = soup.get_text()

        _logger.debug("[*] Thread {} finished parsing {}"
                      .format(thread_id, uri))

        _logger.debug(visible_texts)
        return visible_texts


def get_response(uri, tries=5, tolerant=False):
    """ Fetch page

    """
    headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64; \
            rv:45.0) Gecko/20100101 Firefox/45.0"}

    success = False
    for attempt in range(tries):
        try:
            uri = normalize_uri(uri)
            response = requests.get(uri, headers=headers, timeout=2)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            _logger.debug("[*] Request timed out for {} retrying".format(uri))
            continue
        except requests.exceptions.TooManyRedirects as error:
            print("[*] URI {} is bad".format(uri))
            _logger.debug("URI {} is bad\n{}".format(uri, error))
            if tolerant:
                continue
            else:
                break
        except requests.exceptions.RequestException as error:
            print("[*] URI {} is bad".format(uri))
            _logger.debug("URI {} is bad\n{}".format(uri, error))
            if tolerant:
                continue
            else:
                break
        success = True

    if success:
        _logger.debug("Fetched URI {} data".format(uri))
    else:
        print("[*] WARNING: URI {} has timed out".format(uri))
        _logger.warning("URI {} has timed out".format(uri))
        return None

    return response


def normalize_uri(uri):
    """ Ensure URI starts with http:// replace bad characters and add feed.

    """
    if not validators.url(uri):
        uri = uri.strip("https://")
        uri = "https://" + uri
        uri = uri.replace(' ', '%20')

    return uri
