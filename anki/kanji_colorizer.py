#!/usr/bin/python2

# kanji_colorizer.py is part of kanji-colorize which makes KanjiVG data
# into colored stroke order diagrams; this is the anki2 addon file.
#
# Copyright 2012 Cayenne Boyer
#
# Based on Japanese support reading generation addon by Damien Elmes
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

# Usage: copy this file and the kanjicolorizer directory to your Anki
# addons folder.  Add a "Diagrams" field to a model with "Japanese" in
# the name and a field named "Kanji".  When you finish editing the kanji
# field, if it contains precisely one character, a colored stroke order
# diagram will be added to the diagram field in the same way that the
# Japanese support plugin adds readings.

# Note: this is a work in progress.  I will be adding a way to
# mass (re)generate diagrams, and will be uploading it to the Anki
# addons site so that it can be installed automatically.

# CONFIGURATION

# Different settings can be used  
#config = "--mode contrast"

# END CONFIGURATION

from anki.hooks import addHook
from aqt import mw
from kanjicolorizer.colorizer import KanjiColorizer
import os

srcFields = ['Kanji']
dstFields = ['Diagram']

kc = KanjiColorizer()

def onFocusLost(flag, n, fidx):
    from aqt import mw
    src = None
    dst = None
    # japanese model?
    if "japanese" not in n.model()['name'].lower():
        return flag
    # have src and dst fields?
    for c, name in enumerate(mw.col.models.fieldNames(n.model())):
        for f in srcFields:
            if name == f:
                src = f
                srcIdx = c
        for f in dstFields:
            if name == f:
                dst = f
    if not src or not dst:
        return flag
    # dst field already filled?
    if n[dst]:
        return flag
    # event coming from src field?
    if fidx != srcIdx:
        return flag
    # grab source text
    srcTxt = mw.col.media.strip(n[src])
    if not srcTxt:
        return flag
    if not len(srcTxt) == 1:
        return flag
    # write to temporary file
    tmp_filename = kc.get_character_filename(srcTxt)
    with open(tmp_filename,'w') as tmp_file:
        tmp_file.write(kc.get_colored_svg(srcTxt))
        filename = mw.col.media.addFile(os.path.abspath(tmp_filename))
        n[dst] = '<img src="%s">' % filename
    return True

addHook('editFocusLost', onFocusLost)
