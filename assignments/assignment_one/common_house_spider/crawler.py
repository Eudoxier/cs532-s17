#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" crawl.py

Crawl a page for PDF links

"""

from __future__ import division, print_function, absolute_import

import sys
import logging
import requests

from threading import Thread
from queue import Queue

try:
    import magic
    import future
    import validators
    from bs4 import BeautifulSoup as soup
    from tabulate import tabulate
except ImportError:
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

_logger = logging.getLogger(__name__)


def crawl(thread, q):
    """ Crawl a page for PDF links

    """
    while True:

        address = q.get()
        pdf_links = []
        sizes = []

        try:
            html = get_response(address).content
            data = soup(html, "html.parser")
        except requests.exceptions.RequestException as e:
            print("[*] Request Error for {}: {}: ".format(address, e))
            q.task_done()
            continue


        for tag in data.findAll('a', href=True):

            url = tag.get('href')
            url = normalize_url(url)
            if not validators.url(url): 
                continue    # catch things like `javascript:toggle();

            try:
                response = get_response(url)
                content = response.content
                content_type = response.headers.get('content-type')
                mime_type = magic.from_buffer(content)
                size = response.headers.get('content-length')

                if 'application/pdf' in content_type or 'PDF' in mime_type:
                    pdf_links.append(tag['href'])
                    sizes.append(size)

            except requests.exceptions.RequestException as e:
                continue

        num_pdfs = len(pdf_links)
        print_data = list(set(zip(pdf_links, sizes)))
        num_duplicates = num_pdfs - len(print_data)

        print("[*] Thread {} discovered {} PDF links for {}"\
                .format(thread, num_pdfs, address))
        if num_duplicates > 1 or num_duplicates == 0:
            print("[*] Thread {} removed {} duplicate PDF files\n"\
                    .format(thread, num_duplicates, address))
        else:
            print("[*] Thread {} removed {} duplicate PDF file\n"\
                    .format(thread, num_duplicates, address))


        print("{}\n".format(tabulate(print_data, headers=['PDF link', 'size: bytes'], tablefmt="rst")))

        q.task_done()


def sweeper(addresses, threads):
    """ Start threads, put addresses in queue

    """
    q = Queue()

    if threads > 1:
        print("[*] Spinning up with {} threads\n".format(threads))
    else:
        print("[*] Spinning up with {} thread\n".format(threads))

    for thread_id in range(threads):
        worker = Thread(target=crawl, args=(thread_id, q))
        worker.setDaemon(True)
        worker.start()
    for address in addresses:
        q.put(address)
    q.join()


def get_response(address):
    """ Fetch page, raise errors for bad status codes.

    """
    headers = {'user-agent': "Mozilla/5.0 (X11; Linux x86_64; \
            rv:45.0) Gecko/20100101 Firefox/45.0"}

    address = normalize_url(address)
    response = requests.get(address, headers=headers, timeout=1)
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
