#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from paver.easy import *
from paver.setuputils import setup
import zipfile


options(
    anki=Bunch(
        builddir=path('build') / 'anki_addon',
        zip=path('dist') / 'KanjiColorizerAnkiAddon.zip'))


setup(
    name='KanjiColorizer',
    description='script and module to create colored stroke order '
        'diagrams based on KanjiVG data',
    long_description=open('README.rst').read(),
    version='0.11dev',
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
        'Topic :: Multimedia :: Graphics' ])


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    pass


@task
def clean_anki_addon(options):
    if options.anki.builddir.exists():
        options.anki.builddir.rmtree()


@task
@needs('setuptools.command.build', 'clean_anki_addon')
def build_anki_addon(options):

    import argparse
    import colorsys

    # somewhere to put things
    options.anki.builddir.makedirs()

    # add addon files
    (path('anki') / '__init__.py').copy(options.anki.builddir)
    (path('anki') / 'kanji_colorizer.py').copy(options.anki.builddir)
    lib_path = path('build') / 'lib' / 'kanjicolorizer'
    lib_path.copytree(options.anki.builddir / 'kanjicolorizer')

    # add required modules
    path(argparse.__file__).copy(options.anki.builddir / 'kanjicolorizer')
    path(colorsys.__file__).copy(options.anki.builddir / 'kanjicolorizer')

    # add licenses
    license_dest = options.anki.builddir / 'kanjicolorizer' / 'licenses'
    path('licenses').copytree(license_dest)


@task
@needs('build_anki_addon')
def dist_anki_addon(options):
    print("create addon zip at " + options.anki.zip)
    with zipfile.ZipFile(options.anki.zip, 'w') as addon_zip:
        for file in options.anki.builddir.walkfiles():
            addon_zip.write(file, options.anki.builddir.relpathto(file))
