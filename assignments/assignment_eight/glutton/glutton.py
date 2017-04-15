#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" glutton.py

I eat blog feeds.

"""

from __future__ import division, print_function, absolute_import

import re
import sys
import logging
import pickle

from threading import Thread, Lock
from queue import Queue

try:
    import feedparser
    import requests
    import validators
    import progressbar
    from progressbar import ProgressBar
    from pandas import DataFrame
    from bs4 import BeautifulSoup as bs
    import scipy.cluster.hierarchy as hc
    import matplotlib.pyplot as plt
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

    def cook(self):
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
            print("[*] Fetching new blog URIs")
            self.multitask(self.get_random_uris)
            self.write_blog_uris()

            #  Because of multiprocessing list by be over 100
            print("[*] Threads entered {} URIs".format(len(self.blog_uris)))
            self.blog_uris = self.blog_uris[:100]
            print("[*] Limited to {} blog URIs".format(len(self.blog_uris)))

            print("[*] Parsing new feed URIs")
            self.multitask_queue(self.get_feed_uris)
            self.write_feed_uris()
        else:
            print("[*] Found correct amount of data")

        return self.feed_uris

    def multitask(self, function):
        """ Variable function multiprocessing.

        """
        workers = []
        for thread_id in range(self.n_threads):
            worker = Thread(target=function,
                            args=(thread_id,))
            worker.setDaemon(True)
            workers.append(worker)
            worker.start()

        for worker in workers:
            worker.join()

    def multitask_queue(self, function):
        """ Variable function multiprocessing.

        """
        queue = Queue()
        lock = Lock()
        for thread_id in range(self.n_threads):
            worker = Thread(target=function,
                            args=(thread_id, queue, lock))
            worker.setDaemon(True)
            worker.start()
        for uri in self.blog_uris:
            queue.put(uri)
        queue.join()

    def get_random_uris(self, thread_id):
        """ Fetch n random blog URIs.

        """

        _logger.info("Fetching random URIs")

        # Add the two non-random URIs requested
        non_random_uris = ['http://f-measure.blogspot.com/',
                           'http://ws-dl.blogspot.com/']
        self.blog_uris += non_random_uris

        while len(self.blog_uris) < 100:
            try:
                request_uri = ('https://www.blogger.com/next-blog?navBar=true&'
                               'blogID=4117341923751897912')
                response = get_response(request_uri)
                if response is not None:
                    self.blog_uris.append(response.url)
                    self.blog_uris = list(set(self.blog_uris))
                    print("[*] Thread {} Collected blog URI {}"
                          .format(thread_id, len(self.blog_uris)))
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

    def get_feed_uris(self, thread_id, queue, uri_lock):
        """ Parse feed URIs out of HTML pages.

        """
        _logger.info("Getting blog feed URIs")

        while True:

            uri = queue.get()

            _logger.debug("Getting RSS/Atom feed URI from {}".format(uri))
            response = get_response(uri, tries=10, tolerant=True)
            if response is None:
                print("[*] Bad URI {} Aborting".format(uri) + ' <' + '-' * 42)
                sys.exit(1)

            html = response.text

            try:
                soup = bs(html, 'lxml')
            except RuntimeError as error:
                print("[*] WARNING: Beautiful soup failed parsing \
                      {} with error:\n{}".format(uri, error))
                _logger.warning("[*] BeautifulSoup failed parsing \
                                {} with error:\n{}".format(uri, error))

            try:
                feed_rss_uri = soup.find('link',
                                         type='application/rss+xml')['href']
                feed_atom_uri = soup.find('link',
                                          type='application/atom+xml')['href']
            except TypeError as error:
                print("[*] LOOK: {} is not NoneType!".format(response))
                print("[*] LOOK: Neither are {} or {}!"
                      .format(feed_rss_uri, feed_atom_uri))
                print("[*] ERROR: {}".format(error))

            if feed_rss_uri != '':
                _logger.debug("Adding RSS URI {}".format(feed_rss_uri))
                self.feed_uris.append(feed_rss_uri)
                with uri_lock:
                    print("[*] Thread {} found feed URI {}"
                          .format(thread_id, len(self.feed_uris)))
            elif feed_atom_uri != '':
                _logger.debug("Adding Atom URI {}".format(feed_atom_uri))
                with uri_lock:
                    self.feed_uris.append(feed_atom_uri)
                    print("[*] Thread {} found feed URI {}"
                          .format(thread_id, len(self.feed_uris)))
            else:
                _logger.warning("Failed to find feed URI for {}".format(uri))
                print("[*] Failed to find feed URI for {}...".format(uri))

            queue.task_done()

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
    def __init__(self, n_threads, outfile, pickle_file, new_uris):
        self.outfile = outfile
        self.n_threads = n_threads
        self.new_uris = new_uris
        self.uris = []
        self.uris_processed = 0
        self.word_counts = {}       # Number of times a word appears in a blog
        self.appearances = {}       # Number of blogs a word appears in
        # Pickle Storage
        self.word_counts_data = pickle_file
        self.appearances_data = '../data/appearances.pkl'

    def eat(self, uris):
        """ The Gluttons main loop.

        Take all of the cooked up URIs and eat them.

        """
        if self.n_threads > 1:
            print("[*] Spinning up with {} threads".format(self.n_threads))
            _logger.info("[*] Spinning up with {} threads"
                         .format(self.n_threads))
        else:
            print("[*] Spinning up with {} thread".format(self.n_threads))
            _logger.info("[*] Spinning up with {} thread"
                         .format(self.n_threads))

        self.uris = uris

        if not self.new_uris:
            self.word_counts = get_pickled(self.word_counts_data)
            self.appearances = get_pickled(self.appearances_data)

        if len(self.word_counts) != 100 or len(self.appearances) != 100:

            print("[*] Could not find correct pickle data.")

            get_data = ask_yes_no("Gather new data overwriting pickle data?")
            if not get_data:
                cont = ask_yes_no("Continue anyway?")
                if not cont:
                    print("[*] Aborting...")
                    sys.exit(0)
            else:
                # Process the blog feeds to get the word count data
                self.multitask(self.process_feed)

                # Pickle
                print("[*] Pickling new data")
                with open(self.word_counts_data, 'wb') as word_file:
                    pickle.dump(self.word_counts, word_file)
                with open(self.appearances_data, 'wb') as appearance_file:
                    pickle.dump(self.appearances, appearance_file)

        #  stop-word detection
        wordlist = []
        for word, blog_count in self.appearances.items():
            frac = float(blog_count) / len(self.uris)
            if frac > 0.1 and frac < 0.5:
                wordlist.append(word)

        # Save to file
        print("[*] Saving the data")
        with open(self.outfile, 'w') as out:
            out.write('Blog')
            for word in wordlist:
                out.write('\t{}'.format(word))
            out.write('\n')
            for blog, word_count in self.word_counts.items():
                out.write(blog)
                for word in wordlist:
                    if word in word_count:
                        out.write('\t{}'.format(word_count[word]))
                    else:
                        out.write('\t0')
                out.write('\n')

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

    def process_feed(self, thread_id, queue, *args, **kwargs):
        """ Process a RSS/Atom feed.

        """
        while True:
            uri = queue.get()
            _logger.info("Thread {} Processing URI {}".format(thread_id,
                                                              uri))
            (title, word_count) = self.get_word_counts(thread_id, uri)
            self.word_counts[title] = word_count
            for word, count in word_count.items():
                self.appearances.setdefault(word, 0)
                if count > 1:
                    self.appearances[word] += 1

            self.uris_processed += 1
            print("[*] Processed URI number {}".format(self.uris_processed))
            queue.task_done()

    def get_word_counts(self, thread_id, uri):
        """ Parse HTML for all visible text

        """
        feed_dict = feedparser.parse(uri)
        _logger.debug("{}".format(feed_dict.feed))
        word_count = {}

        page = 1
        entries = feed_dict.entries

        while entries:

            print("[**] Processing page {} for {}"
                  .format(page, feed_dict.feed.title))

            for entry in entries:

                _logger.debug("Thread {} Processing blog entry {}/100"
                              .format(thread_id, entry.title))
                if 'summary' in entry:
                    summary = entry.summary
                else:
                    summary = entry.description

                words = self.get_words(thread_id, uri,
                                       (entry.title + ' ' + summary))
                for word in words:
                    _logger.debug("Found word: {}".format(word))
                    word_count.setdefault(word, 0)
                    word_count[word] += 1

            entries = []
            for link in feed_dict.feed.links:
                # Get next set of blog entries
                if link['rel'] == 'next':
                    feed_dict = feedparser.parse(link['href'])
                    entries = feed_dict.entries
                    page += 1

        try:
            feed_dict.feed.title
        except AttributeError as error:
            _logger.warning("URI {} has no blog title\n{}".format(uri, error))

        return (getattr(feed_dict.feed, 'title', 'Unknown'), word_count)

    def get_words(self, thread_id, uri, html):
        """ Parse a HTML document for all visible text

        """

        _logger.debug("[*] Thread {} parsing uri {} HTML"
                      .format(thread_id, uri))

        try:
            soup = bs(html, 'lxml')
        except RuntimeError as error:
            _logger.warning("[*] BeautifulSoup failed parsing \
                            file {} with error:\n{}".format(uri, error))

        [s.extract() for s in soup(
            ['style', 'script', '[document]'])]
        [s.extract() for s in soup() if re.match('<!--.*-->', str(s))]

        text = (''.join(string.findAll(text=True))
                for string in soup.findAll())
        words = [(word.strip()).lower()
                 for string in text
                 for word in string.split()
                 if word.isalpha()]

        # Remove any empty strings
        words = list(filter(len, words))

        _logger.debug("[*] Thread {} finished parsing {}"
                      .format(thread_id, uri))

        return words


class Mathematician():
    """ Does math stuff.

    """
    def __init__(self, blog_data_file):
        self.blog_data_file = blog_data_file
        self.blog_data_dict = self.read_blog_data()
        self.blog_dataframe = self.create_blog_dataframe()

    def read_blog_data(self):
        """ Unpickle the blog data back into a dictionary.

        """
        return get_pickled(self.blog_data_file)

    def create_blog_dataframe(self):
        """ Transform the blog data from a dictionary into a Pandas dataframe.

        Pandas will create it with blog entries as columns and words
        as rows so it is also transformed.

        """
        df = DataFrame(self.blog_data_dict)
        return df.fillna(0)


class Artist():
    """ Draws things.

    """
    def __init__(self, ascii_out, jpeg_out):
        self.ascii_out = ascii_out
        self.jpeg_out = jpeg_out

    def scipy_dendrogram(self, dataframe):
        """ Create a dendrogram with SciPy.

        To sketch the dendrogram the matrix is first transposed, then we
        take the correlation between the resulting transposed matrix
        rows. It is required that the matrix passed to
        ``hc.distance.squareform()`` is symmetric and the transposition
        also allows for that. Then we grab the linkage.

        The resulting sketch is passed to the SciPy dendrogram graphing
        funciton.

        Do not run this on the given blog data unless you have at least
        20GB of ram.

        """
        print("[*] Sketching a dendrogram...\n")

        try:
            dataframe = dataframe.T
            corr = dataframe.corr()
            condensed_corr = hc.distance.squareform(corr)
            z = hc.linkage(condensed_corr, method='average')
        except ValueError as error:
            # ValueError: Distance matrix 'X' diagonal must be zero.
            print("[*] It blew up again... {}".format(error))
            sys.exit(1)

        print("[*] Drawing a dendrogram...")
        dendrogram = hc.dendrogram(z, labels=corr.columns)
        plt.show()

    def jpeg_dendrogram(self, dataframe):
        """ Output a JPEG dendrogram.

        """
        return 1-1


def get_response(uri, tries=1, tolerant=False):
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


def ask_yes_no(question, default="yes"):
    """ Ask a yes/no question via input() and return the answer.

    "question" is a string presented to the user.
    "default" is the presumed most common answer, if the user hits
        <enter> it must be "yes", "no." If default is None then an
        answer is required to be enterd by the user.

    returns (bool): True for "yes" and False for "no"

    """
    valid_answers = {"yes": True, "y": True, "no": False, "n": False}

    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError("invalid default answer: {}".format(default))

    while True:
        print("[*] " + question + prompt, end='')
        answer = input().lower().strip()
        if default is not None and answer == '':
            return valid_answers[default]
        elif answer in valid_answers:
            return valid_answers[answer]
        else:
            print("[*] Please respond with either ('yes'/'y') or ('no'/'n') ")


def get_pickled(pickle_file):
    """ Retrieve and return pickled data.

    """
    try:
        with open(pickle_file, 'rb') as datafile:
            data = pickle.load(datafile)
    except FileNotFoundError as error:
        print("[*] Unable to find saved pickle file with {}".format(error))
        return None

    return data
