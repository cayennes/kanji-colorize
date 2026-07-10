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
config += " --grid "
config += addon_config["grid"]

default_config = {
    "modelNameSubstring": "japanese",
    "srcField": "Kanji",
    "dstFields": ["Diagram"],
    "overwrite": True
}

configs = []

# avoid errors due to invalid config
if 'model' in addon_config and type(addon_config['model']) is list: # multiple models specified
    for model in addon_config['model']:
        new_model_config = default_config.copy()
        if 'name' in model and type(model['name']) is str:
            new_model_config["modelNameSubstring"] = model["name"].lower()
        else:
            continue
        if 'src-field' in model and type(model['src-field']) is str:
            new_model_config["srcField"] = model['src-field']
        if 'dst-field' in model and type(model['dst-field']) is str:
            new_model_config["dstFields"] = [model['dst-field']]
        if 'dst-field' in model and type(model['dst-field']) is list:
            new_model_config["dstFields"] = model['dst-field']
        if 'overwrite-dest' in model and type(model['overwrite-dest']) is bool:
            model["overwrite"] = model['overwrite-dest']
        configs.append(new_model_config)
else: # only one model
    configs.append(default_config.copy())
    if 'model' in addon_config and type(addon_config['model']) is str:
        configs[0]["modelNameSubstring"] = addon_config['model'].lower()
    if 'src-field' in addon_config and type(addon_config['src-field']) is str:
        configs[0]["srcField"] = addon_config['src-field']
    if 'dst-field' in addon_config and type(addon_config['dst-field']) is str:
        configs[0]["dstFields"] = [addon_config['dst-field']]
    if 'dst-field' in addon_config and type(addon_config['dst-field']) is list:
        configs[0]["dstFields"] = addon_config['dst-field']
    if 'overwrite-dest' in addon_config and type(addon_config['overwrite-dest']) is bool:
        configs[0]["overwrite"] = addon_config['overwrite-dest']

kc = KanjiColorizer(config)


# def modelIsCorrectType(model):
#     '''
#     Returns True if model has Japanese/a model name
#     specified in the config in the name and has both srcField
#     and dstField; otherwise returns False
#     '''
#     # Does the model name have Japanese in it?
#     model_name = model['name'].lower()
#     fields = mw.col.models.fieldNames(model)
#     return any(
#         model_conf["modelNameSubstring"] in model_name and
#         model_conf["srcField"] in fields and
#         any(field for field in model_conf["dstFields"] if field in fields)
#         for model_conf in configs
#     )

def getModelType(model):
    '''
    Returns the index in configs if model has a valid model name and has both srcField
    and dstField; otherwise returns None
    '''
    model_name = model['name'].lower()
    fields = mw.col.models.fieldNames(model)
    modelidx = None
    for i, model_conf in enumerate(configs):
        if (model_conf["modelNameSubstring"] in model_name and
            model_conf["srcField"] in fields and
                any(field for field in model_conf["dstFields"] if field in fields)):
            modelidx = i
            break
    return modelidx


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
    modelidx = getModelType(note.model())
    if modelidx is None:
        return flag

    if currentFieldIndex != None:  # We've left a field
        # But it isn't the relevant one
        if note.model()['flds'][currentFieldIndex]['name'] != configs[modelidx]["srcField"]:
            return flag

    srcTxt = mw.col.media.strip(note[configs[modelidx]["srcField"]])
    existingDstFields = [field for field in configs[modelidx]["dstFields"] if field in mw.col.models.fieldNames(note.model())]

    note_edited = False
    characters = characters_to_colorize(str(srcTxt))

    last_destination_field_contents = note[existingDstFields[-1]]

    for dstField, character in zip(existingDstFields, characters):
        oldDst = note[dstField]
        dst=''

        # write to file; anki works in the media directory by default
        try:
            filename = KanjiVG(character).ascii_filename
        except InvalidCharacterError:
            # silently ignore non-Japanese characters
            continue
        char_svg = kc.get_colored_svg(character).encode('utf_8')
        anki_fname = mw.col.media.writeData(filename, char_svg)
        dst += '<img src="{!s}">'.format(anki_fname)

        if oldDst != '' and not configs[modelidx]["overwrite"]:
            continue

        if dst != oldDst and dst != '':
            note[dstField] = dst
            # if we're editing an existing card, flush the changes
            if note.id != 0:
                note.flush()
            note_edited = True

    # Put leftover characters in the last destination. However if it isn't empty and overwrite is false,
    # don't write any characters to it.
    if len(characters) > len(existingDstFields) and (last_destination_field_contents == '' or configs[modelidx]["overwrite"]):
        dstField = existingDstFields[-1]
        oldDst = note[dstField]
        dst = note[dstField]

        for character in characters[len(existingDstFields):]:
            # write to file; anki works in the media directory by default
            try:
                filename = KanjiVG(character).ascii_filename
            except InvalidCharacterError:
                # silently ignore non-Japanese characters
                continue
            char_svg = kc.get_colored_svg(character).encode('utf_8')
            anki_fname = mw.col.media.writeData(filename, char_svg)
            dst += '<img src="{!s}">'.format(anki_fname)

        if dst != oldDst and dst != '':
            note[dstField] = dst
            # if we're editing an existing card, flush the changes
            if note.id != 0:
                note.flush()
            note_edited = True

    return note_edited or flag


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
                   'destination Diagram field(s).'):
        return
    models = [m for m in mw.col.models.all() if getModelType(m) is not None]
    # Find the notes in those models and give them kanji
    for model in models:
        for nid in mw.col.models.nids(model):
            addKanji(mw.col.getNote(nid))
    showInfo("Done regenerating colorized kanji diagrams!")

def generate_for_new():
    if not askUser("This option will generate diagrams for notes with "
                   "empty destination field(s) only."
                   "Proceed?"):
        return

    models = []
    for mid in mw.col.models.ids():
        modelidx = getModelType(mw.col.models.get(mid))
        if modelidx is not None:
            models.append((mid, modelidx))

    if not models:
        showInfo("Can not find any relevant models. Make sure model, src-field, and dst-field are set correctly in your config.")
        return
    # Generate search string in the format
    #    ("mid:123" "Kanji:_*" "Diagram:") or ("mid:456" "Kanji:_*" "Diagram:")
    parts = []
    for model_id, modelidx in models:
        model_conf = configs[modelidx]

        dst = " ".join(f'"{field}:"' for field in model_conf["dstFields"])

        parts.append(f'("mid:{model_id}" "{model_conf['srcField']}:_*" {dst})')
    search_str = " or ".join(parts)

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
