#!/usr/bin/env python
# Copyright (c) 2017 Joshua Henderson <digitalpeer@digitalpeer.com>
#
# SPDX-License-Identifier: GPL-3.0
# coding=utf-8
import sys
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as _sdist
import subprocess
import codecs
from tinycom import __version__

class sdist(_sdist):
    def run(self):
        try:
            subprocess.check_call('make')
        except subprocess.CalledProcessError as e:
            raise SystemExit(e)
        _sdist.run(self)

try:
    import pypandoc
    README = pypandoc.convert('README.md', 'rst')
except ImportError:
    with codecs.open('README.md', encoding='utf-8') as f:
        README = f.read()

with codecs.open('CHANGES.rst', encoding='utf-8') as f:
    CHANGES = f.read()

setup(
    name='tinycom',
    version=__version__,
    author='Joshua Henderson',
    author_email='digitalpeer@digitalpeer.com',
    url='https://github.com/digitalpeer/tinycom',
    download_url='https://github.com/digitalpeer/tinycom/zipball/master',
    description='A simple line based serial terminal GUI.',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
    },
    entry_points={
        'gui_scripts': [
            'tinycom = tinycom.tinycom:main',
        ]
    },
    install_requires=[],
    keywords='serial terminal',
    license='GPL3',
    classifiers=['Development Status :: 3 - Alpha',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Topic :: Terminals :: Serial',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Information Technology',
    ],
    cmdclass={'sdist': sdist},
)
