"""
Icons made from the photographs, in the estate's seven colours.

    python _tools/photo_icons.py        # writes map-lab/icons/<place>.png

A park map's buildings are portraits, so the honest source for them is the
real building. Each photograph is cropped to its subject, flattened (a median
filter takes out texture the way a brush would), and every pixel is moved to
the nearest of the palette colours. The result is a poster of the place that
could not have been painted in any colour the client did not choose.
"""
import os
from PIL import Image, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "map-lab", "icons")

PALETTE = ["#FFFFFF", "#FFF0DA", "#AABEB3", "#9A9F83", "#679AA7", "#B38A64", "#34372F"]

# photograph, crop box as fractions (left, top, right, bottom)
SOURCES = {
    "magnolia": ("mh-5", (.30, .12, .72, .98)),
    "valley":   ("close-single", (.18, .12, .82, 1.0)),
    "deck":     ("ld-1", (.00, .00, .42, 1.0)),
    "hall":     ("dh-1", (.28, .00, .70, 1.0)),
    "village":  ("ov-2", (.00, .08, 1.0, 1.0)),
    "woods":    ("stay", (.00, .04, .62, 1.0)),
}
SIZE = (360, 280)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


WHITE, CREAM, SAGE, OLIVE, BLUE, CLAY, DEEP = range(7)


def ink(r, g, b):
    """Which plate a pixel prints on. Nearest-colour sends every shaded leaf to
    the darkest ink and the picture goes muddy; a screen printer separates by
    what a colour is (foliage, sky, timber, shadow) and then by how light."""
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h *= 360
    if v < .2:
        return DEEP
    if s < .16:
        if v > .86:
            return WHITE
        if v > .66:
            return CREAM
        return SAGE if v > .42 else OLIVE if v > .28 else DEEP
    if 55 <= h < 165:                     # foliage and grass
        return SAGE if v > .72 else OLIVE if v > .3 else DEEP
    if 165 <= h < 260:                    # sky, glass, painted blue
        return WHITE if v > .9 and s < .3 else BLUE if s > .22 else SAGE
    if h < 55 or h >= 320:                # timber, brick, skin, clay
        if v > .82 and s < .35:
            return CREAM
        return CLAY if v > .3 else DEEP
    return BLUE if v > .35 else DEEP


def posterise(im):
    flat = []
    for hx in PALETTE:
        flat += rgb(hx)
    lut = {}
    px = im.load()
    out = Image.new("P", im.size)
    op = out.load()
    for y in range(im.height):
        for x in range(im.width):
            c = px[x, y]
            k = (c[0] >> 3, c[1] >> 3, c[2] >> 3)
            if k not in lut:
                lut[k] = ink(k[0] * 8 + 4, k[1] * 8 + 4, k[2] * 8 + 4)
            op[x, y] = lut[k]
    out.putpalette(flat + [0] * (768 - len(flat)))
    return out


def make(key, name, box):
    src = os.path.join(ROOT, "assets", "img", name + ".webp")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    # cover-fit to the icon's shape
    tw, th = SIZE
    s = max(tw / float(im.width), th / float(im.height))
    im = im.resize((int(im.width * s + .5), int(im.height * s + .5)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2
    im = im.crop((l, t, l + tw, t + th))
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Brightness(im).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5))
    out = posterise(im).filter(ImageFilter.ModeFilter(5))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, key + ".png")
    out.save(path, optimize=True)
    return path


def main():
    for key, (name, box) in SOURCES.items():
        p = make(key, name, box)
        print("  %-9s <- %-13s %4.0f KB" % (key, name, os.path.getsize(p) / 1024.0))


if __name__ == "__main__":
    main()
