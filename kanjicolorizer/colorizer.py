#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams
#
# Copyright 2012 Cayenne Boyer
# Patches, clean-up Roland Sieker
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

# Usage: See README and/or run with --help option.
# Configuration is now specified on the command line instead of here.

# Note: this module is in the middle of being refactored.

from codecs import open
from errno import ENOENT as FILE_NOT_FOUND
import argparse
import colorsys
import os
import re
import sys
import xml.etree.ElementTree as ET

source_directory = os.path.join(os.path.dirname(__file__),
                                'data', 'kanjivg', 'kanji')

svg_ns = "http://www.w3.org/2000/svg"
kvg_ns = "http://kanjivg.tagaini.net"

ET.register_namespace('svg', svg_ns)
ET.register_namespace('kvg', kvg_ns)


class KanjiVG(object):
    """
    Class to create kanji objects containing KanjiVG data and some more
    basic qualities of the character
    """
    def __init__(self, character, variant=''):
        u"""
        Create a new KanjiVG object

        Either give just the character

        >>> k1 = KanjiVG(u'漢')
        >>> print(k1.character)
        漢
        >>> k1.variant
        ''

        Or if the character has a variant, give that as a second
        argument

        >>> k2 = KanjiVG(u'字', 'Kaisho')
        >>> print(k2.character)
        字
        >>> k2.variant
        'Kaisho'

        Raises InvalidCharacterError if the character and variant don't
        correspond to known data

        >>> k = KanjiVG((u'Л'))
        Traceback (most recent call last):
            ...
        InvalidCharacterError: (u'\\u041b', '')
        """
        self.character = character
        self.variant = variant
        if self.variant is None:
            self.variant = ''
        try:
            #with open(os.path.join(source_directory,
            #        self.ascii_filename), encoding='utf-8') as f:
            #    self.svg = ET.parse(f, encoding='utf-8').getroot()
            self.svg = ET.parse(
                os.path.join(source_directory, self.ascii_filename)).getroot()
        except IOError as e:  # file not found
            if e.errno == FILE_NOT_FOUND:
                raise InvalidCharacterError(character, variant)
            else:
                raise

    @classmethod
    def _create_from_filename(cls, filename):
        u"""
        Alternate constructor that uses a KanjiVG filename; used by
        get_all().

        >>> k = KanjiVG._create_from_filename('00061.svg')
        >>> k.character
        u'a'
        """
        m = re.match('^([0-9a-f]*)-?(.*?).svg$', filename)
        return cls(unichr(int(m.group(1), 16)), m.group(2))

    @classmethod
    def _char_from_filename(cls, filename):
        u"""
        Munge a file name to a (kanji, variant) pair

        >>> k = KanjiVG._create_from_filename('00061.svg')
        >>> k.character
        u'a'
        """
        m = re.match('^([0-9a-f]*)-?(.*?).svg$', filename)
        return unichr(int(m.group(1), 16)), m.group(2)

    @property
    def ascii_filename(self):
        u"""
        An SVG filename in ASCII using the same format KanjiVG uses.

        >>> k = KanjiVG(u'漢')
        >>> k.ascii_filename
        '06f22.svg'

        May raise InvalidCharacterError for some kinds of invalid
        character/variant combinations; this should only happen during
        KanjiVG object initialization.
        """
        try:
            code = '%05x' % ord(self.character)
        except TypeError:  # character not a character
            raise InvalidCharacterError(self.character, self.variant)
        if not self.variant:
            return code + '.svg'
        else:
            return '%s-%s.svg' % (code, self.variant)

    @property
    def character_filename(self):
        u"""
        An SVG filename that uses the unicode character

        >>> k = KanjiVG(u'漢')
        >>> print(k.character_filename)
        漢.svg
        """
        if not self.variant:
            return '%s.svg' % self.character
        else:
            return '%s-%s.svg' % (self.character, self.variant)

    @classmethod
    def get_list(cls):
        u"""
        Returns a complete list of characters,
        data for

        >>> kanji_list = KanjiVG.get_all()
        >>> kanji_list[0].__class__.__name__
        'KanjiVG'
        """
        kanji = []
        for file in os.listdir(source_directory):
            kanji.append(cls._char_from_filename(file))
        return kanji


