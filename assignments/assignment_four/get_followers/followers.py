#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" fetch.py

Get followers

"""

from __future__ import division, print_function, absolute_import

import sys
import logging
import time
import os


try:
    import requests
    import validators
    import twitter
except ImportError as e:
    print("[*] Error: {}".format(e))
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


class Followers():
    """ Grabs and filters tweets from twitter.

    Attributes:
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
    def __init__(self, username):
        """ 

        """
        # Data
        self.username = username

        # Authentication Attributes
        self.access_token = ''
        self.access_token_secret = ''
        self.consumer_key = ''
        self.consumer_secret = ''
        self.api = self.login()

        # For data file username generation
        self.data_path = "../data/{}_data_{}.json"\
                .format(self.username, str(int(time.time()))).replace(' ', '_')

        self.followers = []


    def run(self):
        """

        """
        _logger.debug("Using file: {}".format(self.data_path))
        self.fetch()
        _logger.debug("Got Followers: {}".format(self.followers))
        print(self.followers)
        self.write()


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
        self.get_keys()
        api = twitter.Api(consumer_key=self.consumer_key,
                          consumer_secret=self.consumer_secret,
                          access_token_key=self.access_token,
                          access_token_secret=self.access_token_secret
                         )
        return api


    def fetch(self):
        """

        """
        followers = self.api.GetFollowers(self.username)
        return followers


    def write(self):
        """

        """
        with open(self.data_path, 'w') as outfile:
            for follower in self.followers:
                _logger.debug("Follower: {}".format(follower))
                outfile.write(str(follower))
