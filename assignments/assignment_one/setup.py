#!/usr/bin/env python
import os
from setuptools import setup, Command


class Clean(Command):
    """ Remove temp files in project root

    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -rfv ./*.egg-info \
                  ./*.egg \
                  ./common_house_spider/*.pyc \
                  ./build \
                  ./dist'
                  )


dist_description = ( "The Common House Spider crawls given webpages for links "
                     "and checks if each is a PDF. It collects the PDF links "
                     "and displays them along with the PDF size. It is "
                     "Possible to spawn multiple spiders to significantly "
                     "speed up crawling multiple pages." )


setup(name="common_house_spider",
      version="1.0",
      description="Locates PDF links on a webpage",
      long_description=dist_description,
      author="Derek Goddeau",
      author_email="dgodd001@odu.edu",
      url="https://gitlab.com/datenstrom/cs532-s17/tree/master/assignments/assignment_one",
      license="GNU GPLv3",
      py_modules=['common_house_spider.crawler',
                  'common_house_spider.cli'],
      platforms=['Operating System :: POSIX :: Linux'],
      classifiers=['Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Natural Language :: English',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Intended Audience :: Other Audience',
                   'Environment :: Console',
                   'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
                   'Topic :: Security'],
      install_requires=['bs4',
                        'requests',
                        'future',
                        'tabulate',
                        'setuptools',
                        'validators',
                        'python-magic'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      cmdclass={ 'clean' : Clean }
      )
