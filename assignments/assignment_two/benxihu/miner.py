#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" miner.py

Get links from twitter.

"""

from __future__ import division, print_function, absolute_import

import sys
import logging
import time
import os
import re


try:
    import requests
    import validators
    from tweepy.streaming import StreamListener
    from tweepy import OAuthHandler
    from tweepy import Stream
    from ttp import ttp
except ImportError as e:
    print("[*] Error: {}".format(e))
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


class Miner(StreamListener):
    """ Grabs and filters tweets from twitter.

    Attributes:
        keywords (:obj:`list` of :obj:`str`): list of keywords desired in tweets.

        access_token (str): Access token used to make API requests on an
            accounts behalf.

        access_token_secret (str): The second half of the access token,
            this part should never be shared with anyone or appear in
            any source code.

        consumer_key (str): The API key also required to connect.

        consumer_secret (str): The second secret half of the API key,
            this part should never be shared with anyone or appear in
            any source code.

    """
    def __init__(self, keywords, target, input_file=None):
        """ 

        """
        # Input
        self.input_file = input_file

        # Authentication Attributes
        self.keywords = keywords
        self.access_token = ''
        self.access_token_secret = ''
        self.consumer_key = ''
        self.consumer_secret = ''
        self.auth = ''

        # Count
        self.target = target
        #self.count = 0
        self.links = []
        self.final_redirects = []

        # Output Stream
        self.stream = None

        # For data file name generation
        self.data_path = "../data/{}_data_{}.json"\
                .format(keywords[0], str(int(time.time()))).replace(' ', '_')

        self.link_path = "../data/{}_links_{}.dat"\
                .format(keywords[0], str(int(time.time()))).replace(' ', '_')


    def run(self):
        """

        """
        _logger.debug("Using file: {}".format(self.data_path))
        _logger.debug("Using file: {}".format(self.link_path))
        if self.input_file == None:
            self.get_keys()
            self.login()
            self.keyword_filter()
        else:
            self.parse()

    def on_data(self, data):
        """

        """
        _logger.debug("----------------- Recieved New Data -----------------")
        success = self.targeted_filter(data)
        if success:
            #self.count += 1
            _logger.info("Collected data point number: {}".format(len(self.links)))
        else:
            _logger.debug("Filtered Data")

        if len(self.links) <= self.target:
            return True

        # End Tweepy Stream
        _logger.debug("================= End Stream =================")
        return False



    def on_error(self, error):
        _logger.error("Error: {}".format(error))
        print("Error: {}".format(error))

    def get_keys(self):
        """ Get the API tokens, keys, and secrets from config file.

        """
        with open("api.keys", 'r') as keys:
            self.access_token = keys.readline().split('=')[1].strip()
            self.access_token_secret = keys.readline().split('=')[1].strip()
            self.consumer_key = keys.readline().split('=')[1].strip()
            self.consumer_secret = keys.readline().split('=')[1].strip()

    def login(self):
        """ Authenticate to the twitter streaming API.

        """
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.stream = Stream(self.auth, self)

    def keyword_filter(self):
        """ Filter tweets by a list of keywords.

        """
        _logger.debug("Filtering stream by keywords: {}".format(self.keywords))
        self.stream.filter(track=self.keywords)

    def targeted_filter(self, data):
        """ Detect tweets with URLs.

        """
        p = ttp.Parser()
        result = p.parse(data)

        _logger.debug("Data URLs: {}".format(result.urls))
        _logger.debug("Data Reply: {}".format(result.reply))
        _logger.debug("Data Users: {}".format(result.users))
        _logger.debug("Data Tags: {}".format(result.tags))

        regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(regex, data)

        if match:

            link = match.group(0).strip().replace('\\', '')
            link = link.strip()
            
            try: 
                response = get_response(link)
                self.final_redirects.append(response.url)
            except requests.exceptions.RequestException as e:
                _logger.error("Error resolving link: {}".format(link))
                _logger.error("RequestException: {}".format(e))
                return False
            except UnicodeError as e:
                _logger.error("Error resolving link: {}".format(link))
                _logger.error("UnicodeError: {}".format(e))
                return False

            if link not in self.links and link not in self.final_redirects:
                _logger.info("Success found URL: {}".format(link))
                self.tweet_save(data, link)
                self.links.append(link)
                return True

        elif result.urls and result.urls not in self.links:

            try: 
                response = get_response(link)
                self.final_redirects.append(response.url)
            except requests.exceptions.RequestException as e:
                _logger.error("Error resolving link: {}".format(link))
                _logger.error("RequestException: {}".format(e))
                return False
            except UnicodeError as e:
                _logger.error("Error resolving link: {}".format(link))
                _logger.error("UnicodeError: {}".format(e))
                return False

            if result.urls not in self.final_redirects:

                _logger.info("Success found URL: {}".format(result.urls))
                self.tweet_save(data, result.urls)
                self.links.append(link)
                return True

        return False

    def tweet_save(self, data, link):
        """

        """
        with open(self.data_path, 'a+') as datafile, \
                open(self.link_path, 'a+') as linkfile:

            datafile.write(data)
            linkfile.write(link + '\n')
            _logger.debug("Found tweet with link: {}".format(link))
            print(link)


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
