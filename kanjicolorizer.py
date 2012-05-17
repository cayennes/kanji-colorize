#! /usr/bin/python2

# kanjicolorizer.py is part of kanji-colorize which makes KanjiVG data
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

import os
import colorsys
import re
import argparse

class KanjiColorizer:
    """
    Class that creates colored stroke order diagrams out of kanjivg
    data, and writes them to file.

    Initialize with no arguments to take the command line settings, or
    an empty string to use default settings

    Settings can set by initializing with a string in the same format as
    the command line.
    >>> test_input_dir = os.path.join('test', 'kanjivg', 'kanji')
    >>> test_output_dir = os.path.join('test', 'colorized-kanji')
    >>> my_args = ' '.join(['--source-directory', test_input_dir, 
    ...                     '--output', test_output_dir])
    >>> kc = KanjiColorizer(my_args)

    To get an svg for a single character
    >>> colored_svg = kc.get_colored_svg('a')

    To create a set of diagrams:
    >>> kc.write_all()

    If you want to convert a filename from hexcode to character form:
    >>> kc.convert_filename('ac0de.svg')
    u'\U000ac0de.svg'

    """

    def __init__(self, argstring=''):
        self._init_parser()
        self.read_arg_string(argstring)
    
    def _init_parser(self):
        r"""
        Initializes argparse.ArgumentParser self._parser

        >>> kc = KanjiColorizer()
        
        To show that is really is creating it:
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
                        ' of using similr colors for consecutive strokes '
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
        self._parser.add_argument('--value', default=0.75, type=float,
                    help='a decimal indicating value where 0 is black '
                        'and 1 is colored or white '
                        '(default: %(default)s)')
        self._parser.add_argument('--image-size', default=327, type=int,
                    help="image size in pixels; they're square so this "
                        'will be both height and width'
                        '(default: %(default)s)')
        self._parser.add_argument('--filename-mode', default='character',
                    choices=['character', 'code'],
                    help='character: rename the files to use the '
                        'unicode character as a filename.  code: leave it '
                        'as the code.  '
                        '(default: %(default)s)')
        self._parser.add_argument('-s', '--source-directory', 
                    default=os.path.join(os.path.dirname(__file__),
                                         'kanjivg','kanji')),
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
        >>> svg = kc.get_colored_svg('c')
        >>> svg.splitlines()[0]
        '<?xml version="1.0" encoding="UTF-8"?>'
        >>> svg.find('00063')
        1783
        >>> svg.find('has been modified')
        54

        """
        svg = self._get_original_svg(character)
        svg = self._modify_svg(svg)
        return svg
    
    def write_all(self):
        """
        Converts all svgs, and prints them to files in the destination
        directory
        
        >>> test_input_dir = os.path.join('test', 'kanjivg', 'kanji')
        >>> test_output_dir = os.path.join('test', 'colorized-kanji')
        >>> kc = KanjiColorizer(' '.join(['--source-directory', 
        ...     test_input_dir, '--output', test_output_dir]))
        >>> kc.write_all()

        These should be the correct files:
        >>> for file in os.listdir(test_output_dir):
        ...     our_svg = open(
        ...         os.path.join(test_output_dir, file), 'r').read()
        ...     desired_svg = open(
        ...         os.path.join('test', 'default_results', 
        ...             'kanji-colorize-spectrum',  file), 'r').read()
        ...     for line in difflib.context_diff(our_svg.splitlines(1), 
        ...            desired_svg.splitlines(1)):
        ...         print(line)
        ...

        Clean up doctest
        >>> shutil.rmtree(test_output_dir)

        """
        self._setup_dst_dir()
        for src_filename in os.listdir(self.settings.source_directory):
            with open(os.path.join(self.settings.source_directory, 
                    src_filename), 'r') as f:
                svg = f.read()
            svg = self._modify_svg(svg)
            dst_file_path = os.path.join(self.settings.output_directory, 
                self._get_dst_filename(src_filename))
            with open(dst_file_path, 'w') as f:
                f.write(svg)

    def _modify_svg(self, svg):
        """
        Applies all desired changes to the SVG

        >>> kc = KanjiColorizer('')
        >>> original_svg = open(
        ...    os.path.join('test', 'kanjivg', 'kanji', '06f22.svg'), 
        ...    'r').read()
        >>> desired_svg = open(
        ...    os.path.join(
        ...        'test', 'default_results', 'kanji-colorize-spectrum', 
        ...        u'\u6f22.svg'), 
        ...    'r').read()
        >>> for line in difflib.context_diff(
        ...        kc._modify_svg(original_svg).splitlines(1), 
        ...        desired_svg.splitlines(1)):
        ...     print(line)
        ...
        """
        svg = self._color_svg(svg)
        svg = self._resize_svg(svg)
        svg = self._comment_copyright(svg)
        return svg

    def convert_filename(self, filename):
        r"""
        Convert unicode code in filename to actual character
        
        >>> kc = KanjiColorizer('')
        >>> kc.convert_filename('00063.svg')
        u'c.svg'
        >>> kc.convert_filename('06f22.svg')
        u'\u6f22.svg'
        >>> kc.convert_filename('05b57-Kaisho.svg')
        u'\u5b57-Kaisho.svg'
        """
        def hex_to_unicode_char(match_object):
            'local function used for a call to re.sub'
            return unichr(int(match_object.group(0), 16))
        return re.sub('^[0-9a-fA-F]*', hex_to_unicode_char, filename)

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
        dst_dir = self.settings.output_directory
        if not (os.path.exists(self.settings.output_directory)):
            os.mkdir(self.settings.output_directory)

    def _get_dst_filename(self, src_filename):
        """
        Return the correct filename, based on args.filename-mode

        >>> kc = KanjiColorizer('--filename-mode code')
        >>> kc._get_dst_filename('00063.svg')
        '00063.svg'
        >>> kc = KanjiColorizer('--filename-mode character')
        >>> kc._get_dst_filename('00063.svg')
        u'c.svg'

        """
        if (self.settings.filename_mode == 'character'):
            return self.convert_filename(src_filename)
        else:
            return src_filename

    def _get_original_svg(self, character):
        """
        Get the unmodified svg text for given character

        >>> kc = KanjiColorizer()
        >>> svg = kc._get_original_svg('c')
        >>> svg.splitlines()[0]
        '<?xml version="1.0" encoding="UTF-8"?>'
        >>> svg.find('00063')
        1418

        """
        with open(os.path.join(self.settings.source_directory,
                self._get_character_filename(character))) as f:
            svg = f.read()
        return svg

    def _get_character_filename(self, character):
        """
        Get the original filename for character

        >>> kc = KanjiColorizer()
        >>> kc._get_character_filename('c')
        '00063.svg'

        """
        return '%05x.svg' % ord(character)

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
        '<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /><text style="stroke:#bf0909" >1</text><text style="stroke:#09bfbf" >2</text></svg>'
        >>> svg = "<svg><path /><path /></svg>"
        >>> kc._color_svg(svg)
        '<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /></svg>'
        """
        color_iterator = self._color_generator(self._stroke_count(svg))
        def color_match(match_object):
            return (
                match_object.re.pattern +  
                'style="stroke:' + 
                next(color_iterator) + '" ')
        svg = re.sub('<path ', color_match, svg)
        return re.sub('<text ', color_match, svg)


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
        ratio = `float(self.settings.image_size) / 109`
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
            angle = 0.618033988749895 # conjugate of the golden ratio
            for i in 2 * range(n):
                yield self._hsv_to_rgbhexcode(i * angle, 
                    self.settings.saturation, self.settings.value)
        else: # spectrum is default
            for i in 2 * range(n):
                yield self._hsv_to_rgbhexcode(float(i)/n, 
                    self.settings.saturation, self.settings.value)

if __name__ == "__main__":
    import doctest
    import sys
    import difflib
    import shutil
    doctest.testmod()
