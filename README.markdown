## About

kanji-colorize, which will be available soon, is a script for coloring, resizing, and renaming the stroke order diagrams from the [KanjiVG](http://kanjivg.tagaini.net/) project.  I wrote it to create sets that make it possibe to easily add stroke order diagrams to an [anki](http://ankisrs.net/) kanji deck, but they can be used for anything you want some nicely colored stroke order diagrams for.

For now, there are some sets stroke order diagrams generated with it.

## Getting diagrams

If you just want some colorted diagrams, go to [Downloads](https://github.com/cayennes/kanji-colorize/downloads).  I've packaged up a spectrum set and a contrast set. The spectrum set colors the strokes in rainbow order and is nice because the you can see at a glance how the kanji is put together, but has the disadvantage that stokes next to each other are similar colors, and color is sometimes necessary to tell which number goes with which stroke. The contrast set maximizes the contrast between any set of consecutive strokes.  (This uses the golden ratio.  Math is nifty.)

## Using with Anki

To add these to a kanji deck:

1. Unzip the downloaded collection and put the contents in your deck's .media folder (which is most likely in your Dropbox/Public/Anki folder if you sync media or next to your deck at [My ]Documents/Anki if you don't.)  If your deck doesn't have a media folder create a directory with the same name as your deck except ending in .media instead of .anki.
2. Add `<img src={{{text:Kanji}}}.svg>` to your card template, where Kanji is the name of a field that contains a single kanji character.
3. Close and re-open your deck.

Now all kanji cards you have and all the ones you add will get stroke order diagrams without any more work from you.

Unless:

* If you aren't going to be adding any more kanji to your deck and you'd like to delete all the extra files, you can run "Tools >> Advanced >> Check Media Database..." and select "scan and delete".  If you do this and want to add more kanji later, you will have to repeat the above steps again.

There are examples of the diagrams and more on using stroke order diagrams with anki in [this Japanese Level Up post](http://japaneselevelup.com/2012/03/24/boosting-ankis-power-with-media-enhancements-4-colorful-stroke-order-diagrams/).

## Feedback

If there's anything you think would improve these, you can use the [issue tracker](https://github.com/cayennes/kanji-colorize/issues) or email me at cayennes@gmail.com.

If you find any errors in image files you download, check to see whether they have been fixed in the KanjiVG data by looking at [their online kanji viewer](http://kanjivg.tagaini.net/viewer.html).  If it is correct there, it means that I didn't notice that there was an update; let me know and I'll fix it.  If the error exists there, let the KanjiVG project know using their [issue tracker](https://github.com/KanjiVG/kanjivg/issues).
