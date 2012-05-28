#!/usr/bin/python2

# setup.py is part of kanji-colorize which makes KanjiVG data into
# colored stroke order diagrams
#
# Copyright 2012 Cayenne Boyer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name='KanjiColorizer',
    description='script and module to create colored stroke order '
        'diagrams based on KanjiVG data',
    long_description=open('README.rst').read(),
    version='0.5',
    author='Cayenne',
    author_email='cayennes@gmail.com',
    url='http://github.com/cayennes/kanji-colorize',
    packages=['kanjicolorizer'],
    scripts=['kanji_colorize.py'],
    package_data={'kanjicolorizer': ['data/kanjivg/kanji/*.svg']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License '
            'v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Education',
        'Topic :: Multimedia :: Graphics'
        ]
    )

