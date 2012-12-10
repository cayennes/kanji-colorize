#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# test_colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams
#
# Copyright 2012 Cayenne Boyer, Roland Sieker
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
from mock import MagicMock, patch
import os
from kanjicolorizer import colorizer
from kanjicolorizer.colorizer import KanjiVG, KanjiColorizer
import xml.etree.ElementTree as ET

svg_ns = "http://www.w3.org/2000/svg"
kvg_ns = "http://kanjivg.tagaini.net"
xlink_ns = "http://www.w3.org/1999/xlink"

ET.register_namespace('svg', svg_ns)
ET.register_namespace('kvg', kvg_ns)
ET.register_namespace('xlink', xlink_ns)


TOTAL_NUMBER_CHARACTERS = 11251


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

    def test_valid_variant_contains_group_with_stroke_paths_id(self):
        '''
        This is a proxy for having read the correct file
        '''
        k = KanjiVG(u'字', 'Kaisho')
        # self.assertIn('kvg:StrokePaths_05b57-Kaisho', k.svg)
        # KanjiVG.svg is now an ElementTree.Element.  So we can be
        # more precise here. Make sure that the first group's
        # (<svg:g>...</svg:g>) id is that string:
        self.assertEqual(
            k.svg.find('{{{ns}}}g'.format(ns=svg_ns)).get('id'),
            'kvg:StrokePaths_05b57-Kaisho')

    def test_explicit_none_variant_inits_to_empty_string(self):
        k = KanjiVG(u'字', None)
        self.assertEquals(k.variant, '')

    def test_with_invalid_character_raises_ioerror(self):
        # KanjiVg no doesn't modify the exceptions. Non-existant
        # characters now give an IOError.
        with self.assertRaises(IOError) as ioe:
            KanjiVG(u'Л')
        self.assertIn('No such file or directory', str(ioe))
        self.assertIn('data/kanjivg/kanji/0041b.svg', str(ioe))

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
        # New style doesn't change the exception any more. We get an
        # IOError now.
        self.assertRaises(IOError, KanjiVG, (u'漢', 'Kaisho'))

    def test_empty_variant_raises_correct_exception(self):
        # New style doesn't change the exception any more. We get an
        # IOError now.
        self.assertRaises(
            colorizer.InvalidCharacterError, KanjiVG, (u'字', ''))

    def test_with_too_few_parameters_raises_correct_exception(self):
        self.assertRaises(colorizer.InvalidCharacterError, KanjiVG, ())

    def test_permission_denied_error_propogated(self):
        '''
        Errors other than file not found are unknown problems; the
        exception should not be caught or changed
        '''
        with patch('__builtin__.open') as mock_open:
            mock_open.side_effect = IOError(31, 'Permission denied')
            self.assertRaises(IOError, KanjiVG, ('a'))


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
            Exception, KanjiVG._create_from_filename, '10000.svg')

    def test_incorrect_format_raises_exception(self):
        '''
        As a private method, the precise exception is unimportant
        '''
        self.assertRaises(Exception, KanjiVG._create_from_filename, '5b57')


class KanjiVGAsciiFilenameTest(unittest.TestCase):

    def test_without_variant_has_correct_filename(self):
        k = KanjiVG(u'あ')
        self.assertEqual(k.ascii_filename, '03042.svg')

    def test_with_variant_has_correct_filename(self):
        k = KanjiVG(u'字', 'Kaisho')
        self.assertEqual(k.ascii_filename, '05b57-Kaisho.svg')

    def test_five_digit_unicode_character_has_correct_filename(self):
        k = KanjiVG(u'𦥑')
        self.assertEqual(k.ascii_filename, '26951.svg')


class KanjiVGCharacterFilenameTest(unittest.TestCase):

    def test_without_variant_has_correct_filename(self):
        k = KanjiVG(u'あ')
        self.assertEqual(k.character_filename, u'あ.svg')

    def test_with_variant_has_correct_filename(self):
        k = KanjiVG(u'字', 'Kaisho')
        self.assertEqual(k.character_filename, u'字-Kaisho.svg')


# class KanjiVGGetAllTest(unittest.TestCase):
# The code has changed. Now we only get a list, and load the ETs
# later.
class KanjiVGGetListTest(unittest.TestCase):

    def test_has_correct_number(self):
        all_kanji = KanjiVG.get_list()
        self.assertEqual(len(all_kanji), TOTAL_NUMBER_CHARACTERS)

    def test_first_is_string_pair(self):
        all_kanji = KanjiVG.get_list()
        first_pair = all_kanji[0]
        self.assertIsInstance(first_pair, tuple)
        self.assertEqual(len(first_pair), 2)
        self.assertIsInstance(first_pair[0], str)
        self.assertIsInstance(first_pair[1], str)


