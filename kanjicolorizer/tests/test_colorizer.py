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
        self.assertEqual(k.variant, '')

    def test_valid_ascii_character_contains_named_stroke_group(self):
        '''
        This is a proxy for having read the correct file
        '''
        k = KanjiVG('a')
        self.assertIn('kvg:StrokePaths_00061', k.svg)

    def test_valid_nonascii_character_inits(self):
        k = KanjiVG(u'あ')
        self.assertEqual(k.character, u'あ')
        self.assertEqual(k.variant, '')

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

    def test_explicit_none_variant_inits_to_empty_string(self):
        k = KanjiVG(u'字', None)
        self.assertEquals(k.variant, '')

    def test_with_invalid_character_raises_correct_ex_args(self):
        with self.assertRaises(colorizer.InvalidCharacterError) as cm:
            KanjiVG(u'Л')
        # args set
        self.assertEqual(cm.exception.args[0], u'Л')
        self.assertEqual(cm.exception.args[1], '')
        # message contains the useful information
        self.assertIn(repr(u'Л'), repr(cm.exception))

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


class KanjiVGCreateFromFilenameTest(unittest.TestCase):

    def test_without_variant_with_hex_inits(self):
        k = KanjiVG._create_from_filename('06f22.svg')
        self.assertEquals(k.character, u'漢')
        self.assertEquals(k.variant, '')

    def test_with_variant_inits(self):
        k = KanjiVG._create_from_filename('05b57-Kaisho.svg')
        self.assertEquals(k.character, u'字')
        self.assertEquals(k.variant, 'Kaisho')

    def test_five_digit_inits(self):
        k = KanjiVG._create_from_filename('26951.svg')
        self.assertEquals(k.character, u'𦥑')

    def test_correct_format_nonexistent_file_raises_exception(self):
        '''
        As a private method, the precise exception is unimportant
        '''
        self.assertRaises(
            Exception,
            KanjiVG._create_from_filename,
            '10000.svg')

    def test_incorrect_format_raises_exception(self):
        '''
        As a private method, the precise exception is unimportant
        '''
        self.assertRaises(
            Exception,
            KanjiVG._create_from_filename,
            '5b57')

if __name__ == "__main__":
    unittest.main()
