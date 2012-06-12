#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# test_colorizer.py is part of kanji-colorize which makes KanjiVG data
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

import unittest
from kanjicolorizer.colorizer import KanjiVG


class KanjiVGInitTest(unittest.TestCase):

    def test_valid_ascii_character_inits(self):
        k = KanjiVG('a')
        self.assertEqual(k.character, 'a')
        self.assertEqual(k.variant, None)

    def test_valid_ascii_character_contains_named_stroke_group(self):
        '''
        This is a proxy for having read the correct file
        '''
        k = KanjiVG('a')
        self.assertIn('kvg:StrokePaths_00061', k.svg)

    def test_valid_nonascii_character_inits(self):
        k = KanjiVG(u'あ')
        self.assertEqual(k.character, u'あ')
        self.assertEqual(k.variant, None)

    def test_valid_nonascii_character_contains_named_stroke_group(self):
        '''
        This is a proxy for having read the correct file
        '''
        k = KanjiVG(u'あ')
        self.assertIn('kvg:StrokePaths_03042', k.svg)

    def test_valid_variant_inits(self):
        k = KanjiVG(u'字', 'Kaisho')
        self.assertEqual(k.character, u'字')
        self.assertEqual(k.variant, 'Kaisho')

    def test_valid_variant_contains_named_stroke_group(self):
        '''
        This is a proxy for having read the correct file
        '''
        k = KanjiVG(u'字', 'Kaisho')
        self.assertIn('kvg:StrokePaths_05b57-Kaisho', k.svg)

if __name__ == "__main__":
    unittest.main()
