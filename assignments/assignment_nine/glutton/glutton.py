#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" glutton.py

I eat blog feeds.

"""

from __future__ import division, print_function, absolute_import

import os
import re
import sys
import logging
import pickle

from threading import Thread
from queue import Queue

try:
    import feedparser
    import requests
    import validators
    import progressbar
    import progressbar
    from bs4 import BeautifulSoup as bs
except ImportError as error:
    print("[*] Error: {}".format(error))
    print("[*] Please run `pip install -r requrements.txt` "
          "before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


class Hungry():
    """ I eat a blog feed.

    """
    def __init__(self, n_threads, outfile, pickle_file, new_uris, n_entries):
        self.outfile = outfile
        self.n_threads = n_threads
        self.new_uris = new_uris
        self.n_entries = n_entries
        self.word_counts = {}       # Number of times a word appears in a blog
        self.appearances = {}       # Number of blogs a word appears in
        # Pickle Storage
        self.word_counts_data = pickle_file
        self.appearances_data = '../data/appearances.pkl'
        self.title_keys = '../data/truth.yml'

    def eat(self, uris):
        """The Gluttons main loop.

        Process the URIs

        """
        if self.n_threads > 1:
            print("[*] Spinning up with {} threads".format(self.n_threads))
            _logger.info("[*] Spinning up with {} threads"
                         .format(self.n_threads))
        else:
            print("[*] Spinning up with {} thread".format(self.n_threads))
            _logger.info("[*] Spinning up with {} thread"
                         .format(self.n_threads))

        touch(self.word_counts_data)
        touch(self.appearances_data)
        if not self.new_uris:  # Attempt to recover saved data
            try:
                self.word_counts = get_pickled(self.word_counts_data)
                self.appearances = get_pickled(self.appearances_data)
            except EOFError:
                self.word_counts = {}
                self.appearances = {}

        if len(self.word_counts) != self.n_entries:

            print("[*] Could not find correct pickle data.")
            print("[*] Entries: {}/{}"
                  .format(len(self.word_counts), self.n_entries))

            get_data = ask_yes_no("Gather new data overwriting pickle data?",
                                  default="no")
            if not get_data:
                cont = ask_yes_no("Continue anyway?")
                if not cont:
                    print("[*] Aborting...")
                    sys.exit(0)
            else:
                # Empty word_count and appearances
                self.word_counts = {}
                self.appearances = {}

                # Process the blog feeds to get the word count data
                self.multitask(self.process_entry, uris, self.n_threads)

                # Pickle
                print("[*] Pickling new data")
                with open(self.word_counts_data, 'wb') as word_file:
                    pickle.dump(self.word_counts, word_file)
                with open(self.appearances_data, 'wb') as appearance_file:
                    pickle.dump(self.appearances, appearance_file)

        wordlist = self.tfidf()
        self.save_data(wordlist)

    def multitask(self, function, data, threads, *args, **kwargs):
        """ Variable function multiprocessing.

        """
        queue = Queue()
        for thread_id in range(threads):
            worker = Thread(target=function,
                            args=(thread_id, queue, args, kwargs))
            worker.setDaemon(True)
            worker.start()
        for datum in data:
            queue.put(datum)
        queue.join()

    def process_entry(self, thread_id, queue, *args, **kwargs):
        """ Process a Atom feed attempt fallback to RSS if Atom not available.

        """
        uris_processed = 0

        if 'feed_threads' in kwargs:
            feed_threads = kwargs['feed_threads']
        else:
            feed_threads = 1

        while True:
            uri = queue.get()
            _logger.info("Thread {} Processing URI {}".format(thread_id,
                                                              uri))
            self.get_entry_word_counts(thread_id, uri, feed_threads)

            uris_processed += 1
            print("[*] Processed URI number {}".format(uris_processed))
            queue.task_done()

    def get_entry_word_counts(self, thread_id, uri, feed_threads=1):
        """ Parse HTML for all visible text

        """
        feed_dict = feedparser.parse(uri)
        _logger.debug("{}".format(feed_dict.feed))
        word_count = {}

        page = 1
        entries = feed_dict.entries

        # Save the XML
        xml_file = ("../data/raw_xml/" + feed_dict.feed.title +
                    "_page_" + str(page) + ".xml")
        xml_response = get_response(uri, tolerant=True, tries=4)
        with open(xml_file, 'w+') as out:
            out.write(xml_response.text)

        print("[*] Gathering {} entries from {}".format(self.n_entries, uri))
        with progressbar.ProgressBar(max_value=self.n_entries) as pbar:

            processed = 0
            while entries and processed < self.n_entries:

                for entry in entries:

                    if processed >= 100:
                        break

                    word_count = {}
                    title = entry.title
                    response = get_response(entry.link, tolerant=True, tries=4)
                    if "text/html" not in response.headers['content-type']:
                        continue

                    words = self.get_words(thread_id, entry.link, response.text)

                    for word in words:
                        #_logger.debug("Found word: {}".format(word))
                        word_count.setdefault(word, 0)
                        word_count[word] += 1
                    _logger.debug(word_count)

                    self.word_counts[title] = word_count
                    for word, count in word_count.items():
                        self.appearances.setdefault(word, 0)
                        if count > 1:
                            self.appearances[word] += 1

                    processed += 1
                    _logger.debug("Processed entry {}".format(processed))
                    try:
                        pbar.update(processed)
                    except ValueError:
                        pass

                entries = []
                for link in feed_dict.feed.links:
                    # Get next set of blog entries
                    if link['rel'] == 'next':

                        nxt = link['href']

                        # Save the XML
                        page += 1
                        xml_file = ("../data/raw_xml/" + feed_dict.feed.title +
                                    "_page_" + str(page) + ".xml")
                        xml_response = get_response(nxt, tolerant=True, tries=4)
                        with open(xml_file, 'w+') as out:
                            out.write(xml_response.text)

                        # Get new entries
                        feed_dict = feedparser.parse(nxt)
                        entries = feed_dict.entries

        print("[*] Processed {} entries".format(processed))

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

        _logger.debug("[*] Thread {} finished parsing {}:\n"
                      .format(thread_id, uri, words))

        return words

    def tfidf(self):
        """ TFIDF.

        Stop word detection.

        """
        wordlist = []
        for word, entry_count in self.appearances.items():
            frac = float(entry_count) / self.n_entries
            if frac > 0.1 and frac < 0.5:
                wordlist.append(word)

        _logger.debug(wordlist)
        return wordlist

    def save_data(self, wordlist):
        """ Save the data in ASCII.

        The format is intended for use with the Programming Collective
        Intelligence (PCI) code. Also writes out a file with just the
        titles as YAML key values for human categorizing that can be
        easily loaded into a dictionary.

        """
        print("[*] Saving the data")

        # Save to file for PCI
        with open(self.outfile, 'w') as out:
            out.write('Title')
            for word in wordlist:
                _logger.debug("Create column for word{}".format(word))
                out.write('\t{}'.format(word))
            out.write('\n')
            for title, word_count in self.word_counts.items():
                _logger.debug("Saving blog entry: {}".format(title))
                out.write(title)
                for word in wordlist:
                    if word in word_count:
                        out.write('\t{}'.format(word_count[word]))
                    else:
                        out.write('\t0')
                out.write('\n')

        # Without titles for visual matrix comparison
        with open('../data/visual.dat', 'w') as out:
            out.write('Title')
            for word in wordlist:
                _logger.debug("Create column for word{}".format(word))
                out.write('\t{}'.format(word))
            out.write('\n')
            for _, word_count in self.word_counts.items():
                for word in wordlist:
                    if word in word_count:
                        out.write('\t{}'.format(word_count[word]))
                    else:
                        out.write('\t0')
                out.write('\n')


        # YAML titles as keys
        with open(self.title_keys, 'w') as out:
            for title, _ in self.word_counts.items():
                escaped_title = ""
                for letter in title:
                    if letter == '"':
                        escaped_title += '\\"'
                    else:
                        escaped_title += letter

                key = '"' + escaped_title + '":\n'
                out.write(key)


def get_response(uri, tries=1, tolerant=False, timeout=2):
    """ Fetch page

    """
    headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64; \
            rv:45.0) Gecko/20100101 Firefox/45.0"}

    success = False
    for attempt in range(tries):
        try:
            uri = normalize_uri(uri)
            response = requests.get(uri, headers=headers, timeout=timeout)
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


def touch(path):
    """ Create file if does not exist, do not modify if it does.

    Opens and imediately closes a file in append mode, updates the
    last accessed time. Creates any directories in the path that
    do not exist.

    """
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    with open(path, 'a'):
        os.utime(path, None)


def is_even(value):
    """Return true if value is even else false.

    """
    if value % 2 == 0:
        return True
    return False
