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


dist_description = ( "Grabs links from twitter" )


setup(name="benxihu",
      version="1.0",
      description="Grabs links from twitter",
      long_description=dist_description,
      author="Derek Goddeau",
      author_email="dgodd001@odu.edu",
      url="https://gitlab.com/datenstrom/cs532-s17/tree/master/assignments/assignment_two",
      license="GNU GPLv3",
      py_modules=['benxihu.cli'],
      platforms=['Operating System :: POSIX :: Linux'],
      classifiers=['Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Natural Language :: English',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Intended Audience :: Other Audience',
                   'Environment :: Console',
                   'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
                   'Topic :: Security'],
      install_requires=['tweepy'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      cmdclass={ 'clean' : Clean }
      )
