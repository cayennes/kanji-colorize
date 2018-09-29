#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams
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

# Usage: See README and/or run with --help option.
# Configuration is now specified on the command line instead of here.

# Note: this module is in the middle of being refactored.

import os
import re
from errno import ENOENT as FILE_NOT_FOUND
import sys

# Anki add-on compatibility
try:
    import colorsys
except ModuleNotFoundError:
    from . import colorsys  # Anki add-on
try:
    import argparse
except ModuleNotFoundError:
    from . import argparse  # Anki add-on


# Function that I want to have after refactoring, currently implemented using
# existing interface

def colorize(character, mode="spectrum", saturation=0.95, value=0.75,
             image_size=327):
    """
    Returns a string containing the colorized svg for the character

    >>> svg = colorize('a', mode='spectrum', image_size=100,
    ...                saturation=0.95, value=0.75)
    >>> 'has been modified' in svg
    True

    """
    arg_fmt = '--mode {} --saturation {} --value {} --image-size {}'
    arg_string = arg_fmt.format(mode, saturation, value, image_size)
    colorizer = KanjiColorizer(arg_string)

    return colorizer.get_colored_svg(character)


# Setup

source_directory = os.path.join(os.path.dirname(__file__),
                                'data', 'kanjivg', 'kanji')


# Classes

class KanjiVG(object):
    '''
    Class to create kanji objects containing KanjiVG data and some more
    basic qualities of the character
    '''
    def __init__(self, character, variant=''):
        '''
        Create a new KanjiVG object

        Either give just the character

        >>> k1 = KanjiVG('漢')
        >>> print(k1.character)
        漢
        >>> k1.variant
        ''

        Or if the character has a variant, give that as a second
        argument

        >>> k2 = KanjiVG('字', 'Kaisho')
        >>> print(k2.character)
        字
        >>> k2.variant
        'Kaisho'

        Raises InvalidCharacterError if the character and variant don't
        correspond to known data

        >>> k = KanjiVG('Л')
        Traceback (most recent call last):
            ...
        kanjicolorizer.colorizer.InvalidCharacterError: ('\\u041b', '')

        '''
        self.character = character
        self.variant = variant
        if self.variant is None:
            self.variant = ''
        try:
            with open(os.path.join(source_directory, self.ascii_filename),
                      'r', encoding='utf-8') as f:
                self.svg = f.read()
        except IOError as e:  # file not found
            if e.errno == FILE_NOT_FOUND:
                raise InvalidCharacterError(character, variant) from e
            else:
                raise

    @classmethod
    def _create_from_filename(cls, filename):
        '''
        Alternate constructor that uses a KanjiVG filename; used by
        get_all().

        >>> k = KanjiVG._create_from_filename('00061.svg')
        >>> k.character
        'a'
        '''
        m = re.match('^([0-9a-f]*)-?(.*?).svg$', filename)
        return cls(chr(int(m.group(1), 16)), m.group(2))

    @property
    def ascii_filename(self):
        '''
        An SVG filename in ASCII using the same format KanjiVG uses.

        >>> k = KanjiVG('漢')
        >>> k.ascii_filename
        '06f22.svg'

        May raise InvalidCharacterError for some kinds of invalid
        character/variant combinations; this should only happen during
        KanjiVG object initialization.
        '''
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
        '''
        An SVG filename that uses the unicode character

        >>> k = KanjiVG('漢')
        >>> print(k.character_filename)
        漢.svg
        '''
        if not self.variant:
            return '%s.svg' % self.character
        else:
            return '%s-%s.svg' % (self.character, self.variant)

    @classmethod
    def get_all(cls):
        '''
        Returns a complete list of KanjiVG objects; everything there is
        data for

        >>> kanji_list = KanjiVG.get_all()
        >>> kanji_list[0].__class__.__name__
        'KanjiVG'
        '''
        kanji = []
        for file in os.listdir(source_directory):
            kanji.append(cls._create_from_filename(file))
        return kanji


