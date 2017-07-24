#!/usr/bin/python3
# -*- coding: utf-8 -*-
from distutils.core import setup

with open('README.md','r') as f:
    long_description = f.read()

setup(
      name='fingerfood',
      version='1.0.1',
      description='Document fingerprinting for duplicate detection',
      author='andrea capitanelli',
      author_email='andrea.capitanelli@gmail.com',
      maintainer='andrea capitanelli',
      maintainer_email='andrea.capitanelli@gmail.com',
      url='https://github.com/vegaviz/fingerfood',
      packages=['fingerfood'],
      package_dir={'fingerfood': 'fingerfood'},
      long_description=long_description,
      keywords='fingerprinting copy-detection',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Information Analysis'
     ],
)
