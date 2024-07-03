* `mode` (default: `spectrum`). options:
    * `spectrum`: color progresses evenly through the spectrum; nice for seeing the way the kanji is put together at a glance, but has the disadvantage of using similar colors for consecutive strokes which can make it less clear which number goes with which number goes with which stroke.
    * `contrast`: maximizes the contrast among any group of consecutive strokes, using the golden ratio; also provides consistency by using the same sequence for every kanji
* `saturation`: a decimal indicating saturation where 0 is white/gray/black and 1 is completely colorful. (default: `0.95`)
* `value`: a decimal indicating value where 0 is black and 1 is colored or white (default: `0.75`)
* `image-size`: image size in pixels; they're square so this will be both height and width (default: `327`)
* `group-mode`: Somewhat buggy option to color groups of kanji instead of strokes. (default: `false`)
* `model`: name of the model containing kanji and diagram fields
* `src-field`: name of the field that contains the kanji
* `dst-field`: name of the field to save diagram to
* `diagrammed-characters`: which characters from the source field to produce diagrams for:
    * `all`: all characters
    * `kanji`: only kanji, not kana or anything else
    * `auto`: if there are some kanji and some other characters only include the kanji; otherwise include all characters
* `overwrite-dest`: set to true by default. If false the destination field will not be overwritten if there is anything in it.
* `grid`: options to draw a grid (default: `none`):
    * `none`: no grid
    * `2x2`: a 2x2 grid
    * `4x4`: a 4x4 grid
    * `diag`: diagonals
    * `2x2diag`: a 2x2 grid with diagonals
    * `4x4diag`: a 4x4 grid with diagonals

Some changes will not take effect until you restart anki.
