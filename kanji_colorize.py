#! /usr/bin/python2

# kanji_colorize.py makes KanjiVG data into colored stroke order diagrams
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

parser = argparse.ArgumentParser(description='Create a set of colored '
                                             'stroke order svgs')
parser.add_argument('--mode', default='spectrum',
                    choices=['spectrum', 'contrast'],
                    help='spectrum: color progresses evenly through the'
                    ' spectrum; nice for seeing the way the kanji is '
                    'put together at a glance, but has the disadvantage'
                    ' of using similr colors for consecutive strokes '
                    'which can make it less clear which number goes '
                    'with which stroke.  contrast: maximizes contrast '
                    'among any group of consecutive strokes, using the '
                    'golden ratio; also provides consistency by using '
                    'the same sequence for every kanji.  (default: '
                    '%(default)s)')
parser.add_argument('--saturation', default=0.95, type=float,
                    help='a decimal indicating saturation where 0 is '
                    'white/gray/black and 1 is completely  colorful '
                    '(default: %(default)s)')
parser.add_argument('--value', default=0.75, type=float,
                    help='a decimal indicating value where 0 is black '
                    'and 1 is colored or white '
                    '(default: %(default)s)')
parser.add_argument('--image-size', default=327, type=int,
                    help="image size in pixels; they're square so this "
                    'will be both height and width'
                    '(default: %(default)s)')
parser.add_argument('--filename-mode', default='character',
                    choices=['character', 'code'],
                    help='character: rename the files to use the '
                    'unicode character as a filename.  code: leave it '
                    'as the code.  '
                    '(default: %(default)s)')
parser.add_argument('-s', '--source-directory', 
                    default=os.path.join(os.path.dirname(__file__),
                                         'kanjivg','kanji')),
parser.add_argument('-o', '--output-directory',
                    default='colorized-kanji')

# Utility functions for working with colors

def hsv_to_rgbhexcode(h, s, v):
    """
Convert an h, s, v color into rgb form #000000

>>> hsv_to_rgbhexcode(0, 0, 0)
'#000000'
>>> hsv_to_rgbhexcode(2.0/3, 1, 1)
'#0000ff'
>>> hsv_to_rgbhexcode(0.5, 0.95, 0.75)
'#09bfbf'
"""
    color = colorsys.hsv_to_rgb(h, s, v)
    return '#%02x%02x%02x' % tuple([i * 255 for i in color])

def color_generator(args, n):
    """
Create an iterator that loops through n colors twice (so that they can be
used for both strokes and stroke numbers) using mode, saturation, and
value from the args namespace

>>> my_args = parser.parse_args(
...            '--mode contrast --saturation 1 --value 1'.split())
>>> [color for color in color_generator(my_args, 3)]
['#ff0000', '#004aff', '#94ff00', '#ff0000', '#004aff', '#94ff00']
>>> my_args = parser.parse_args(
...            '--mode spectrum --saturation 0.95 --value 0.75'.split())
>>> [color for color in color_generator(my_args, 2)]
['#bf0909', '#09bfbf', '#bf0909', '#09bfbf']
"""
    if (args.mode == "contrast"):
        angle = 0.618033988749895 # conjugate of the golden ratio
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(
                i * angle, args.saturation, args.value)
    else: # spectrum is default
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(
                float(i)/n, args.saturation, args.value)

# Utility functions for working with SVG text

def stroke_count(svg):
    """
Return the number of strokes in the svg, based on occurences of "<path "

>>> svg = "<svg><path /><path /><path /></svg>"
>>> stroke_count(svg)
3
"""
    return len(re.findall('<path ', svg))

# Modify SVG text

def color_svg(args, svg):
    """
Color the svg with colors from color_generator, which uses configuration
from the args namespace

This adds a style attribute to path (stroke) and text (stroke number)
elements.  Both of these already have attributes, so we can expect a
space.  Not all SVGs include stroke numbers.

>>> svg = "<svg><path /><path /><text >1</text><text >2</text></svg>"
>>> my_args = parser.parse_args(''.split())
>>> color_svg(my_args, svg)
'<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /><text style="stroke:#bf0909" >1</text><text style="stroke:#09bfbf" >2</text></svg>'
>>> svg = "<svg><path /><path /></svg>"
>>> color_svg(my_args, svg)
'<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /></svg>'
"""
    color_iterator = color_generator(args, stroke_count(svg))
    def color_match(match_object):
        return (
            match_object.re.pattern +  
            'style="stroke:' + 
            next(color_iterator) + '" ')
    svg = re.sub('<path ', color_match, svg)
    return re.sub('<text ', color_match, svg)

def resize_svg(args, svg):
    """
Resize the svg according to args.image_size, by changing the 109s
in the <svg> attributes, and adding a transform scale to the groups
enclosing the strokes and stroke numbers

>>> my_args = parser.parse_args('--image-size 100'.split())
>>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g></svg>'
>>> resize_svg(my_args, svg)
'<svg  width="100" height = "100" viewBox="0 0 100 100"><!109><g id="kvg:StrokePaths_" transform="scale(0.9174311926605505,0.9174311926605505)"><path /></g></svg>'
>>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g><g id="kvg:StrokeNumbers_"><text /></g></svg>'
>>> my_args = parser.parse_args('--image-size 327'.split())
>>> resize_svg(my_args, svg)
'<svg  width="327" height = "327" viewBox="0 0 327 327"><!109><g id="kvg:StrokePaths_" transform="scale(3.0,3.0)"><path /></g><g id="kvg:StrokeNumbers_" transform="scale(3.0,3.0)"><text /></g></svg>'
"""
    ratio = `float(args.image_size) / 109`
    svg = svg.replace(
        '109" height="109" viewBox="0 0 109 109', 
        '{0}" height = "{0}" viewBox="0 0 {0} {0}'.format(
            str(args.image_size)))
    svg = re.sub(
        '(<g id="kvg:Stroke.*?)(>)', 
        r'\1 transform="scale(' + ratio + ',' + ratio + r')"\2', 
        svg)
    return svg

