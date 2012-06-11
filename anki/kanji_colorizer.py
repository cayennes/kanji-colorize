#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

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

# Usage: Add a "Diagrams" field to a model with "Japanese"
# in the name and a field named "Kanji".  When you finish editing the
# kanji field, if it contains precisely one character, a colored stroke
# order diagram will be added to the Diagram field in the same way that
# the Japanese support plugin adds readings.
#
# To add diagrams to all such fields, or regenerate them with new
# settings, use the "Kanji Colorizer: (re)generate all" option in the
# tools menu.

# CONFIGURATION

# Change the settings by editing the part between quotation marks in
# the last line of each block; leave everything else as it is.

# MODE
config = "--mode "
# spectrum: color progresses evenly through the spectrum; nice for
#           seeing the way the kanji is put together at a glance, but
#           has the disadvantage of using similar colors for consecutive
#           strokes which can make it less clear which number goes with
#           which number goes with which stroke.
# contrast: maximizes the contrast among any group of consecutive
#           strokes, using the golden ratio; also provides consistency
#           by using the same sequence for every kanji
config += "spectrum"

# SATURATION
config += " --saturation "
# --saturation: a decimal indicating saturation where 0 is
# white/gray/black and 1 is completely colorful
config += "0.95"

# VALUE
config += " --value "
# --value: a decimal indicating value where 0 is black and 1 is colored
# or white
config += "0.75"

# IMAGE SIZE
config += " --image-size "
# --image-size: image size in pixels; they're square so this will be
# both height and width
config += "327"

# END CONFIGURATION

from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *
from kanjicolorizer.colorizer import KanjiColorizer
import os

srcField = 'Kanji'
dstField = 'Diagram'

kc = KanjiColorizer(config)


def modelIsCorrectType(model):
    '''
    Returns True if model has Japanese in the name and has both srcField
    and dstField; otherwise returns False
    '''
    # Does the model name have Japanese in it?
    model_name = model['name'].lower()
    fields = mw.col.models.fieldNames(model)
    return ('japanese' in model_name and
                         srcField in fields and
                         dstField in fields)


def kanjiToAdd(note, currentFieldIndex=None):
    '''
    Determines whether and what kanji to add a diagram for, given a note
    and possibly the index of a field that was edited
    '''
    if not modelIsCorrectType(note.model()):
        return None
    if currentFieldIndex != None:  # We've left a field
        # But it isn't the relevant one
        if note.model()['flds'][currentFieldIndex]['name'] != srcField:
            return None
    # check that srcField contains a single character
    srcTxt = mw.col.media.strip(note[srcField])
    if not srcTxt:
        return None
    if not len(srcTxt) == 1:
        return None
    return srcTxt


def addKanji(note, flag=False, currentFieldIndex=None):
    '''
    Checks to see if a kanji should be added, and adds it if so.
    '''
    character = kanjiToAdd(note, currentFieldIndex)
    if character == None:
        return flag
    # write to file; anki works in the media directory by default
    filename = kc.get_character_filename(character)
    with open(filename, 'w') as file:
        file.write(kc.get_colored_svg(character))
        mw.col.media.addFile(os.path.abspath(filename))
        note[dstField] = '<img src="%s">' % filename
    note.flush()
    return True


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

# add menu item
do_regenerate_all = QAction("Kanji Colorizer: (re)generate all", mw)
mw.connect(do_regenerate_all, SIGNAL("triggered()"), regenerate_all)
mw.form.menuTools.addAction(do_regenerate_all)
