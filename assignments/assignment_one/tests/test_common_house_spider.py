#!/usr/bin/env python

import pytest
import future

from queue import Queue
from common_house_spider.crawler import *

class TestCrawler:

    def test_crawl(self):
        
        with open("tests/data/odu_spring_16_links.dat") as links:
            spring_16_links = [line.strip() for line in links]
        with open("tests/data/odu_spring_16_sizes.dat") as sizes:
            spring_16_sizes = [line.strip() for line in sizes]
        spring_16_test_data = zip(spring_16_links, spring_16_sizes)

        with open("tests/data/odu_spring_17_links.dat") as links:
            spring_17_links = [line.strip() for line in links]
        with open("tests/data/odu_spring_17_sizes.dat") as sizes:
            spring_17_sizes = [line.strip() for line in sizes]
        spring_17_test_data = zip(spring_17_links, spring_17_sizes)

        odu_spring_16 = "http://www.cs.odu.edu/~mln/teaching/cs532-s16/test/pdfs.html"
        odu_spring_17 = "http://www.cs.odu.edu/~mln/teaching/cs532-s17/test/pdfs.html"

        q = Queue()
        q.put(odu_spring_16)
        data = crawl(0, q)
        assert data[1] == 10
        assert data[2] == 10
        for link, size in data[0]:
            assert link in spring_16_links
            assert size in spring_16_sizes
        
        q = Queue()
        q.put(odu_spring_17)
        data = crawl(0, q)
        assert data[1] == 11
        assert data[2] == 11
        for link, size in data[0]:
            assert link in spring_17_links
            assert size in spring_17_sizes
