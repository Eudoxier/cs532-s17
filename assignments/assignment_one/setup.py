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
        os.system('rm -rfv ./*.egg-info ./*.egg ./common_house_spider/*.pyc')


setup(name="spider",
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      cmdclass={ 'clean' : Clean }
      )