class KanjiColorizer:
    """
    Class that creates colored stroke order diagrams out of kanjivg
    data, and writes them to file.

    Initialize with no arguments to take the command line settings, or
    an empty string to use default settings

    Settings can set by initializing with a string in the same format as
    the command line.
    >>> test_output_dir = os.path.join('test', 'colorized-kanji')
    >>> my_args = ' '.join(['--characters', 'aあ漢',
    ...                     '--output', test_output_dir])
    >>> kc = KanjiColorizer(my_args)

    To get an svg for a single character
    >>> colored_svg = kc.get_colored_svg('a')

    To create a set of diagrams:
    >>> kc.write_all()

    Note: This class is in the middle of having stuff that shouldn't be
    included factored out.  Some things have already been moved to the
    KanjiVG class; more stuff will move.
    """

    def __init__(self, argstring=''):
        '''
        Creates a new instance of KanjiColorizer, which stores settings
        and provides various methods to produce colored kanji SVGs.

        Takes an option alrgument of with an argument string; see
        read_arg_string documentation for information on how this is
        used.
        '''
        self._init_parser()
        self.read_arg_string(argstring)

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
                    choices=['spectrum', 'contrast'],
                    help='spectrum: color progresses evenly through the'
                        ' spectrum; nice for seeing the way the kanji is'
                        ' put together at a glance, but has the disadvantage'
                        ' of using similar colors for consecutive strokes '
                        'which can make it less clear which number goes '
                        'with which stroke.  contrast: maximizes contrast '
                        'among any group of consecutive strokes, using the '
                        'golden ratio; also provides consistency by using '
                        'the same sequence for every kanji.  (default: '
                        '%(default)s)')
        self._parser.add_argument('--saturation', default=0.95, type=float,
                    help='a decimal indicating saturation where 0 is '
                        'white/gray/black and 1 is completely  colorful '
                        '(default: %(default)s)')
        self._parser.add_argument('--group-mode', action='store_true',
                    help='Color kanji groups instead of stroke by stroke '
                        '(default: %(default)s)')
        self._parser.add_argument('--value', default=0.75, type=float,
                    help='a decimal indicating value where 0 is black '
                        'and 1 is colored or white '
                        '(default: %(default)s)')
        self._parser.add_argument('--image-size', default=327, type=int,
                    help="image size in pixels; they're square so this "
                        'will be both height and width '
                        '(default: %(default)s)')
        self._parser.add_argument('--characters', type=str,
                    help='a list of characters to include, without '
                         'spaces; if this option is used, no variants '
                         'will be included; if this option is not '
                         'used, all characters will be included, '
                         'including variants')
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
        'contrast'
        """
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
        '<?xml version="1.0" encoding="UTF-8"?>'
        >>> svg.find('00061')
        1780
        >>> svg.find('has been modified')
        54

        """
        svg = KanjiVG(character).svg
        svg = self._modify_svg(svg)
        return svg

    def write_all(self):
        """
        Converts all svgs (or only those specified with the --characters
        option) and prints them to files in the destination directory.

        Silently ignores invalid characters.

        >>> test_output_dir = os.path.join('test', 'colorized-kanji')
        >>> kc = KanjiColorizer(' '.join(['--characters', 'aあ漢',
        ...                               '--output', test_output_dir]))
        >>> kc.write_all()

        These should be the correct files:
        >>> import difflib
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
        >>> import shutil
        >>> shutil.rmtree(test_output_dir)

        """
        self._setup_dst_dir()
        if not self.settings.characters:
            characters = KanjiVG.get_all()
        else:
            characters = []
            if ',' in self.settings.characters \
                    and len(self.settings.characters) > 1:
                self.settings.characters = self.settings.characters.split(',')
            for c in self.settings.characters:
                var = ''
                if '-' in c:
                    varsplit = c.split('-')
                    c = varsplit[0]
                    var = '-'.join(varsplit[1:])
                try:
                    characters.append(KanjiVG(c, var))
                except InvalidCharacterError:
                    pass
        for kanji in characters:
            svg = self._modify_svg(kanji.svg)
            dst_file_path = os.path.join(self.settings.output_directory,
                self._get_dst_filename(kanji))
            with open(dst_file_path, 'w', encoding='utf-8') as f:
                f.write(svg)

    def _modify_svg(self, svg):
        """
        Applies all desired changes to the SVG

        >>> kc = KanjiColorizer('')
        >>> original_svg = open(
        ...    os.path.join(source_directory, '06f22.svg'),
        ...    'r', encoding='utf-8').read()
        >>> desired_svg = open(
        ...    os.path.join(
        ...        'test', 'default_results', 'kanji-colorize-spectrum',
        ...        '漢.svg'),
        ...    'r', encoding='utf-8').read()
        >>> import difflib
        >>> for line in difflib.context_diff(
        ...        kc._modify_svg(original_svg).splitlines(1),
        ...        desired_svg.splitlines(1)):
        ...     print(line)
        ...
        """
        svg = self._color_svg(svg)

        if self.settings.group_mode:
            svg = self._remove_strokes(svg)

        svg = self._resize_svg(svg)
        svg = self._comment_copyright(svg)
        return svg

    def _remove_strokes(self, svg):
        return re.sub("<text.*?</text>", "", svg)

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

    def _color_svg(self, svg):
        """
        Color the svg with colors from _color_generator, which uses
        configuration from settings

        This adds a style attribute to path (stroke) and text (stroke
        number) elements.  Both of these already have attributes, so we
        can expect a space.  Not all SVGs include stroke numbers.

        >>> svg = "<svg><path /><path /><text >1</text><text >2</text></svg>"
        >>> kc = KanjiColorizer('')
        >>> kc._color_svg(svg)
        '<svg><path style="stroke: #bf0909;" /><path style="stroke: #09bfbf;" /><text style="fill: #bf0909;" >1</text><text style="fill: #09bfbf;" >2</text></svg>'
        >>> svg = "<svg><path /><path /></svg>"
        >>> kc._color_svg(svg)
        '<svg><path style="stroke: #bf0909;" /><path style="stroke: #09bfbf;" /></svg>'
        """
        color_iterator = self._color_generator(self._stroke_count(svg))

        def path_match(match_object):
            return (
                match_object.re.pattern +
                'style="stroke: ' +
                next(color_iterator) + ';" ')

        def text_match(match_object):
            return (
                match_object.re.pattern +
                'style="fill: ' +
                next(color_iterator) + ';" ')

        if not self.settings.group_mode:
            svg = re.sub('<path ', path_match, svg)
            return re.sub('<text ', text_match, svg)
        else:
            found = False
            depth = 0
            iopen = 0
            lines = svg.split('\n')

            nsvg=''
            for line in lines:
                if line.find('<g ') != -1 or line.find('</g>') != -1:
                    if not found:
                        if line.find("<g ") != -1 and line.find('kvg:element') != -1:
                            found = True
                            #print "first element tag found"
                    else:
                        if line.find("</g>") != -1:
                            if iopen != 0 and iopen == depth:
                                iopen = 0
                                #print 'color group closed'
                            depth-=1

                        if line.find("<g ") != -1:
                            depth+=1
                            if iopen == 0 and line.find('kvg:element') != -1:
                                iopen = depth
                                line = re.sub('<g ', path_match, line)
                                #print 'color group opened'

                nsvg+=line+"\n"
            return nsvg

    def _comment_copyright(self, svg):
        """
        Add a comment about what this script has done to the copyright notice

        >>> svg = '''<!--
        ... Copyright (C) copyright holder (etc.)
        ... -->
        ... <svg> <! content> </svg>
        ... '''

        This contains the notice:

        >>> kc = KanjiColorizer('')
        >>> kc._comment_copyright(svg).count('This file has been modified')
        1

        And depends on the settings it is run with:

        >>> kc = KanjiColorizer('--mode contrast')
        >>> kc._comment_copyright(svg).count('contrast')
        1
        >>> kc = KanjiColorizer('--mode spectrum')
        >>> kc._comment_copyright(svg).count('contrast')
        0
        """
        note = """This file has been modified from the original version by the kanji_colorize.py
script (available at http://github.com/cayennes/kanji-colorize) with these
settings:
    mode: """ + self.settings.mode + """
    saturation: """ + str(self.settings.saturation) + """
    value: """ + str(self.settings.value) + """
    image_size: """ + str(self.settings.image_size) + """
It remains under a Creative Commons-Attribution-Share Alike 3.0 License.

The original SVG has the following copyright:

"""
        place_before = "Copyright (C)"
        return svg.replace(place_before, note + place_before)

    def _resize_svg(self, svg):
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
        ratio = repr(float(self.settings.image_size) / 109)
        svg = svg.replace(
            '109" height="109" viewBox="0 0 109 109',
            '{0}" height = "{0}" viewBox="0 0 {0} {0}'.format(
                str(self.settings.image_size)))
        svg = re.sub(
            '(<g id="kvg:Stroke.*?)(>)',
            r'\1 transform="scale(' + ratio + ',' + ratio + r')"\2',
            svg)
        return svg

    # Private utility methods

    def _stroke_count(self, svg):
        """
        Return the number of strokes in the svg, based on occurences of
        "<path "

        >>> svg = "<svg><path /><path /><path /></svg>"
        >>> kc = KanjiColorizer('')
        >>> kc._stroke_count(svg)
        3
        """
        return len(re.findall('<path ', svg))

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
        return '#%02x%02x%02x' % tuple([int(i * 255) for i in color])

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
            for i in 2 * list(range(n)):
                yield self._hsv_to_rgbhexcode(i * angle,
                    self.settings.saturation, self.settings.value)
        else:  # spectrum is default
            for i in 2 * list(range(n)):
                yield self._hsv_to_rgbhexcode(float(i) / n,
                    self.settings.saturation, self.settings.value)


# Exceptions

class Error(Exception):
    '''
    Base class for this module's exceptions
    '''
    pass


class InvalidCharacterError(Error):
    '''
    Exception thrown when trying to initialize or use a character that
    there isn't data for
    '''
    pass


# Test if run

if __name__ == "__main__":
    import doctest
    doctest.testmod()
