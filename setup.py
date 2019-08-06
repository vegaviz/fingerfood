#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path as os_path
from setuptools import setup

# Package meta-data.
NAME = 'web-utils'
DESCRIPTION = 'A few tools for managing web content.'
URL = 'https://github.com/acapitanelli/web-utils'
AUTHOR = 'Andrea Capitanelli'
EMAIL = 'andrea@capitanelli.gmail.com'
VERSION = '1.0.0'

# short/long description
here = os_path.abspath(os_path.dirname(__file__))
try:
    with open(os_path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
        long_desc = '\n' + f.read()
except FileNotFoundError:
    long_desc = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    url=URL,
    python_requires='>=3.6.0',
    packages=['web_utils'],
    long_description=long_desc,
    long_description_content_type='text/markdown',
    keywords='web utils download html text fingerprinting',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System'
    ]
)
