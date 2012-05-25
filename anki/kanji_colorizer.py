#!/usr/bin/python2

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

# Note: This is a work in progress.  When it is stable I will be
# uploading it to the anki2 addons page.

# CONFIGURATION

# Different settings can be used  
config = "--mode contrast"

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

# Function to add a colorized kanji to a card

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
    if currentFieldIndex != None: # We've left a field
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
    with open(filename,'w') as file:
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