class KanjiColorizerCharactersOptionTest(unittest.TestCase):

    def setUp(self):
        # For the new version using ElementTree, don't patch open,
        # patch ET.parse instead. It now returns an empty ElementTree.
        patch_parse = patch('xml.etree.ElementTree.parse')
        self.mock_parse = patch_parse.start()
        self.addCleanup(patch_parse.stop)
#        self.mock_parse.return_value = MagicMock(spec=ET.ElementTree)
#        self.mock_parse.return_value.read = MagicMock(
#            return_value=ET.ElementTree(
#                ET.Element('svg')))
        self.mock_parse.return_value = ET.ElementTree(ET.Element('svg'))

        ## replace the open function with a mock; reading any file will
        ## return ''
        patch_open = patch('__builtin__.open')
        self.mock_open = patch_open.start()
        self.addCleanup(patch_open.stop)
        self.mock_open.return_value = MagicMock(spec=file)
        self.mock_open.return_value.read = MagicMock(return_value='')

    def assertOpenedFileForWriting(self, file_name):
        '''
        Checks self.open_mock to find out whether it was called with 'w'
        in the second argument and file_name as the file part of the
        first. (This ignores the path part of the open.)  Asserts that
        it was.
        '''
        calls = self.mock_open.call_args_list
        files_opened_for_writing = [
            os.path.split(c[0][0])[1]
            for c in calls if ('w' in c[0][1])]
        self.assertIn(file_name, files_opened_for_writing)

    def assertDidntOpenFileForWriting(self, file_name):
        '''
        Checks self.open_mock to find out whether it was called with 'w'
        in the second argument and file_name as the file part of the
        first. (This ignores the path part of the open.)  Asserts that
        it wasn't.
        '''
        calls = self.mock_open.call_args_list
        files_opened_for_writing = [
            os.path.split(c[0][0])[1]
            for c in calls if ('w' in c[0][1])]
        self.assertNotIn(file_name, files_opened_for_writing)

    def assertNumberFilesOpenedForWriting(self, number):
        '''
        Checks self.open_mock to find out how many times it was called
        with 'w' in the second argument.  Asserts that it was number.
        '''
        calls = self.mock_open.call_args_list
        self.assertEqual(len([c for c in calls if 'w' in c[0][1]]), number)

    def test_ascii_sets_setting(self):
        kc = KanjiColorizer('--characters a')
        self.assertEqual(kc.settings.characters, u'a')

    def test_nonascii_sets_setting(self):
        kc = KanjiColorizer(u'--characters あ')
        self.assertEqual(kc.settings.characters, u'あ')

    def test_multiple_characters_sets_setting(self):
        kc = KanjiColorizer(u'--characters 漢字')
        self.assertEqual(kc.settings.characters, u'漢字')

    def test_default_writes_correct_number(self):
        kc = KanjiColorizer()
        kc.write_all()
        self.assertNumberFilesOpenedForWriting(TOTAL_NUMBER_CHARACTERS)

    def test_default_writes_some_characters(self):
        kc = KanjiColorizer()
        kc.write_all()
        # To deal with file name clashes "A.svg"/'a.svg', the
        # lower-case romaji now are 'a_.svg' ...
        self.assertOpenedFileForWriting(u'a_.svg')
        self.assertOpenedFileForWriting(u'あ.svg')

    def test_writes_a_character(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'あ'
        kc.write_all()
        self.assertOpenedFileForWriting(u'あ.svg')
        self.assertNumberFilesOpenedForWriting(1)

    def test_writes_only_one_character(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'あ'
        kc.write_all()
        self.assertNumberFilesOpenedForWriting(1)

    def test_writes_exactly_two_characters(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'漢字'
        kc.write_all()
        self.assertNumberFilesOpenedForWriting(2)

    def test_writes_correct_two_characters(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'漢字'
        kc.write_all()
        self.assertOpenedFileForWriting(u'漢.svg')
        self.assertOpenedFileForWriting(u'字.svg')

    @unittest.expectedFailure
    # All characters seem valid when open is mocked and a character's
    # validity is checked by the existence of a file.
    def test_invalid_character_doesnt_write_file(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'Л'
        kc.write_all()
        self.assertDidntOpenFileForWriting(u'Л.svg')

    def test_invalid_after_valid_writes_valid(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'あЛ'
        kc.write_all()
        self.assertOpenedFileForWriting(u'あ.svg')

    def test_invalid_before_valid_writes_valid(self):
        kc = KanjiColorizer()
        kc.settings.characters = u'Лあ'
        kc.write_all()
        self.assertOpenedFileForWriting(u'あ.svg')


if __name__ == "__main__":
    unittest.main()
