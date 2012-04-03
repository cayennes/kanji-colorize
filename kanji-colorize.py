#! /usr/bin/python

# kanji-colorize.py processes KanjiVG data into colored stroke order diagrams
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

# mode: 
# * spectrum: color progresses evenly through the spectrum.  This is nice for
#             seeing the way the kanji is put together at a glance, but has
#             the disadvantage of using similar colors for consecutive strokes
#             which can make it less clear which number goes with which stroke
# * contrast: maximizes contrast among any group of consecutive strokes, by 
#             using the golden ratio
mode = "spectrum"

# saturation and value, as numbers between 0 and 1
saturation = 0.95
value = 0.75

# image size in pixels
image_size = 327

# rename files to use characters rather than codes; set to True or False
character_file_names = True

# END OF CONFIGURATION VARIABLES

# make sure config variables are in the right format
mode = mode.lower()
saturation = float(saturation)
value = float(value)
image_size = int(image_size)

# begin script

import os
import colorsys
import re

def stroke_count(svg):
    'Return the number of strokes in the svg, based on occurences of "<path "'
    return len(re.findall('<path ', svg))

def hsv_to_rgbhexcode(h, s, v):
    'Convert an h, s, v color into rgb form #000000'
    color = colorsys.hsv_to_rgb(h, s, v)
    return '#%02x%02x%02x' % tuple([i * 255 for i in color])

def color_generator(n):
    """Create an iterator that loops through n colors twice (so that they can be used
for both strokes and stroke numbers) using the mode config variable to 
determine what colors to produce."""
    if (mode == "contrast"):
        angle = 0.618033988749895 # conjugate of the golden ratio
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(i * angle, saturation, value)
    else: # spectrum is default
        for i in 2 * range(n):
            yield hsv_to_rgbhexcode(float(i)/n, saturation, value)

def color_svg(svg):
    "Color the svg according to the mode config variable"
    color_iterator = color_generator(stroke_count(svg))
    def color_match(match_object):
        return match_object.re.pattern + 'style="stroke:' + next(color_iterator) + '" '
    svg = re.sub('<path ', color_match, svg)
    return re.sub('<text ', color_match, svg)

def resize_svg(svg):
    "Resize the svg according to the image_size config variable"
    ratio = `float(image_size) / 109`
    svg = svg.replace('109" height="109" viewBox="0 0 109 109', '{0}" height = "{0}" viewBox="0 0 {0} {0}'.format(`image_size`))
    svg = re.sub('(<g id="kvg:Stroke.*?)(>)', r'\1 transform="scale(' + ratio + ',' + ratio + r')"\2', svg)
    return svg

def comment_copyright(svg):
    "Add a comment about what this script has done to the copyright notice"
    note = """This file has been modified from the original version by the kanji-colorize 
script (available at http://github.com/cayennes/kanji-colorize) with these 
settings: 
    mode: """ + mode + """
    saturation: """ + `saturation` + """
    value: """ + `value` + """
    image_size: """ + `image_size` + """
It remains under a Creative Commons-Attribution-Share Alike 3.0 License.

The original SVG has the following copyright:

"""
    place_before = "Copyright (C)"
    return svg.replace(place_before, note + place_before)

def convert_file_name(filename):
    "Convert unicode code in filename to actual character"
    def hex_to_unicode_char(match_object):
        'local function used for a call to re.sub'
        return unichr(int(match_object.group(0), 16))
    return re.sub('^[0-9a-fA-F]*', hex_to_unicode_char, filename)

# Find and set up directories

if (os.path.exists('kanji')):
    src_dir = 'kanji'
elif (os.path.exists('kanjivg/kanji')):
    src_dir = 'kanjivg/kanji'
elif (os.path.exists('../kanjivg/kanji')):
    src_dir = '../kanjivg/kanji'

dst_dir = 'kanji-colorize-' + mode
if not (os.path.exists(dst_dir)):
    os.mkdir(dst_dir)
   
# Do conversions

for src_filename in os.listdir(src_dir):
    # read original svg
    with open(src_dir + '/' + src_filename, 'r') as f:
        svg = f.read()
    # modify
    svg = color_svg(svg)
    svg = resize_svg(svg)
    svg = comment_copyright(svg)
    # write to new svg
    if (character_file_names):
        dst_filename = convert_file_name(src_filename)
    else:
        dst_filename = src_filename
    with open(dst_dir + '/' + dst_filename, 'w') as f:
        f.write(svg)
