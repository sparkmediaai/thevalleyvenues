"""
Cut the client's logo into the two pieces the site actually needs.

    python _build/make_logo.py

The supplied artwork is one stacked lockup: a magnolia bloom in a circle above
THE VALLEY VENUES above WEDDINGS & EVENTS. That shape is 1.5 times taller than
it is wide, which is wrong for a sticky masthead -- sized to keep the wordmark
readable it would be a 6rem header following you down every page, and sized to
fit a slim header the words inside it would be four pixels tall.

So it is cut at the blank band the artwork already has between the bloom and
the type (detected, not guessed):

    logo.webp        the full lockup, for the footer and anywhere with room
    logo-mark.webp   the bloom alone, for the masthead and small spaces

Both keep the original transparency. Neither is recoloured: the artwork is
black and the site's ink is #23291F, which is a visible difference on cream,
but a logo is the client's to change and not ours.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets")
SRC = r"D:/DevStuff/VV Images/VV Images/drive-download-20260904T154746Z-1-001/Logo.png"

# Exported at roughly twice the largest size either is displayed at, so they
# stay crisp on a retina screen without carrying a megabyte to do it.
FULL_W = 460
MARK_W = 240


def trim(im):
    box = im.getchannel("A").getbbox()
    return im.crop(box) if box else im


def rows_with_ink(alpha):
    px = alpha.load()
    w, h = alpha.size
    out = []
    for y in range(h):
        n = 0
        for x in range(0, w, 2):
            if px[x, y] > 24:
                n += 1
        out.append(n)
    return out


def first_gap(rows, least=20):
    """The first blank band tall enough to be a deliberate separation rather
    than the gap between two letters."""
    run = None
    for y, v in enumerate(rows):
        if v == 0:
            run = y if run is None else run
        elif run is not None:
            if y - run >= least:
                return run, y
            run = None
    return None


def save(im, name, width):
    if im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    path = os.path.join(OUT, name)
    im.save(path, "WEBP", quality=92, method=6, lossless=False, exact=True)
    print("%-18s %4dx%-4d %4d KB" % (name, im.width, im.height,
                                     os.path.getsize(path) // 1024))
    return im.size


def main():
    src = trim(Image.open(SRC).convert("RGBA"))
    gap = first_gap(rows_with_ink(src.getchannel("A")))
    if not gap:
        raise SystemExit("could not find the band between the bloom and the type")

    mark = trim(src.crop((0, 0, src.width, gap[0])))
    print("cut at y=%d-%d" % gap)
    save(src, "logo.webp", FULL_W)
    save(mark, "logo-mark.webp", MARK_W)


if __name__ == "__main__":
    main()
