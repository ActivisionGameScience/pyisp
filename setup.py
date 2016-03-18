#!/usr/bin/env python

from setuptools import setup, find_packages
import os

#from pip.req import parse_requirements
#import pip
#requirements = [
#    str(req.req) for req in parse_requirements('requirements.txt', session=pip.download.PipSession())
#]

setup(name='pyisp',
      version=os.getenv('VERSION'),
      description='IP to ISP lookup library.  Supports Autonomous System lookup',
      author='Spencer Stirling',
      packages=[
          'pyisp',
      ],
      include_package_data=True,
      install_requires=[
          'py-radix',
      ],
     )
