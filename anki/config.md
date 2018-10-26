* `mode` (default: `spectrum`). options:
    * `spectrum`: color progresses evenly through the spectrum; nice for seeing the way the kanji is put together at a glance, but has the disadvantage of using similar colors for consecutive strokes which can make it less clear which number goes with which number goes with which stroke.
    * `contrast`: maximizes the contrast among any group of consecutive strokes, using the golden ratio; also provides consistency by using the same sequence for every kanji
* `saturation`: a decimal indicating saturation where 0 is white/gray/black and 1 is completely colorful. (default: `0.95`)
* `value`: a decimal indicating value where 0 is black and 1 is colored or white (default: `0.75`)
* `image-size`: image size in pixels; they're square so this will be both height and width (default: `327`)
* `group-mode`: Somewhat buggy option to color groups of kanji instead of strokes. (default: `false`)

You will need to restart anki for changes to take effect.