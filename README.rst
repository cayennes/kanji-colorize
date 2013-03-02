==============
KanjiColorizer
==============

About
-----

``kanji_colorize.py`` is a script for coloring, resizing, and renaming the
stroke order diagrams from the `KanjiVG <http://kanjivg.tagaini.net/>`_
project.  I wrote it to create sets that make it possibe to easily add
stroke order diagrams to an `anki <http://ankisrs.net/>`_ kanji deck, but
they can be used for anything you want some nicely colored stroke order
diagrams for.

If you'd prefer not to bother running a python script, there are some
sets of stroke order diagrams generated with it available for download.

Getting diagrams
----------------

If you just want some colorted diagrams, you can get them at 
`Downloads <https://github.com/cayennes/kanji-colorize/downloads>`_.
(Unfortunately github downloadable custom packages have been depricated
so I will not be able to update these.)

I've packaged up a spectrum set and a contrast set. The spectrum set
colors the strokes in rainbow order and is nice because the you can see
at a glance how the kanji is put together, but has the disadvantage that
stokes next to each other are similar colors, and color is sometimes
necessary to tell which number goes with which stroke. The contrast set
maximizes the contrast between any set of consecutive strokes.  (This
uses the golden ratio.  Math is nifty.)

Downloading the Software
------------------------

If you want the software to generate diagrams to your own specifications,
there is a package of the software on `KanjiColorizer's page on PyPI
<http://pypi.python.org/pypi/KanjiColorizer>`_.  You can also clone the
repository on GitHub; note that you will need to run ``git submodule
update`` if you do.  Don't download the automatic packages that GitHub
provides; they won't include the data.

Generating diagrams
-------------------

If you download and run this script, as well as the choice between
spectrum or contrast available in the downloadable sets of diagrams, you
can choose other options such as the saturation and value of the colors.

Usage:

1. Make sure you have `python 2.7 <http://www.python.org/getit/>`_
   installed.  Mac and and most Linux distros come with this included so
   only Windows users need this step.
2. Run ``python kanji_colorize.py`` from its directory.
   ``python kanji_colorize.py --help`` will list available options so you
   can customize the results.  If you want to save a set of options, you 
   can create a shell script.
3. You will find your diagrams in the ``colorized-kanji`` directory or
   the output directory you chose.

If you want to try out your settings without spending the time
processing the whole kanji collection, use the ``--characters`` option
(for example, ``python kanji_colorizer.py --characters 漢字``) to only
color the specified characters.

If you want to be able to run the script as ``kanji_colorize.py`` from
anywhere, run ``python setup.py install``.

Using with Anki
---------------

Anki 2.x
`````````````
There is an addon for Anki2 that generates colored diagrams for all of
your kanji cards.  You can download it from the Anki2 Addon site.

**known issue**: Unfortunately it is currently broken unless you have a full install of
python 2.x on your path.  I intend to fix this soon, for some value of
soon.

Anki 1.x
````````

While I originally had instructions for a way to use a set of generated
diagrams with Anki1, it never worked very well.


Using the Package in Python Code
--------------------------------

The code is designed to be imported and used in python programs, but the
API *will* be changing.

Documentation can be found in the docstrings.  Though I have to admit
that I used doctest, which mean writing not-great documentation and
not-great tests for almost no work.

Feedback
--------

If there's anything you think would improve these, you can use the
`issue tracker <https://github.com/cayennes/kanji-colorize/issues>`_ or
email me at cayennes@gmail.com.

If you find any errors in image files you download, check to see whether
they have been fixed in the KanjiVG data by looking at `their online
kanji viewer <http://kanjivg.tagaini.net/viewer.html>`_.  If it is 
correct there, it means that I didn't notice that there was an update;
let me know and I'll fix it.  If the error exists there, let the KanjiVG
project know using `their issue tracker
<https://github.com/KanjiVG/kanjivg/issues>`_.  If you find errors in
image files you generated from KanjiVG data and you have the most recent
data, it should be reported to KanjiVG.

Development
-----------

Have you created an improvement to KanjiColorizer that you think
other people would also like to have?  If so, please submit a patch or a
pull request!  I'm not always very prompt but I do get to them
eventually.

Please make sure existing tests pass.  Or even better, add new tests for
anything you add.  Either doctest or unittest is fine, though ideally
the doctests would contain executable examples that fully illustrate the
function and the unittest tests would contain further worthwhile checks.

To run the existing tests:

    $ python -m kanjicolorizer.colorizer
    $ python -m unittest discover

Licence
-------

The code is available under the Affero GPL version 3 or later and the SVG
images are available under Creative Commons Attribution-Share Alike 3.0.
See file headers and files in ``licenses/`` for more information.
