#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# kanji_colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams; this is the anki2 addon file.
#
# Copyright 2012 Cayenne Boyer
#
# The code to do this automatically when the Kanji field is exited was
# originally based on the Japanese support reading generation addon by
# Damien Elmes
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

# Installation: copy this file and the kanjicolorizer directory to your
# Anki addons folder.

# Usage: Add a "Diagram" field to a model with "Japanese"
# in the name and a field named "Kanji".  When you finish editing the
# kanji field, if it contains precisely one character, a colored stroke
# order diagram will be added to the Diagram field in the same way that
# the Japanese support plugin adds readings.
#
# To add diagrams to all such fields, or regenerate them with new
# settings, use the "Kanji Colorizer: (re)generate all" option in the
# tools menu.


from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *
from .kanjicolorizer.colorizer import (KanjiVG, KanjiColorizer,
                                      InvalidCharacterError)

# Configuration

addon_config = mw.addonManager.getConfig(__name__)

config = "--mode "
config += addon_config["mode"]
if addon_config["group-mode"]:
  config += " --group-mode "
config += " --saturation "
config += str(addon_config["saturation"])
config += " --value "
config += str(addon_config["value"])
config += " --image-size "
config += str(addon_config["image-size"])

modelNameSubstring = 'japanese'
srcField           = 'Kanji'
dstField           = 'Diagram'
overwrite          = True

# avoid errors due to invalid config
if 'model' in addon_config and type(addon_config['model']) is str:
    modelNameSubstring = addon_config['model'].lower()
if 'src-field' in addon_config and type(addon_config['src-field']) is str:
    srcField = addon_config['src-field']
if 'dst-field' in addon_config and type(addon_config['dst-field']) is str:
    dstField = addon_config['dst-field']
if 'overwrite-dest' in addon_config and type(addon_config['overwrite-dest']) is bool:
    overwrite = addon_config['overwrite-dest']

kc = KanjiColorizer(config)


def modelIsCorrectType(model):
    '''
    Returns True if model has Japanese in the name and has both srcField
    and dstField; otherwise returns False
    '''
    # Does the model name have Japanese in it?
    model_name = model['name'].lower()
    fields = mw.col.models.fieldNames(model)
    return (modelNameSubstring in model_name and
                         srcField in fields and
                         dstField in fields)

def is_kanji(c):
    '''
    Boolean indicating if the character is in the kanji unicode range
    '''
    return ord(c) >= 19968 and ord(c) <= 40879


def characters_to_colorize(s):
    '''
    Given a string, returns a list of characters to colorize

    If the string mixes kanji and other characters, it will return
    only the kanji. Otherwise it will return all characters.
    '''
    conf = mw.addonManager.getConfig(__name__)['diagrammed-characters']
    if conf == 'all':
        return list(s)
    elif conf == 'kanji':
        return [c for c in s if is_kanji(c)]
    else:
        just_kanji = [c for c in s if is_kanji(c)]
        if len(just_kanji) >= 1:
            return just_kanji
        return list(s)


def addKanji(note, flag=False, currentFieldIndex=None):
    '''
    Checks to see if a kanji should be added, and adds it if so.
    '''
    if not modelIsCorrectType(note.model()):
        return flag

    if currentFieldIndex != None: # We've left a field
        # But it isn't the relevant one
        if note.model()['flds'][currentFieldIndex]['name'] != srcField:
            return flag

    srcTxt = mw.col.media.strip(note[srcField])

    oldDst = note[dstField]
    dst=''

    for character in characters_to_colorize(str(srcTxt)):
        # write to file; anki works in the media directory by default
        try:
            filename = KanjiVG(character).ascii_filename
        except InvalidCharacterError:
            # silently ignore non-Japanese characters
            continue
        char_svg = kc.get_colored_svg(character).encode('utf_8')
        anki_fname = mw.col.media.writeData(filename, char_svg)
        dst += '<img src="{!s}">'.format(anki_fname)

    if oldDst != '' and not overwrite:
        return flag

    if dst != oldDst and dst != '':
        note[dstField] = dst
        # if we're editing an existing card, flush the changes
        if note.id != 0:
            note.flush()
        return True

    return flag


# Add a colorized kanji to a Diagram whenever leaving a Kanji field

def onFocusLost(flag, note, currentFieldIndex):
    return addKanji(note, flag, currentFieldIndex)

addHook('editFocusLost', onFocusLost)


# menu item to regenerate all

def regenerate_all():
    # Find the models that have the right name and fields; faster than
    # checking every note
    if not askUser("Do you want to regenerate all kanji diagrams? "
                   'This may take some time and will overwrite the '
                   'destination Diagram fields.'):
        return
    models = [m for m in mw.col.models.all() if modelIsCorrectType(m)]
    # Find the notes in those models and give them kanji
    for model in models:
        for nid in mw.col.models.nids(model):
            addKanji(mw.col.getNote(nid))
    showInfo("Done regenerating colorized kanji diagrams!")

def generate_for_new():
    if not askUser("This option will generate diagrams for notes with "
                   "an empty {} field only. "
                   "Proceed?".format(dstField)):
        return
    model_ids = [mid for mid in mw.col.models.ids() if modelIsCorrectType(mw.col.models.get(mid))]
    # Generate search string in the format 
    #    (mid:123 or mid:456) Kanji:_* Diagram:
    search_str = '({}) {}:_* {}:'.format(
        ' or '.join(('mid:'+str(mid) for mid in model_ids)), srcField, dstField)
    # Find the notes
    for note_id in mw.col.findNotes(search_str):
        addKanji(mw.col.getNote(note_id))
    showInfo("Done generating colorized kanji diagrams!")

# add menu items
submenu = mw.form.menuTools.addMenu("Kanji Colorizer")

do_generate_new = QAction("generate all new", mw)
do_generate_new.triggered.connect(generate_for_new)
submenu.addAction(do_generate_new)

do_regenerate_all = QAction("(re)generate all", mw)
do_regenerate_all.triggered.connect(regenerate_all)
submenu.addAction(do_regenerate_all)
