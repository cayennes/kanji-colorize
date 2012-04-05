## About

`kanji_colorize.py` is a script for coloring, resizing, and renaming the stroke order diagrams from the [KanjiVG](http://kanjivg.tagaini.net/) project.  I wrote it to create sets that make it possibe to easily add stroke order diagrams to an [anki](http://ankisrs.net/) kanji deck, but they can be used for anything you want some nicely colored stroke order diagrams for.

If you'd prefer not to bother running a python script, there are some sets of stroke order diagrams generated with it available for download.

## Getting diagrams

If you just want some colorted diagrams, you can get them at [Downloads](https://github.com/cayennes/kanji-colorize/downloads).  

I've packaged up a spectrum set and a contrast set. The spectrum set colors the strokes in rainbow order and is nice because the you can see at a glance how the kanji is put together, but has the disadvantage that stokes next to each other are similar colors, and color is sometimes necessary to tell which number goes with which stroke. The contrast set maximizes the contrast between any set of consecutive strokes.  (This uses the golden ratio.  Math is nifty.)

## Generating diagrams

If you download and run this script, as well as the choice between spectrum or contrast available in the downloadable sets of diagrams, you can choose other options such as the saturation and value of the colors.

Usage:

1. Make sure you have [python 2.x](http://www.python.org/getit/) installed.  Mac and and most Linux distros come with this included so only Windows users need this step.
2. [Download KanjiVG svg diagrams](http://kanjivg.tagaini.net/download.html); choose "Download separate".  It also works if you choose to download the [whole project](https://github.com/KanjiVG/kanjivg) for any reason.
3. Edit the CONFIGURATION VARIABLES section of `kanji_colorize.py` to your liking; all options are explained in the accompanying comments.
4. Run `python kanji_colorize.py`in a location that contains the script and the kanji or kanjivg directory you downloaded, or containing the script with kanjivg in the parent directory.
5. You will find your newly colored diagrams in kanji-colorize-spectrum or kanji-colorize-contrast depending on the setting you used.

If you want to try out your settings without spending the time
processing the whole kanji collection, run the script from the test
directory.  It contains a kanji directory with just four files in it.

## Using with Anki

To add these to a kanji deck:

1. Unzip the downloaded collection if you downloaded it
2. Put the contents in your deck's .media folder (which is most likely in your Dropbox/Public/Anki folder if you sync media or next to your deck at [My ]Documents/Anki if you don't.)  If your deck doesn't have a media folder create a directory with the same name as your deck except ending in .media instead of .anki.
3. Add `<img src={{text:Kanji}}.svg>` to your card template, where Kanji is the name of a field that contains a single kanji character.  Note that `{{text:Kanji}}` (or `{{Kanji}}`) can't be used in the same template as `{{{Kanji}}}`; see [Anki's CardLayout help page](http://ankisrs.net/docs/CardLayout) for more information.
4. Close and re-open your deck.

Now all kanji cards you have and all the ones you add will get stroke order diagrams without any more work from you.

Unless:

* If you aren't going to be adding any more kanji to your deck and you'd like to delete all the extra files, you can run "Tools >> Advanced >> Check Media Database..." and select "scan and delete".  If you do this and want to add more kanji later, you will have to repeat the above steps again.

There are examples of the diagrams and more on using stroke order diagrams with anki in [this Japanese Level Up post](http://japaneselevelup.com/2012/03/24/boosting-ankis-power-with-media-enhancements-4-colorful-stroke-order-diagrams/).

## Known Issues

Distributing zips of files with characters for filenames doesn't work as well as a universal simple method of adding stroke order diagrams to anki decks as I had hoped, for two reasons:

1. Zip doesn't support unicode very well; it doesn't have a way of indicating what character set is used.
2. Anki support for adding media via the template is somewhat weak, and it's unclear how to get it to reliably sync to other devices, though I and other users have gotten it to work.

Rather than trying to refine this method, I believe a better solution would be a shared plugin/addon that adds diagrams to cards instead.  Since anki 2.0 is around the corner I will be writing an addon for that instead of an anki 1.x plugin that would quickly become irrelevant.  Hopefully the current clunky solution is good enough for the short term.

## Feedback

If there's anything you think would improve these, you can use the [issue tracker](https://github.com/cayennes/kanji-colorize/issues) or email me at cayennes@gmail.com.

If you find any errors in image files you download, check to see whether they have been fixed in the KanjiVG data by looking at [their online kanji viewer](http://kanjivg.tagaini.net/viewer.html).  If it is correct there, it means that I didn't notice that there was an update; let me know and I'll fix it.  If the error exists there, let the KanjiVG project know using their [issue tracker](https://github.com/KanjiVG/kanjivg/issues).  If you find errors in image files you generated from KanjiVG data and you have the most recent data, it should be reported to KanjiVG.