def comment_copyright(args, svg):
    """
Add a comment about what this script has done to the copyright notice

>>> svg = '''<!--
... Copyright (C) copyright holder (etc.)
... -->
... <svg> <! content> </svg>
... '''

This contains the notice:

>>> my_args = parser.parse_args(''.split())
>>> comment_copyright(my_args, svg).count('This file has been modified')
1

And depends on the settings it is run with:

>>> my_args = parser.parse_args('--mode contrast'.split())
>>> comment_copyright(my_args, svg).count('contrast')
1
>>> my_args = parser.parse_args('--mode spectrum'.split())
>>> comment_copyright(my_args, svg).count('contrast')
0
"""
    note = """This file has been modified from the original version by the kanji_colorize.py
script (available at http://github.com/cayennes/kanji-colorize) with these 
settings: 
    mode: """ + args.mode + """
    saturation: """ + str(args.saturation) + """
    value: """ + str(args.value) + """
    image_size: """ + str(args.image_size) + """
It remains under a Creative Commons-Attribution-Share Alike 3.0 License.

The original SVG has the following copyright:

"""
    place_before = "Copyright (C)"
    return svg.replace(place_before, note + place_before)

def modify_svg(args, svg):
    """
Applies all desired changes to the SVG

>>> import difflib
>>> my_args = parser.parse_args(''.split())
>>> original_svg = open(
...    os.path.join('test', 'kanjivg', 'kanji', '06f22.svg'), 
...    'r').read()
>>> desired_svg = open(
...    os.path.join(
...        'test', 'default_results', 'kanji-colorize-spectrum', 
...        u'\u6f22.svg'), 
...    'r').read()
>>> for line in difflib.context_diff(
...        modify_svg(my_args, original_svg).splitlines(1), 
...        desired_svg.splitlines(1)):
...     print(line)
...
"""
    svg = color_svg(args, svg)
    svg = resize_svg(args, svg)
    svg = comment_copyright(args, svg)
    return svg

# Functions to work with files and directories

def convert_file_name(filename):
    r"""
Convert unicode code in filename to actual character

>>> convert_file_name('00063.svg')
u'c.svg'
>>> convert_file_name('06f22.svg')
u'\u6f22.svg'
>>> convert_file_name('05b57-Kaisho.svg')
u'\u5b57-Kaisho.svg'
"""
    def hex_to_unicode_char(match_object):
        'local function used for a call to re.sub'
        return unichr(int(match_object.group(0), 16))
    return re.sub('^[0-9a-fA-F]*', hex_to_unicode_char, filename)

def get_dst_filename(args, src_filename):
    """
Return the correct filename, based on args.filename-mode

>>> my_args = parser.parse_args('--filename-mode code'.split())
>>> get_dst_filename(my_args, '00063.svg')
'00063.svg'
>>> my_args = parser.parse_args('--filename-mode character'.split())
>>> get_dst_filename(my_args, '00063.svg')
u'c.svg'
"""
    if (args.filename_mode == 'character'):
        return convert_file_name(src_filename)
    else:
        return src_filename

def setup_dst_dir(args):
    """
Creates the destination directory args.output_directory if necessary

(Set up the doctest environment)
>>> current_directory = os.path.abspath(os.path.curdir)
>>> os.mkdir(os.path.join('test', 'doctest-tmp'))
>>> os.chdir(os.path.join('test', 'doctest-tmp'))
>>> my_args = parser.parse_args(''.split())

This creates the directory
>>> setup_dst_dir(my_args)
>>> os.listdir(os.path.curdir)
['colorized-kanji']

But doesn't do anything or throw an error if it already exists
>>> setup_dst_dir(my_args)
>>> os.listdir(os.path.curdir)
['colorized-kanji']

(done; reseting environment for other doctests)
>>> os.rmdir(my_args.output_directory)
>>> os.chdir(os.path.pardir)
>>> os.rmdir('doctest-tmp')
>>> os.chdir(current_directory)
"""
    dst_dir = args.output_directory
    if not (os.path.exists(dst_dir)):
        os.mkdir(dst_dir)

# Do conversions

def convert_all(args):
    """
Converts all svgs, and prints them to files in the destination directory

>>> test_input_dir = os.path.join('test', 'kanjivg', 'kanji')
>>> test_output_dir = os.path.join('test', 'colorized-kanji')
>>> my_args = parser.parse_args(['--source-directory', test_input_dir,
...                           '--output', test_output_dir])
>>> convert_all(my_args)

These should be the correct files:
>>> import difflib
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
>>> import shutil
>>> shutil.rmtree(test_output_dir)

"""
    setup_dst_dir(args)
    for src_filename in os.listdir(args.source_directory):
        with open(os.path.join(args.source_directory, src_filename), 
                  'r') as f:
            svg = f.read()
        svg = modify_svg(args, svg)
        dst_file_path = os.path.join(
            args.output_directory, get_dst_filename(args, src_filename))
        with open(dst_file_path, 'w') as f:
            f.write(svg)

if __name__ == "__main__":
    args = parser.parse_args()
    convert_all(args)
