"""
Cut the estate pages' galleries from the live site's own photography.

    python _tools/place_live.py

place.py cuts from the sorted library on the D: drive. These frames come from
a different place -- thevalleyvenues.com, the client's live site, whose
per-venue pages carry photography the sorted library does not have (the
rebuilt Magnolia House, the tiny-home cottages, the Lodge interiors). They were
pulled once into a scratch folder and laid out on contact sheets; a frame is
referred to here by the page it came from and its index on that sheet, so a
pick reads as "lodging sheet, frame 12" rather than a forty-character upload
name.

Same rules as place.py. Nothing is upscaled: a slot that asks for more width
than the original has gets the original's width and the height scaled to
match. A vertical bias picks where the crop sits when the aspect changes.
"""
import glob, os
from PIL import Image, ImageStat, ImageEnhance

LIVE = (r"C:/Users/DAVE~1.MCC/AppData/Local/Temp/claude/C--Users-dave-mccormick-Something"
        r"/9113fdc1-8166-47e1-8097-b0e3ebb5a721/scratchpad/live/img")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")
TARGET = 0.55            # the same brightness nudge the rest of the site gets

# (destination, sheet, frame index, width, height, vertical bias)
# Galleries are 4:3 at 1000x750, matching the real-weddings wall. The one wide
# frame per page (nth 4n+1) is cut 1400x510 so nobody's head is cropped by
# object-fit, exactly as the gallery on real-weddings learned the hard way.
PICKS = [
    ('mh-1', 'magnolia-house', 16, 1400, 510, 0.55),
    ('mh-2', 'magnolia-house', 12, 1000, 750, 0.45),
    ('mh-3', 'magnolia-house', 13, 1000, 750, 0.40),
    ('mh-4', 'magnolia-house', 10, 1000, 750, 0.45),
    ('mh-5', 'magnolia-house', 0, 1400, 510, 0.50),
    ('mh-6', 'magnolia-house', 11, 1000, 750, 0.45),
    ('mh-7', 'magnolia-house', 8, 1000, 750, 0.45),
    ('mh-8', 'magnolia-house', 5, 1000, 750, 0.50),
    ('tv-1', 'the-valley', 0, 1400, 510, 0.45),
    ('tv-2', 'the-valley', 3, 1000, 750, 0.45),
    ('tv-3', 'the-valley', 2, 1000, 750, 0.45),
    ('tv-4', 'the-valley', 17, 1000, 750, 0.45),
    ('tv-5', 'the-valley', 5, 1400, 510, 0.55),
    ('tv-6', 'the-valley', 9, 1000, 750, 0.45),
    ('tv-7', 'the-valley', 18, 1000, 750, 0.50),
    ('tv-8', 'the-valley', 10, 1000, 750, 0.45),
    ('ld-1', 'lookout-deck', 1, 1400, 510, 0.45),
    ('ld-2', 'lookout-deck', 4, 1000, 750, 0.45),
    ('ld-3', 'lookout-deck', 11, 1000, 750, 0.45),
    ('ld-4', 'lookout-deck', 13, 1000, 750, 0.50),
    ('ld-5', 'lookout-deck', 6, 1400, 510, 0.50),
    ('ld-6', 'lookout-deck', 2, 1000, 750, 0.45),
    ('ld-7', 'lookout-deck', 9, 1000, 750, 0.45),
    ('ld-8', 'lookout-deck', 3, 1000, 750, 0.45),
    ('dh-1', 'davis-hall', 6, 1400, 510, 0.50),
    ('dh-2', 'davis-hall', 10, 1000, 750, 0.50),
    ('dh-3', 'davis-hall', 8, 1000, 750, 0.50),
    ('dh-4', 'davis-hall', 12, 1000, 750, 0.45),
    ('dh-5', 'davis-hall', 1, 1400, 510, 0.45),
    ('dh-6', 'davis-hall', 0, 1000, 750, 0.40),
    ('dh-7', 'davis-hall', 17, 1000, 750, 0.50),
    ('dh-8', 'davis-hall', 20, 1000, 750, 0.50),
    ('ov-1', 'lodging', 29, 1400, 510, 0.50),
    ('ov-2', 'lodging', 0, 1000, 750, 0.50),
    ('ov-3', 'lodging', 25, 1000, 750, 0.45),
    ('ov-4', 'lodging', 31, 1000, 750, 0.50),
    ('ov-5', 'lodging', 4, 1400, 510, 0.50),
    ('ov-6', 'lodging', 72, 1000, 750, 0.50),
    ('ov-7', 'lodging', 14, 1000, 750, 0.50),
    ('ov-8', 'lodging', 18, 1000, 750, 0.50),
]


def frame(sheet, index):
    hits = sorted(glob.glob(os.path.join(LIVE, sheet, "%03d-*" % index)))
    if not hits:
        raise SystemExit("no frame %d on the %s sheet" % (index, sheet))
    return hits[0]


def cut(src, W, H, bias):
    im = Image.open(src)
    im.draft("RGB", (W * 2, H * 2))
    im = im.convert("RGB")
    if im.width < W:                      # never invent pixels
        H = int(H * im.width / float(W)); W = im.width
    r = max(W / float(im.width), H / float(im.height))
    im = im.resize((max(W, int(im.width * r)), max(H, int(im.height * r))), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * bias)
    im = im.crop((x, y, x + W, y + H))
    lum = ImageStat.Stat(im.convert("L")).mean[0] / 255.0
    if lum < 0.46 or lum > 0.66:
        im = ImageEnhance.Brightness(im).enhance(max(0.85, min(1.25, TARGET / lum)))
    return im, W, H


def main():
    if not PICKS:
        raise SystemExit("PICKS is empty -- look at the contact sheets first")
    total = 0
    for dest, sheet, index, W, H, bias in PICKS:
        im, w, h = cut(frame(sheet, index), W, H, bias)
        path = os.path.join(OUT, dest + ".webp")
        im.save(path, quality=82, method=5)
        kb = os.path.getsize(path) // 1024
        total += kb
        print("%-22s %4dx%-4d %4dKB   %s #%d" % (dest, w, h, kb, sheet, index))
    print("\n%d frames, %d KB" % (len(PICKS), total))


if __name__ == "__main__":
    main()