class KanjiColorizer(object):
    u"""
    Class that creates colored stroke order diagrams out of kanjivg
    data, and writes them to file.

    Initialize with no arguments to take the command line settings, or
    an empty string to use default settings

    Settings can set by initializing with a string in the same format as
    the command line.
    >>> test_output_dir = os.path.join('test', 'colorized-kanji')
    >>> my_args = ' '.join(['--characters', u'aあ漢',
    ...                     '--output', test_output_dir])
    >>> kc = KanjiColorizer(my_args)

    To get an svg for a single character
    >>> colored_svg = kc.get_colored_svg('a')

    To create a set of diagrams:
    >>> kc.write_all()

    Note: This class is in the middle of having stuff that shouldn't be
    included factored out.  Some things have already been moved to the
    KanjiVG class; more stuff will move to other classes before 0.6.
    """

    def __init__(self, argstring=''):
        """
        Creates a new instance of KanjiColorizer, which stores settings
        and provides various methods to produce colored kanji SVGs.

        Takes an option alrgument of with an argument string; see
        read_arg_string documentation for information on how this is
        used.
        """
        self._init_parser()
        self.read_arg_string(argstring)
        # To re-add the coding declaration and the copyright notice ET
        # swallows.
        self.svg = None
        self.settings = None
        self.svg_header = u'''<?xml version="1.0" encoding="UTF-8"?>
<!--
This file has been modified from the original version by the kanji_colorize.py
script (available at http://github.com/cayennes/kanji-colorize) with these
settings:
    mode: {mode}
    saturation: {saturation}
    value: {value}
    image_size: {image_size}
It remains under a Creative Commons-Attribution-Share Alike 3.0 License.

The original SVG has the following copyright:
Copyright (C) 2009/2010/2011 Ulrich Apel.
This work is distributed under the conditions of the Creative Commons
Attribution-Share Alike 3.0 Licence. This means you are free:
* to Share - to copy, distribute and transmit the work
* to Remix - to adapt the work

Under the following conditions:
* Attribution. You must attribute the work by stating your use of KanjiVG in
  your own copyright header and linking to KanjiVG's website
  (http://kanjivg.tagaini.net)
* Share Alike. If you alter, transform, or build upon this work, you may
  distribute the resulting work only under the same or similar license to this
  one.

See http://creativecommons.org/licenses/by-sa/3.0/ for more details.
-->
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
<!ATTLIST g
xmlns:kvg CDATA #FIXED "http://kanjivg.tagaini.net"
kvg:element CDATA #IMPLIED
kvg:variant CDATA #IMPLIED
kvg:partial CDATA #IMPLIED
kvg:original CDATA #IMPLIED
kvg:part CDATA #IMPLIED
kvg:number CDATA #IMPLIED
kvg:tradForm CDATA #IMPLIED
kvg:radicalForm CDATA #IMPLIED
kvg:position CDATA #IMPLIED
kvg:radical CDATA #IMPLIED
kvg:phon CDATA #IMPLIED >
<!ATTLIST path
xmlns:kvg CDATA #FIXED "http://kanjivg.tagaini.net"
kvg:type CDATA #IMPLIED >
]>
<?xml-stylesheet type="text/css" href="_kanji_style.css"?>
'''

    def _init_parser(self):
        r"""
        Initializes argparse.ArgumentParser self._parser

        >>> kc = KanjiColorizer()

        To show that it really is creating it:
        >>> kc._parser = None

        Then when this method is run:
        >>> kc._init_parser()
        >>> type(kc._parser)
        <class 'argparse.ArgumentParser'>

        >>> kc._parser.get_default('mode')
        'spectrum'

        """
        self._parser = argparse.ArgumentParser(description='Create a set of '
                                             'colored stroke order svgs')
        self._parser.add_argument('--mode', default='spectrum',
                    choices=['spectrum', 'contrast', 'css'],
                    help='spectrum: color progresses evenly through the'
                        ' spectrum; nice for seeing the way the kanji is'
                        ' put together at a glance, but has the disadvantage'
                        ' of using similar colors for consecutive strokes '
                        'which can make it less clear which number goes '
                        'with which stroke. contrast: maximizes contrast '
                        'among any group of consecutive strokes, using the '
                        'golden ratio; also provides consistency by using '
                        'the same sequence for every kanji. css: does no '
                        'coloring, instead adds classes to the paths so that '
                        'the kanji can be colorend with a style sheet. '
                        '(default: %(default)s)')
        self._parser.add_argument('--saturation', default=0.95, type=float,
                    help='a decimal indicating saturation where 0 is '
                        'white/gray/black and 1 is completely  colorful '
                        '(default: %(default)s)')
        self._parser.add_argument('--value', default=0.75, type=float,
                    help='a decimal indicating value where 0 is black '
                        'and 1 is colored or white '
                        '(default: %(default)s)')
        self._parser.add_argument('--image-size', default=327, type=int,
                    help="image size in pixels; they're square so this "
                        'will be both height and width '
                        '(default: %(default)s)')
        self._parser.add_argument('--characters', type=unicode,
                    help='a list of characters to include, without '
                         'spaces; if this option is used, no variants '
                         'will be included; if this option is not '
                         'used, all characters will be included, '
                         'including variants')
        self._parser.add_argument('-r','--relative', dest='rel_size',
                                  action='store_true',
                                  help='''Set the size to 100%%. It is up to \
 the user of the svg to define a size. When using this the image-size \
is ignored.''',
                                  required=False)
        self._parser.add_argument('--filename-mode', default='character',
                    choices=['character', 'code'],
                    help='character: rename the files to use the '
                        'unicode character as a filename.  code: leave it '
                        'as the code.  '
                        '(default: %(default)s)')
        self._parser.add_argument('-o', '--output-directory',
                    default='colorized-kanji')

    # Public methods

    def read_cl_args(self):
        """
        Sets the settings to what's indicated in command line arguments

        >>> kc = KanjiColorizer()
        >>> kc.settings.mode
        'spectrum'
        >>> sys.argv = ['this.py', '--mode', 'contrast']
        >>> kc.read_cl_args()
        >>> kc.settings.mode
        u'contrast'
        """
        # Put argv in the correct encoding
        for i in range(len(sys.argv)):
            sys.argv[i] = sys.argv[i].decode(sys.stdin.encoding)
        self.settings = self._parser.parse_args()

    def read_arg_string(self, argstring):
        """
        >>> kc = KanjiColorizer()
        >>> kc.settings.mode
        'spectrum'
        >>> kc.read_arg_string('--mode contrast')
        >>> kc.settings.mode
        'contrast'
        """
        self.settings = self._parser.parse_args(argstring.split())

    def get_colored_svg(self, character):
        """
        Returns a string containing a colored stroke order diagram svg
        for character.

        >>> kc = KanjiColorizer()
        >>> svg = kc.get_colored_svg('a')
        >>> svg.splitlines()[0]
        u'<?xml version="1.0" encoding="UTF-8"?>'
        >>> svg.find('00061')
        1783
        >>> svg.find('has been modified')
        54

        """
        self.svg = KanjiVG(character).svg
        self._modify_svg()
        return self.svg

    def write_all(self):
        """
        Converts all svgs (or only those specified with the --characters
        option) and prints them to files in the destination directory.

        Silently ignores invalid characters.

        >>> test_output_dir = os.path.join('test', 'colorized-kanji')
        >>> kc = KanjiColorizer(' '.join(['--characters', u'aあ漢',
        ...                               '--output', test_output_dir]))
        >>> kc.write_all()

        These should be the correct files:
        >>> for file in os.listdir(test_output_dir):
        ...     our_svg = open(
        ...         os.path.join(test_output_dir, file),
        ...         'r', encoding='utf-8').read()
        ...     desired_svg = open(
        ...         os.path.join('test', 'default_results',
        ...             'kanji-colorize-spectrum',  file),
        ...             'r', encoding='utf-8').read()
        ...     for line in difflib.context_diff(our_svg.splitlines(1),
        ...            desired_svg.splitlines(1)):
        ...         print(line)
        ...

        Clean up doctest
        >>> shutil.rmtree(test_output_dir)

        """
        self._setup_dst_dir()
        if not self.settings.characters:
            characters = KanjiVG.get_list()
        else:
            characters = []
            for c in self.settings.characters:
                base = c
                variant = ''
                if '-' in c:
                    base = c.split('-')[0]
                    variant = '-'.join(c.split('-')[1:])
                characters.append((base, variant))
        for k_base, var in characters:
            try:
                kanji = KanjiVG(k_base, var)
            except InvalidCharacterError:
                pass
            self.svg = kanji.svg
            self._modify_svg()
            dst_file_path = os.path.join(self.settings.output_directory,
                self._get_dst_filename(kanji))
            with open(dst_file_path, 'w', encoding='utf-8') as f:
                f.write(self._header_copyright())
                f.write(ET.tostring(self.svg))

    def _modify_svg(self):
        u"""
        Applies all desired changes to the SVG

        >>> kc = KanjiColorizer('')
        >>> original_svg = open(
        ...    os.path.join(source_directory, '06f22.svg'),
        ...    'r', encoding='utf-8').read()
        >>> desired_svg = open(
        ...    os.path.join(
        ...        'test', 'default_results', 'kanji-colorize-spectrum',
        ...        u'漢.svg'),
        ...    'r', encoding='utf-8').read()
        >>> for line in difflib.context_diff(
        ...        kc._modify_svg(original_svg).splitlines(1),
        ...        desired_svg.splitlines(1)):
        ...     print(line)
        ...
        """
        if 'css' == self.settings.mode:
            self._classes_svg()
        else:
            self._color_svg()
        self._resize_svg()
        # svg = self._comment_copyright(svg)

    # Private methods for working with files and directories

    def _setup_dst_dir(self):
        """
        Creates the destination directory args.output_directory if
        necessary

        (Set up the doctest environment)
        >>> current_directory = os.path.abspath(os.path.curdir)
        >>> os.mkdir(os.path.join('test', 'doctest-tmp'))
        >>> os.chdir(os.path.join('test', 'doctest-tmp'))
        >>> kc = KanjiColorizer('')

        This creates the directory
        >>> kc._setup_dst_dir()
        >>> os.listdir(os.path.curdir)
        ['colorized-kanji']

        But doesn't do anything or throw an error if it already exists
        >>> kc._setup_dst_dir()
        >>> os.listdir(os.path.curdir)
        ['colorized-kanji']

        (done; reseting environment for other doctests)
        >>> os.rmdir(kc.settings.output_directory)
        >>> os.chdir(os.path.pardir)
        >>> os.rmdir('doctest-tmp')
        >>> os.chdir(current_directory)
        """
        if not (os.path.exists(self.settings.output_directory)):
            os.mkdir(self.settings.output_directory)

    def _get_dst_filename(self, kanji):
        """
        Return the correct filename, based on args.filename-mode

        >>> kc = KanjiColorizer('--filename-mode code')
        >>> kc._get_dst_filename(KanjiVG('a'))
        '00061.svg'
        >>> kc = KanjiColorizer('--filename-mode character')
        >>> kc._get_dst_filename(KanjiVG('a'))
        'a.svg'

        """
        if (self.settings.filename_mode == 'character'):
            return kanji.character_filename
        else:
            return kanji.ascii_filename

    # private methods for modifying svgs

    def _color_svg(self):
        """
        Color the svg with colors from _color_generator, which uses
        configuration from settings

        This adds a style attribute to path (stroke) and text (stroke
        number) elements. We use ElementTree now, so we don't have to
        worry about exact text properties. Not all SVGs include stroke
        numbers.

        >>> svg = "<svg><path /><path /><text >1</text><text >2</text></svg>"
        >>> kc = KanjiColorizer('')
        >>> kc._color_svg(svg)
        '<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /><text style="stroke:#bf0909" >1</text><text style="stroke:#09bfbf" >2</text></svg>'
        >>> svg = "<svg><path /><path /></svg>"
        >>> kc._color_svg(svg)
        '<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /></svg>'
        """
        paths_list = list(
            self.svg.getiterator('{{{ns}}}path'.format(ns=svg_ns)))
        texts_list = list(
            self.svg.getiterator('{{{ns}}}text'.format(ns=svg_ns)))
        color_iterator = self._color_generator(len(paths_list))
        for path_el in paths_list:
            path_el.set(
                'style', 'stroke:{color}'.format(color=next(color_iterator)))
        for text_el in texts_list:
            text_el.set(
                'style', 'stroke:{color}'.format(color=next(color_iterator)))

    def _classes_svg(self):
        """
        Add classes to paths
        """
        for path_el in self.svg.getiterator('{{{ns}}}path'.format(ns=svg_ns)):
            try:
                id_ = path_el.get('id')
            except KeyError:
                print 'id-less path found'
            else:
                try:
                    id_num = id_.split('-')[-1].lstrip('s')
                except ValueError:
                    print u'bad path id: {0}'.format(id_)
                else:
                    path_el.set(
                        'class', 'stroke_path stroke_num{0}'.format(id_num))
        for text_el in self.svg.getiterator('{{{ns}}}text'.format(ns=svg_ns)):
            try:
                text = text_el.text
            except (KeyError, TypeError):
                print 'text-less text'
            else:
                try:
                    id_num = int(text)
                except ValueError:
                    print u'bad text, NAI: {0}'.format(text)
                else:
                    text_el.set(
                        'class', 'stroke_number stroke_num{0}'.format(id_num))
        for gr in self.svg.getiterator('{{{ns}}}g'.format(ns=svg_ns)):
            try:
                id_ = gr.get('id')
            except KeyError:
                print 'id-less group found'
            else:
                try:
                    id_num = int(id_.split('-')[-1].lstrip('g'))
                except ValueError:
                    pass
                    # print u'bad group id: {0}'.format(id_)
                else:
                    gr.set(
                        'class', 'stroke_group group_num{0}'.format(id_num))

    def _header_copyright(self):
        """
        Return the xml preamble and a copyright comment.

        >.>> svg = '''<!--
        ... Copyright (C) copyright holder (etc.)
        ... -->
        ... <svg> <! content> </svg>
        ... '''

        This contains the notice:

        >.>> kc = KanjiColorizer('')
        >.>> kc._header_copyright(svg).count('This file has been modified')
        1

        And depends on the settings it is run with:

        >.>> kc = KanjiColorizer('--mode contrast')
        >.>> kc._comment_copyright(svg).count('contrast')
        1
        >.>> kc = KanjiColorizer('--mode spectrum')
        >.>> kc._comment_copyright(svg).count('contrast')
        0
        """
        return self.svg_header.format(mode=self.settings.mode,
                                      saturation=self.settings.saturation,
                                      value=self.settings.value,
                                      image_size=self.settings.image_size)

    def _resize_svg(self):
        """

        Resize the svg according to args.image_size, by changing the 109s
        in the <svg> attributes, and adding a transform scale to the
        groups enclosing the strokes and stroke numbers

        >>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g></svg>'
        >>> kc = KanjiColorizer('--image-size 100')
        >>> kc._resize_svg(svg)
        '<svg  width="100" height = "100" viewBox="0 0 100 100"><!109><g id="kvg:StrokePaths_" transform="scale(0.9174311926605505,0.9174311926605505)"><path /></g></svg>'
        >>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g><g id="kvg:StrokeNumbers_"><text /></g></svg>'
        >>> kc = KanjiColorizer('--image-size 327')
        >>> kc._resize_svg(svg)
        '<svg  width="327" height = "327" viewBox="0 0 327 327"><!109><g id="kvg:StrokePaths_" transform="scale(3.0,3.0)"><path /></g><g id="kvg:StrokeNumbers_" transform="scale(3.0,3.0)"><text /></g></svg>'
        """
        # That is what the width and height are for. And what we use the ET for.
        if self.settings.rel_size:
            self.svg.set('width', '100%')
            self.svg.set('height', '100%')
        else:
            self.svg.set('width', str(self.settings.image_size))
            self.svg.set('height', str(self.settings.image_size))

    # Private utility methods

    def _hsv_to_rgbhexcode(self, h, s, v):
        """
        Convert an h, s, v color into rgb form #000000

        >>> kc = KanjiColorizer('')
        >>> kc._hsv_to_rgbhexcode(0, 0, 0)
        '#000000'
        >>> kc._hsv_to_rgbhexcode(2.0/3, 1, 1)
        '#0000ff'
        >>> kc._hsv_to_rgbhexcode(0.5, 0.95, 0.75)
        '#09bfbf'
        """
        color = colorsys.hsv_to_rgb(h, s, v)
        return '#%02x%02x%02x' % tuple([i * 255 for i in color])

    def _color_generator(self, n):
        """
        Create an iterator that loops through n colors twice (so that
        they can be used for both strokes and stroke numbers) using
        mode, saturation, and value from the args namespace

        >>> my_args = '--mode contrast --saturation 1 --value 1'
        >>> kc = KanjiColorizer(my_args)
        >>> [color for color in kc._color_generator(3)]
        ['#ff0000', '#004aff', '#94ff00', '#ff0000', '#004aff', '#94ff00']
        >>> my_args = '--mode spectrum --saturation 0.95 --value 0.75'
        >>> kc = KanjiColorizer(my_args)
        >>> [color for color in kc._color_generator(2)]
        ['#bf0909', '#09bfbf', '#bf0909', '#09bfbf']
        """
        if (self.settings.mode == "contrast"):
            angle = 0.618033988749895  # conjugate of the golden ratio
            for i in 2 * range(n):
                yield self._hsv_to_rgbhexcode(i * angle,
                    self.settings.saturation, self.settings.value)
        else:  # spectrum is default
            for i in 2 * range(n):
                yield self._hsv_to_rgbhexcode(float(i) / n,
                    self.settings.saturation, self.settings.value)


# Exceptions

class Error(Exception):
    """
    Base class for this module's exceptions
    """
    pass


class InvalidCharacterError(Error):
    """
    Exception thrown when trying to initialize or use a character that
    there isn't data for
    """
    pass


# Test if run

if __name__ == "__main__":
    import doctest
    import difflib
    import shutil
    doctest.testmod()
