#! /usr/bin/python

# kanji_colorize.py makes KanjiVG data into colored stroke order diagrams
#
# Copyright 2012 Cayenne Boyer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Usage: see README file

# CONFIGURATION VARIABLES

config = dict( 
# mode: 
# * spectrum: color progresses evenly through the spectrum.  This is
#             nice for seeing the way the kanji is put together at a
#             glance, but has the disadvantage of using similar colors
#             for consecutive strokes which can make it less clear which
#             number goes with which stroke 
# * contrast: maximizes contrast among any group of consecutive strokes,
#             by using the golden ratio
mode = "spectrum",

# saturation and value, as numbers between 0 and 1
saturation = 0.95,
value = 0.75,

# image size in pixels
image_size = 327,

# rename files to use characters rather than codes; set to True or False
character_file_names = True,

)
# END OF CONFIGURATION VARIABLES

# make sure config variables are in the right format
config["mode"] = config["mode"].lower()
config["saturation"] = float(config["saturation"])
config["value"] = float(config["value"])
config["image_size"] = int(config["image_size"])

# BEGIN SCRIPT

# Things used for running

import os
import colorsys
import re

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

def color_generator(n):
    """
Create an iterator that loops through n colors twice (so that they can be
used for both strokes and stroke numbers) using mode, saturation, and
value in the config dictionary to determine what colors to produce.

>>> config.update({'mode': 'contrast', 'saturation': 1, 'value':1})
>>> [color for color in color_generator(3)]
['#ff0000', '#004aff', '#94ff00', '#ff0000', '#004aff', '#94ff00']
>>> config.update({'mode': 'spectrum', 'saturation': 0.95, 'value':0.75})
>>> [color for color in color_generator(2)]
['#bf0909', '#09bfbf', '#bf0909', '#09bfbf']
"""
    if (config["mode"] == "contrast"):
        angle = 0.618033988749895 # conjugate of the golden ratio
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(
                i * angle, config["saturation"], config["value"])
    else: # spectrum is default
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(
                float(i)/n, config["saturation"], config["value"])

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

def color_svg(svg):
    """
Color the svg with colors from color_generator, which uses config
variables.

This adds a style attribute to path (stroke) and text (stroke number)
elements.  Both of these already have attributes, so we can expect a
space.  Not all SVGs include stroke numbers.

>>> svg = "<svg><path /><path /><text >1</text><text >2</text></svg>"
>>> color_svg(svg)
'<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /><text style="stroke:#bf0909" >1</text><text style="stroke:#09bfbf" >2</text></svg>'
>>> svg = "<svg><path /><path /></svg>"
>>> color_svg(svg)
'<svg><path style="stroke:#bf0909" /><path style="stroke:#09bfbf" /></svg>'
"""
    color_iterator = color_generator(stroke_count(svg))
    def color_match(match_object):
        return (
            match_object.re.pattern +  
            'style="stroke:' + 
            next(color_iterator) + '" ')
    svg = re.sub('<path ', color_match, svg)
    return re.sub('<text ', color_match, svg)

def resize_svg(svg):
    """
Resize the svg according to config["image_size"], by changing the 109s
in the <svg> attributes, and adding a transform scale to the groups
enclosing the strokes and stroke numbers

>>> config["image_size"] = 100
>>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g></svg>'
>>> resize_svg(svg)
'<svg  width="100" height = "100" viewBox="0 0 100 100"><!109><g id="kvg:StrokePaths_" transform="scale(0.9174311926605505,0.9174311926605505)"><path /></g></svg>'
>>> svg = '<svg  width="109" height="109" viewBox="0 0 109 109"><!109><g id="kvg:StrokePaths_"><path /></g><g id="kvg:StrokeNumbers_"><text /></g></svg>'
>>> config["image_size"] = 327
>>> resize_svg(svg)
'<svg  width="327" height = "327" viewBox="0 0 327 327"><!109><g id="kvg:StrokePaths_" transform="scale(3.0,3.0)"><path /></g><g id="kvg:StrokeNumbers_" transform="scale(3.0,3.0)"><text /></g></svg>'
"""
    ratio = `float(config["image_size"]) / 109`
    svg = svg.replace(
        '109" height="109" viewBox="0 0 109 109', 
        '{0}" height = "{0}" viewBox="0 0 {0} {0}'.format(
            `config["image_size"]`))
    svg = re.sub(
        '(<g id="kvg:Stroke.*?)(>)', 
        r'\1 transform="scale(' + ratio + ',' + ratio + r')"\2', 
        svg)
    return svg

