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
from mock import patch
from kanjicolorizer import colorizer
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

    def test_with_invalid_character_raises_correct_ex_args(self):
        with self.assertRaises(colorizer.InvalidCharacterError) as cm:
            KanjiVG(u'Л')
        # args set
        self.assertEqual(cm.exception.args[0], u'Л')
        self.assertEqual(cm.exception.args[1], None)
        # message contains the useful information
        self.assertIn(repr(u'Л'), repr(cm.exception))
        self.assertIn(repr(None), repr(cm.exception))

    def test_with_multiple_characters_raises_correct_exception(self):
        self.assertRaises(
            colorizer.InvalidCharacterError,
            KanjiVG,
            (u'漢字'))

    def test_with_nonexistent_variant_raises_correct_ex_args(self):
        with self.assertRaises(colorizer.InvalidCharacterError) as cm:
            KanjiVG(u'字', 'gobbledygook')
        # args set
        self.assertEqual(cm.exception.args[0], u'字')
        self.assertEqual(cm.exception.args[1], 'gobbledygook')
        # message contains the useful information
        self.assertIn(repr(u'字'), repr(cm.exception))
        self.assertIn(repr('gobbledygook'), repr(cm.exception))

    def test_with_mismatched_variant_raises_correct_exception(self):
        self.assertRaises(
            colorizer.InvalidCharacterError,
            KanjiVG,
            (u'漢', 'Kaisho'))

    def test_empty_variant_raises_correct_exception(self):
        self.assertRaises(
            colorizer.InvalidCharacterError,
            KanjiVG,
            (u'字', ''))

    def test_with_too_few_parameters_raises_correct_exception(self):
        self.assertRaises(
            colorizer.InvalidCharacterError,
            KanjiVG,
            ())

    def test_permission_denied_error_propogated(self):
        '''
        Errors other than file not found are unknown problems; the
        exception should not be caught or changed
        '''
        with patch('__builtin__.open') as mock_open:
            mock_open.side_effect = IOError(31, 'Permission denied')
            self.assertRaises(
                IOError,
                KanjiVG,
                ('a'))

if __name__ == "__main__":
    unittest.main()
