#!/usr/bin/env python

import re
import sys
import pytest
import future

from common_house_spider.crawler import *

class TestCrawler:

    @pytest.fixture(scope="module")
    def data_16(self):

        with open("tests/data/odu_spring_16_links.dat") as links:
            spring_16_links = [line.strip() for line in links]
        with open("tests/data/odu_spring_16_sizes.dat") as sizes:
            spring_16_sizes = [line.strip() for line in sizes]

        return zip(spring_16_links, spring_16_sizes)


    @pytest.fixture(scope="module")
    def data_17(self):

        with open("tests/data/odu_spring_17_links.dat") as links:
            spring_17_links = [line.strip() for line in links]
        with open("tests/data/odu_spring_17_sizes.dat") as sizes:
            spring_17_sizes = [line.strip() for line in sizes]

        return zip(spring_17_links, spring_17_sizes)


    @pytest.fixture(scope="module")
    def data_stats(self):

        with open("tests/data/stats_links.dat") as links:
            stats_links = [line.strip() for line in links]
        with open("tests/data/stats_sizes.dat") as sizes:
            stats_sizes = [line.strip() for line in sizes]

        return zip(stats_links, stats_sizes)


    @pytest.fixture(scope="module")
    def data_blackhat(self):

        with open("tests/data/blackhat_links.dat") as links:
            stats_links = [line.strip() for line in links]
        with open("tests/data/blackhat_sizes.dat") as sizes:
            stats_sizes = [line.strip() for line in sizes]

        return zip(stats_links, stats_sizes)


    @pytest.fixture(scope="module")
    def data_carhacking(self):

        with open("tests/data/carhacking_links.dat") as links:
            stats_links = [line.strip() for line in links]
        with open("tests/data/carhacking_sizes.dat") as sizes:
            stats_sizes = [line.strip() for line in sizes]

        return zip(stats_links, stats_sizes)


    def test_crawler_17_inclusive(self, capfd, data_17):
        """ Test that actual PDF links are in output

        """
        odu_spring_17 = "http://www.cs.odu.edu/~mln/teaching/cs532-s17/test/pdfs.html"
        sweeper([odu_spring_17], 1)
        out, err = capfd.readouterr()

        for link, size in data_17:
            assert link, size in out

        output_data = []

    def test_crawler_17_exclusive(self, capfd, data_17):
        """ Test that all URLs in output match actual PDF links

        """
        odu_spring_17 = "http://www.cs.odu.edu/~mln/teaching/cs532-s17/test/pdfs.html"
        sweeper([odu_spring_17], 1)
        out, err = capfd.readouterr()

        output_urls = out.rstrip().split('\n')

        output_data = []
        for line in output_urls:
            line = line.strip()
            if line.startswith('http://') or line.startswith('https://'):
                url, size = line.split()
                output_data.append((url, size))

        for link, size in output_data:
            assert link, size in data_17


    def test_crawler_16_inclusive(self, capfd, data_16):
        """ Test that output includes all correct PDFs and sizes.

        """
        odu_spring_16 = "http://www.cs.odu.edu/~mln/teaching/cs532-s16/test/pdfs.html"
        sweeper([odu_spring_16], 1)
        out, err = capfd.readouterr()

        for link, size in data_16:
            assert link, size in out


    def test_crawler_16_exclusive(self, capfd, data_16):
        """ Test that all URLs in output match actual PDF links

        """
        odu_spring_16 = "http://www.cs.odu.edu/~mln/teaching/cs532-s16/test/pdfs.html"
        sweeper([odu_spring_16], 1)
        out, err = capfd.readouterr()

        output_urls = out.rstrip().split('\n')

        output_data = []
        for line in output_urls:
            line = line.strip()
            if line.startswith('http://') or line.startswith('https://'):
                url, size = line.split()
                output_data.append((url, size))

        for link, size in output_data:
            assert link, size in data_16


    def test_crawler_balckhat_inclusive(self, capfd, data_blackhat):
        """ Test that output includes all correct PDFs and sizes.

        """
        blackhat = "https://www.nostarch.com/blackhatpython"
        sweeper([blackhat], 1)
        out, err = capfd.readouterr()

        for link, size in data_blackhat:
            assert link, size in out


    def test_crawler_blackhat_exclusive(self, capfd, data_blackhat):
        """ Test that all URLs in output match actual PDF links

        """
        blackhat = "https://www.nostarch.com/blackhatpython"
        sweeper([blackhat], 1)
        out, err = capfd.readouterr()

        output_urls = out.rstrip().split('\n')

        output_data = []
        for line in output_urls:
            line = line.strip()
            if line.startswith('http://') or line.startswith('https://'):
                url, size = line.split()
                output_data.append((url, size))

        for link, size in output_data:
            assert link, size in data_blackhat


    def test_crawler_stats_inclusive(self, capfd, data_stats):
        """ Test that output includes all correct PDFs and sizes.

        """
        stats = "www.nostarch.com/statsdonewrong"
        sweeper([stats], 1)
        out, err = capfd.readouterr()

        for link, size in data_stats:
            assert link, size in out


    def test_crawler_stats_exclusive(self, capfd, data_stats):
        """ Test that all URLs in output match actual PDF links

        """
        stats = "www.nostarch.com/statsdonewrong"
        sweeper([stats], 1)
        out, err = capfd.readouterr()

        output_urls = out.rstrip().split('\n')

        output_data = []
        for line in output_urls:
            line = line.strip()
            if line.startswith('http://') or line.startswith('https://'):
                url, size = line.split()
                output_data.append((url, size))

        for link, size in output_data:
            assert link, size in data_stats


    def test_crawler_carhacking_inclusive(self, capfd, data_carhacking):
        """ Test that output includes all correct PDFs and sizes.

        """
        carhacking = "http://www.nostarch.com/carhacking"
        sweeper([carhacking], 1)
        out, err = capfd.readouterr()

        for link, size in data_carhacking:
            assert link, size in out


    def test_crawler_carhacking_exclusive(self, capfd, data_carhacking):
        """ Test that all URLs in output match actual PDF links

        """
        carhacking = "http://www.nostarch.com/carhacking"
        sweeper([carhacking], 1)
        out, err = capfd.readouterr()

        output_urls = out.rstrip().split('\n')

        output_data = []
        for line in output_urls:
            line = line.strip()
            if line.startswith('http://') or line.startswith('https://'):
                url, size = line.split()
                output_data.append((url, size))

        for link, size in output_data:
            assert link, size in data_carhacking