def comment_copyright(svg):
    """
Add a comment about what this script has done to the copyright notice

>>> svg = '''<!--
... Copyright (C) copyright holder (etc.)
... -->
... <svg> <! content> </svg>
... '''

This contains the notice:

>>> comment_copyright(svg).count('This file has been modified')
1

And depends on the settings it is run with:

>>> config['mode'] = 'contrast'
>>> comment_copyright(svg).count('contrast')
1
>>> config['mode'] = 'spectrum'
>>> comment_copyright(svg).count('contrast')
0
"""
    note = """This file has been modified from the original version by the kanji_colorize.py
script (available at http://github.com/cayennes/kanji-colorize) with these 
settings: 
    mode: """ + config["mode"] + """
    saturation: """ + `config["saturation"]` + """
    value: """ + `config["value"]` + """
    image_size: """ + `config["image_size"]` + """
It remains under a Creative Commons-Attribution-Share Alike 3.0 License.

The original SVG has the following copyright:

"""
    place_before = "Copyright (C)"
    return svg.replace(place_before, note + place_before)

def modify_svg(svg):
    """
Applies all desired changes to the SVG

>>> import difflib
>>> original_svg = open(
...    os.path.join('test', 'kanjivg', 'kanji', '06f22.svg'), 
...    'r').read()
>>> desired_svg = open(
...    os.path.join(
...        'test', 'default_results', 'kanji-colorize-spectrum', 
...        u'\u6f22.svg'), 
...    'r').read()
>>> for line in difflib.context_diff(
...        modify_svg(original_svg).splitlines(1), 
...        desired_svg.splitlines(1)):
...     print(line)
...
"""
    svg = color_svg(svg)
    svg = resize_svg(svg)
    svg = comment_copyright(svg)
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

def get_dst_filename(src_filename):
    """
Return the correct filename, based on config["character_file_names"]

>>> config["character_file_names"] = False
>>> get_dst_filename('00063.svg')
'00063.svg'
>>> config["character_file_names"] = True
>>> get_dst_filename('00063.svg')
u'c.svg'
"""
    if (config["character_file_names"]):
        return convert_file_name(src_filename)
    else:
        return src_filename


def get_src_dir():
    """
Look in the directories listed in possible_dirs, in order, and use the
first one that exists.  Returns path in a form appropriate for the
current operating system.

(this line is for resetting the doctest environment)
>>> current_directory = os.path.abspath(os.path.curdir)

From a directory containing kanjivg/kanji

>>> os.chdir('test')
>>> if os.name == 'posix':
...     get_src_dir() == 'kanjivg/kanji'
... elif os.name == 'nt':
...     get_src_dir() == r'kanjvg\\kanji'
...
True

Then containing 'kanji'

>>> os.chdir('kanjivg')
>>> get_src_dir() == 'kanji'
True

From a sibling directory of kanjivg/kanji

>>> os.chdir(os.path.join(os.path.pardir, 'default_results'))
>>> if os.name == 'posix':
...     get_src_dir() == '../kanjivg/kanji'
... elif os.name == 'nt':
...     get_src_dir() == r'..\\kanjvg\\kanji'
...
True

(done; reseting environment for doctest)
>>> os.chdir(current_directory)

"""
    possible_dirs = [
        'kanji', 
        os.path.join('kanjivg', 'kanji'), 
        os.path.join(os.path.pardir,'kanjivg','kanji')]
    for dir in possible_dirs:
        if (os.path.exists(dir)):
            return dir

def get_dst_dir():
    """
returns the destination directory name, which is kanji-colorize-
followed by the mode.

>>> config["mode"] = "contrast"
>>> get_dst_dir()
'kanji-colorize-contrast'
>>> config["mode"] = "spectrum"
>>> get_dst_dir()
'kanji-colorize-spectrum'
"""
    return 'kanji-colorize-' + config["mode"]

def setup_dst_dir():
    """
Creates the destination directory if necessary

(Set up the doctest environment)
>>> current_directory = os.path.abspath(os.path.curdir)
>>> os.mkdir(os.path.join('test', 'doctest-tmp'))
>>> os.chdir(os.path.join('test', 'doctest-tmp'))

This creates the directory
>>> setup_dst_dir()
>>> os.listdir(os.path.curdir)
['kanji-colorize-spectrum']

But doesn't do anything or throw an error if it already exists
>>> setup_dst_dir()
>>> os.listdir(os.path.curdir)
['kanji-colorize-spectrum']

(done; reseting environment for other doctests)
>>> os.rmdir(get_dst_dir())
>>> os.chdir(os.path.pardir)
>>> os.rmdir('doctest-tmp')
>>> os.chdir(current_directory)
"""
    dst_dir = get_dst_dir()
    if not (os.path.exists(dst_dir)):
        os.mkdir(dst_dir)

# Do conversions

def convert_all():
    src_dir, dst_dir = get_src_dir(), get_dst_dir()
    setup_dst_dir()
    for src_filename in os.listdir(src_dir):
        with open(os.path.join(src_dir, src_filename), 'r') as f:
            svg = f.read()
        svg = modify_svg(svg)
        dst_file_path = os.path.join(
            dst_dir, get_dst_filename(src_filename))
        with open(dst_file_path, 'w') as f:
            f.write(svg)

if __name__ == "__main__":
    convert_all()
