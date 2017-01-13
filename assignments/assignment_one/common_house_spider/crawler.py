#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" crawl.py

Crawl a page for PDF links

"""

from __future__ import division, print_function, absolute_import

import sys
import future
import logging
import requests

from threading import Thread
from queue import Queue


try:
    from bs4 import BeautifulSoup as soup
except ImportError:
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)


__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def crawl(thread, q):
    """ Crawl a page for PDF links

    """
    while True:

        pdf_links = []
        address = q.get()

        try:

            html = get_page(address)
            data = soup(html, "html.parser")

            for tag in data.findAll('a', href=True):
                url = tag.get('href').strip("http://")
                url = "http://" + url
                response = requests.get(url)
                content_type = response.headers.get('content-type')
                if 'application/pdf' in content_type:
                    pdf_links.append(tag['href'])

        except requests.exceptions.RequestException as e:

            print("[*] Request Error for {}: {}: ".format(url, e))

        print("[*] Thread {} discovered {} PDF links for {}"\
                .format(thread, len(pdf_links), address))

        for pdf_link in pdf_links:
            print(pdf_link)

        q.task_done()


def sweeper(addresses, threads):
    """ Start threads, put addresses in queue

    """
    q = Queue()
    print("[*] Spinning up with {} threads".format(threads))
    for thread_id in range(threads):
        worker = Thread(target=crawl, args=(thread_id, q))
        worker.setDaemon(True)
        worker.start()
    for address in addresses:
        q.put(address)
    q.join()


def get_page(address):
    """ Fetch page, raise errors for bad status codes.

    """
    headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64; \
            rv:45.0) Gecko/20100101 Firefox/45.0"}

    response = requests.get(address, headers=headers, timeout=1)
    response.raise_for_status()
    html = response.content

    return html
