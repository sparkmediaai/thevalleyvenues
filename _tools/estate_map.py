"""
Draw the estate map.

    python _tools/estate_map.py

Kobi's draft sketch settles the layout: where the buildings sit relative to one
another, how the drive loops around Magnolia House, which way the one-ways run,
where the vendors drop off and where guests park. That topology is taken as
given here. What is not taken from it is the drawing itself -- the sketch's
buildings are cartoon three-quarter views, and the brand direction is explicit
that the storybook feeling should come from atmosphere rather than costume. So
these are flat elevations in the estate palette: fine linework, no perspective,
no gloss.

Generated rather than hand-drawn for three reasons. The woodland is nine
hundred trees and nobody should be maintaining that by hand; the trees have to
keep clear of the roads, which is a containment test rather than an eye test;
and when a building moves, everything anchored to it should move with it.

Everything is one of the seven palette colours. The blue finally earns its
place: it is the creek.

Output is assets/map.svg, which the page styles and makes interactive -- this
script draws no hover states and no colours that a stylesheet should own.
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "map.svg")

W, H = 2000, 800
SEED = 20260913

# The palette, and nothing else.
IVORY = "#F5F1EA"
CREAM = "#FFF0DA"
OLIVE = "#9A9F83"
CLAY = "#B38A64"
BLUE = "#679AA7"
SAGE = "#AABEB3"
DEEP = "#34372F"

# ---------------------------------------------------------------- the places
# x, y is the anchor the building is drawn around; the label sits below it.
# Every position here is traced from Kobi's own site plan: her drawing was
# sampled, the drive colour separated from the woodland, and the result mapped
# into this 2000x800 frame, so the two maps agree to within a few feet.
PLACES = {
    "village":  dict(x=1240, y=112, label="Overlook Village",
                     href="/the-estate/overlook-village/", lx=1240, ly=246),
    "magnolia": dict(x=652,  y=372, label="Magnolia House",
                     href="/the-estate/magnolia-house/", lx=652, ly=316),
    # The lodge for the largest party, on the drive between the village and
    # the hall, where her older map has it.
    "lodge":    dict(x=1402, y=402, label="The Lodge",
                     href="/the-estate/the-lodge/", lx=1402, ly=452),
    # One structure, two named spaces: the deck is the hall's own wrap-around,
    # which is what the site plan shows and what the pamphlet says.
    "hall":     dict(x=1600, y=364, label="Davis Hall",
                     href="/the-estate/davis-hall/", lx=1560, ly=300),
    "deck":     dict(x=1830, y=396, label="The Lookout Deck",
                     href="/the-estate/lookout-deck/", lx=1830, ly=456),
    "valley":   dict(x=1520, y=548, label="The Valley",
                     href="/the-estate/the-valley/", lx=1520, ly=630),
    "woods":    dict(x=214,  y=706, label="Lost in the Woods",
                     href="/stay/", lx=214, ly=768),
}

# ----------------------------------------------------------------- the roads
# Her layout exactly: the climb to the village, the spine down the west side
# to the cottage, the one-way loop around Magnolia House, the run east under
# the courtyard, the fork where the entrance comes up off Pope Creek Road, and
# the climb to the hall's parking. Nothing runs to The Valley: it is walked to.
DRIVES = [
    # the entrance, up off Pope Creek Road to the fork
    ("M 828 650 C 888 652 948 646 984 634 C 1012 624 1031 606 1036 576 "
     "C 1042 540 1038 500 1022 466", "drive"),
    # the one-way east arm, from the roundabout under the courtyard to the fork
    ("M 596 428 C 612 464 646 488 692 496 C 726 503 762 487 790 468 "
     "C 822 449 900 437 962 442 C 990 446 1008 454 1022 466", "drive"),
    # the loop around Magnolia House: over the top, and the lower arm back
    ("M 380 414 C 392 374 424 350 470 345 C 520 340 568 360 590 398 "
     "C 594 408 596 418 596 428", "drive"),
    ("M 596 428 C 560 446 516 452 470 450 C 430 448 398 436 380 414", "drive"),
    # out of the loop, heading west, and exit only beyond it
    ("M 380 414 C 326 414 256 418 200 420 C 170 421 146 424 126 414", "drive"),
    # the long climb north-east to the village
    ("M 134 276 C 140 240 160 216 196 206 C 250 190 320 186 392 176 "
     "C 560 152 740 128 900 106 C 990 94 1080 80 1168 68", "drive"),
    # the west spine, down the property to the cottage in the woods
    ("M 134 276 C 130 316 126 352 120 392 C 112 434 96 472 86 514 "
     "C 74 562 58 610 62 650 C 66 684 86 704 120 712 C 152 720 186 716 214 710", "drive"),
    # the fork's other arm: east past the Lodge, then up to the hall's parking
    ("M 1022 466 C 1062 448 1124 438 1200 433 C 1248 430 1280 428 1296 418 "
     "C 1316 404 1324 380 1326 350 C 1330 310 1350 282 1384 268 "
     "C 1422 254 1468 262 1506 272 C 1528 278 1544 282 1554 286", "drive"),
    # the spur off it to the Lodge and the hall's door
    ("M 1327 356 C 1358 352 1396 350 1424 351 C 1434 351 1440 351 1446 351", "spur"),
]

# Pope Creek Road is public and is drawn differently: it is the only thing on
# the map that does not belong to the estate.
POPE = ("M 0 380 C 40 384 92 396 120 412 C 150 450 168 520 182 576 "
        "C 196 620 230 612 300 617 C 420 628 600 643 780 659 "
        "C 900 670 1040 684 1100 706 C 1130 730 1145 770 1150 800")

# Lookout Creek, which the pamphlet names and the sketch leaves out. It keeps
# to the low ground along the bottom, clear of her drives.
CREEK = ("M 120 800 C 240 782 420 766 600 758 C 760 752 900 758 1010 776 "
         "C 1070 786 1120 794 1160 800")

# ------------------------------------------------------- parking and wayfinding
PARKING = [(1560, 276, 190, 48), (1262, 436, 100, 32), (1064, 580, 134, 44)]

SIGNS = [
    (248, 444, "Exit only", "middle"),
    (428, 470, "One way", "middle"),
    (868, 470, "One way", "middle"),
    (843, 634, "Entrance", "end"),
    (470, 322, "Vendor drop-off", "middle"),
]

# Woodland, as polygons the trees are scattered inside.
WOODS = [
    [(150, 150), (420, 120), (760, 92), (1080, 64), (1120, 116), (800, 144), (460, 180), (180, 218)],
    [(150, 248), (360, 222), (416, 300), (378, 386), (200, 398), (138, 330)],
    [(178, 470), (340, 456), (380, 546), (300, 650), (160, 630), (130, 546)],
    [(430, 520), (900, 500), (980, 700), (700, 760), (450, 700)],
    [(1060, 492), (1232, 482), (1340, 566), (1150, 640), (1060, 580)],
    [(1180, 620), (1700, 600), (1980, 650), (1980, 780), (1300, 780)],
    [(1200, 150), (1560, 124), (1620, 240), (1300, 284), (1200, 240)],
    [(1770, 250), (2000, 230), (2000, 600), (1800, 560)],
    [(1570, 474), (1780, 464), (1820, 570), (1610, 590)],
]

# Which way the one-ways run. (index into DRIVES, fraction along it, flip)
ARROWS = [
    # The entrance path is drawn from the road upward, which is the way the
    # traffic goes, so it is not flipped.
    (0, .52, False),   # in off Pope Creek Road
    (1, .40, True),    # east arm: traffic runs west, against the drawing
    (1, .76, True),
    (2, .50, False),   # round the loop, over the top of the island
    (3, .50, False),   # and back along the lower arm
    (4, .50, False),   # out west, exit only
    (5, .42, False),   # up to the village
    (6, .62, False),   # down to the woods
    (7, .34, False),   # east toward the Lodge and the hall
]


# Nothing is planted within this of a drive, the creek or a building.
CLEAR_ROAD = 34
CLEAR_PLACE = 96


def pt_seg(px, py, ax, ay, bx, by):
    """Distance from a point to a segment."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def flatten(d, steps=26):
    """Every path here is M followed by cubics, which is all this has to read."""
    out = []
    nums, cur, i = [], "", 0
    tok = d.replace(",", " ").split()
    cmd = None
    pos = (0.0, 0.0)
    i = 0
    while i < len(tok):
        t = tok[i]
        if t in ("M", "C"):
            cmd = t
            i += 1
            continue
        if cmd == "M":
            pos = (float(tok[i]), float(tok[i + 1]))
            out.append(pos)
            i += 2
            cmd = "C"
            continue
        x1, y1, x2, y2, x3, y3 = (float(v) for v in tok[i:i + 6])
        p0 = pos
        for s in range(1, steps + 1):
            u = s / steps
            m = 1 - u
            x = (m ** 3 * p0[0] + 3 * m * m * u * x1 + 3 * m * u * u * x2 + u ** 3 * x3)
            y = (m ** 3 * p0[1] + 3 * m * m * u * y1 + 3 * m * u * u * y2 + u ** 3 * y3)
            out.append((x, y))
        pos = (x3, y3)
        i += 6
    return out


def arrow_at(path, t, flip=False):
    """A chevron sitting on the path, pointing the way the traffic goes."""
    pts = flatten(path)
    i = max(1, min(len(pts) - 1, int(t * (len(pts) - 1))))
    (x0, y0), (x1, y1) = pts[i - 1], pts[i]
    a = math.degrees(math.atan2(y1 - y0, x1 - x0)) + (180 if flip else 0)
    return ('<g class="map-arrow" transform="translate(%.0f %.0f) rotate(%.1f)">'
            '<path d="M -5 -5 L 4 0 L -5 5" fill="none" stroke="%s" stroke-width="2.4" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>'
            % (x1, y1, a, CREAM))


def inside(poly, x, y):
    hit = False
    n = len(poly)
    for a in range(n):
        b = (a + 1) % n
        xa, ya = poly[a]
        xb, yb = poly[b]
        if (ya > y) != (yb > y) and x < (xb - xa) * (y - ya) / (yb - ya + 1e-9) + xa:
            hit = not hit
    return hit


def fir_symbol():
    """One fir, defined once and referenced by every tree on the map.

    Eight hundred copies of three tier paths came to 165KB of markup. A symbol
    and eight hundred <use> elements, grouped so the tone sits on the group
    rather than on each tree, is about a third of that -- and the drawing is
    identical."""
    tiers = []
    w, h = 13.0, 30.0
    for ty, tw in ((0.00, 0.52), (0.34, 0.78), (0.66, 1.0)):
        top = -h + ty * h
        half = w * tw / 2
        base = top + h * 0.42
        tiers.append("M 0 %.0f Q %.0f %.0f %.0f %.0f Q %.0f %.0f %.0f %.0f Z" % (
            top, half * 0.72, base - h * 0.10, half, base,
            0, base + h * 0.055, -half, base))
    return ('<symbol id="vv-fir" overflow="visible">'
            '<path d="%s"/></symbol>' % " ".join(tiers))


# ------------------------------------------------------------------ buildings
def magnolia(x, y):
    """Four columns, a pediment, and the conservatory glazing behind."""
    b = []
    # the lawn the house sits on
    b.append('<ellipse cx="%d" cy="%d" rx="104" ry="26" fill="%s" opacity=".35"/>'
             % (x, y + 46, OLIVE))
    # the conservatory, glazed, joined to the east end of the house
    b.append('<rect x="%d" y="%d" width="56" height="42" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x + 48, y + 4, BLUE, DEEP))
    b.append('<rect x="%d" y="%d" width="56" height="42" fill="%s" stroke="%s" stroke-width="1.6" opacity=".45"/>'
             % (x + 48, y + 4, CREAM, DEEP))
    for i in range(4):
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width=".9" opacity=".7"/>'
                 % (x + 48 + i * 14, y + 4, x + 48 + i * 14, y + 46, DEEP))
    # the house
    b.append('<rect x="%d" y="%d" width="96" height="44" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>'
             % (x - 48, y + 2, DEEP))
    b.append('<path d="M %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.8" stroke-linejoin="round"/>'
             % (x - 56, y + 2, x, y - 30, x + 56, y + 2, CREAM, DEEP))
    for i in range(4):
        cx = x - 34 + i * 23
        b.append('<rect x="%d" y="%d" width="6" height="42" fill="%s" stroke="%s" stroke-width="1.2"/>'
                 % (cx, y + 3, CREAM, DEEP))
    b.append('<rect x="%d" y="%d" width="14" height="22" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (x - 7, y + 24, CLAY, DEEP))
    b.append('<rect x="%d" y="%d" width="112" height="5" rx="2" fill="%s"/>' % (x - 56, y + 46, DEEP))
    return "".join(b)


def village(x, y):
    """Four shed-roofed cottages stepping along the hill, each facing out."""
    b = ['<path d="M %d %d C %d %d %d %d %d %d L %d %d Z" fill="%s" opacity=".45"/>'
         % (x - 104, y + 78, x - 40, y + 52, x + 60, y + 62, x + 118, y + 96,
            x - 104, y + 96, OLIVE)]
    for i in range(4):
        ox = x - 70 + i * 46
        oy = y + i * 7
        b.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
                 'stroke-width="1.6" stroke-linejoin="round"/>'
                 % (ox, oy + 12, ox + 40, oy - 12, ox + 40, oy + 2, ox, oy + 26, CLAY, DEEP))
        b.append('<rect x="%d" y="%d" width="40" height="30" fill="#FFFFFF" stroke="%s" stroke-width="1.6"/>'
                 % (ox, oy + 26, DEEP))
        b.append('<rect x="%d" y="%d" width="15" height="15" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (ox + 5, oy + 32, BLUE, DEEP))
        # the stilts the cottages stand on, facing the valley
        for sx in (ox + 5, ox + 33):
            b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.2"/>'
                     % (sx, oy + 56, sx, oy + 68, DEEP))
    return "".join(b)


def hall(x, y):
    """The long white hall. Its deck is drawn by deck(), attached to this."""
    b = []
    b.append('<rect x="%d" y="%d" width="200" height="48" fill="#FFFFFF" stroke="%s" stroke-width="1.8"/>'
             % (x - 110, y - 6, DEEP))
    b.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
             'stroke-width="1.8" stroke-linejoin="round"/>'
             % (x - 118, y - 6, x - 98, y - 30, x + 88, y - 30, x + 98, y - 6, DEEP, DEEP))
    for i in range(7):
        b.append('<rect x="%d" y="%d" width="14" height="18" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (x - 98 + i * 27, y + 8, CREAM, DEEP))
    return "".join(b)


def deck(x, y):
    """The wrap-around: a band along the hall's front, widening off its east end.

    Drawn as one continuous platform because that is what it is -- the site plan
    labels the hall and the deck together and the pamphlet calls it a wrap-around,
    so a map that put them a walk apart would be telling a story the estate does
    not support."""
    b = []
    # the band running back along the front of the hall
    b.append('<rect x="%d" y="%d" width="%d" height="16" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (x - 250, y + 10, 250, CLAY, DEEP))
    # the deck proper, out over the fall of the land
    b.append('<rect x="%d" y="%d" width="104" height="46" rx="2" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x - 6, y - 20, CLAY, DEEP))
    for i in range(9):
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width=".7" opacity=".45"/>'
                 % (x - 2 + i * 12, y - 18, x - 2 + i * 12, y + 24, DEEP))
    # the rail, on the two open sides
    b.append('<path d="M %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (x - 6, y + 26, x + 98, y + 26, x + 98, y - 20, DEEP))
    for i in range(8):
        b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.1"/>'
                 % (x + 2 + i * 12, y + 26, x + 2 + i * 12, y + 16, DEEP))
    return "".join(b)


def valley(x, y):
    """The meadow: the arch at the top of an aisle, and the chairs either side."""
    b = []
    b.append('<ellipse cx="%d" cy="%d" rx="108" ry="62" fill="%s" opacity=".40"/>' % (x, y + 6, OLIVE))
    for side in (-1, 1):
        for r in range(6):
            for c in range(5):
                cx = x + side * (17 + c * 13)
                cy = y - 26 + r * 13
                b.append('<rect x="%.1f" y="%.1f" width="7" height="8" rx="1" fill="#FFFFFF" '
                         'stroke="%s" stroke-width=".55"/>' % (cx - 3.5, cy, DEEP))
    # the aisle
    b.append('<rect x="%d" y="%d" width="20" height="88" fill="%s" opacity=".55"/>'
             % (x - 10, y - 30, CREAM))
    # the arbour at the head of the aisle: two posts and a beam across
    b.append('<rect x="%d" y="%d" width="7" height="46" fill="#FFFFFF" stroke="%s" stroke-width="1.3"/>'
             % (x - 26, y - 34, DEEP))
    b.append('<rect x="%d" y="%d" width="7" height="46" fill="#FFFFFF" stroke="%s" stroke-width="1.3"/>'
             % (x + 19, y - 34, DEEP))
    b.append('<rect x="%d" y="%d" width="63" height="8" fill="#FFFFFF" stroke="%s" stroke-width="1.3"/>'
             % (x - 31, y - 40, DEEP))
    b.append('<path d="M %d %d q 10 -9 20 0 q 10 -9 20 0" fill="none" stroke="%s" '
             'stroke-width="3" stroke-linecap="round" opacity=".8"/>' % (x - 24, y - 40, OLIVE))
    return "".join(b)


def woods(x, y):
    """One cabin, a deep porch, and nothing else near it."""
    b = []
    b.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>'
             % (x - 46, y + 6, x - 30, y - 16, x + 48, y - 16, x + 40, y + 6, DEEP, DEEP))
    b.append('<rect x="%d" y="%d" width="74" height="34" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x - 40, y + 6, CLAY, DEEP))
    b.append('<rect x="%d" y="%d" width="18" height="22" fill="%s" stroke="%s" stroke-width="1"/>'
             % (x - 30, y + 14, BLUE, DEEP))
    b.append('<rect x="%d" y="%d" width="16" height="16" fill="%s" stroke="%s" stroke-width="1"/>'
             % (x + 6, y + 14, CREAM, DEEP))
    b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.4"/>'
             % (x + 40, y + 6, x + 40, y + 40, DEEP))
    return "".join(b)


DRAW = {"magnolia": magnolia, "village": village, "hall": hall,
        "deck": deck, "valley": valley, "woods": woods}


def build(**opt):
    """Return the map as markup.

    Options exist so the lab can ask for variants without a second copy of the
    drawing: `ground`/`ink`/`wood`/`road` override palette slots, `labels=False`
    leaves the naming to HTML, and `seed` replants the woodland."""
    rng = random.Random(opt.get("seed", SEED))
    ground = opt.get("ground", CREAM)
    wood = opt.get("wood", OLIVE)
    wood2 = opt.get("wood2", SAGE)
    road = opt.get("road", CLAY)

    # Everything a tree has to keep away from.
    keep = []
    for d, _ in DRIVES:
        keep += flatten(d)
    keep += flatten(POPE)
    keep += flatten(CREEK)
    segs = [(keep[i], keep[i + 1]) for i in range(len(keep) - 1)
            if math.hypot(keep[i + 1][0] - keep[i][0], keep[i + 1][1] - keep[i][1]) < 60]

    trees = []
    for poly in WOODS:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        target = int(abs((max(xs) - min(xs)) * (max(ys) - min(ys))) / 900)
        tries = 0
        placed = 0
        while placed < target and tries < target * 40:
            tries += 1
            x = rng.uniform(min(xs), max(xs))
            y = rng.uniform(min(ys), max(ys))
            if not inside(poly, x, y):
                continue
            if any(math.hypot(x - p["x"], y - p["y"]) < CLEAR_PLACE for p in PLACES.values()):
                continue
            if any(pt_seg(x, y, a[0], a[1], b[0], b[1]) < CLEAR_ROAD for a, b in segs):
                continue
            trees.append((y, x, rng.uniform(.72, 1.18), rng.random()))
            placed += 1
    trees.sort()  # painter's order, so the near ones overlap the far ones

    p = []
    p.append('<svg class="estate-map" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
             'xmlns:xlink="http://www.w3.org/1999/xlink" role="img" '
             'aria-label="An illustrated map of the estate: six places, the drives between '
             'them, and the way in from Pope Creek Road">' % (W, H))

    p.append('<rect class="map-ground" width="%d" height="%d" fill="%s"/>' % (W, H, ground))

    # the creek
    p.append('<path class="map-creek" d="%s" fill="none" stroke="%s" stroke-width="5" '
             'stroke-linecap="round" opacity=".7"/>' % (CREEK, BLUE))

    # the public road, then the estate drives
    p.append('<g class="map-pope"><path d="%s" fill="none" stroke="%s" stroke-width="15" '
             'stroke-linecap="round"/><path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="9 11" stroke-linecap="round" opacity=".65"/></g>'
             % (POPE, DEEP, POPE, CREAM))

    p.append('<g class="map-drives">')
    for d, kind in DRIVES:
        w = 15 if kind == "drive" else 9
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" stroke-linecap="round"/>'
                 % (d, road, w))
    for d, kind in DRIVES:
        if kind == "drive":
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                     'stroke-dasharray="9 11" stroke-linecap="round" opacity=".8"/>' % (d, CREAM))
    p.append('</g>')

    # Woodland. Depth without leaving the palette: one olive, one sage, and the
    # cream ground showing through at a few strengths. Grouped by tone so the
    # fill and the opacity are written once each rather than once per tree.
    p.append('<defs>%s</defs>' % fir_symbol())
    buckets = {}
    for y, x, sc, t in trees:
        near = max(0.0, min(1.0, (y - 60) / float(H)))
        fill = wood2 if t > .82 else wood
        step = round(.58 + .42 * near, 1)
        buckets.setdefault((fill, step), []).append((x, y, sc))
    p.append('<g class="map-woods">')
    for (fill, alpha), items in sorted(buckets.items(), key=lambda kv: kv[0][1]):
        p.append('<g fill="%s" opacity="%s">' % (fill, alpha))
        for x, y, sc in items:
            p.append('<use href="#vv-fir" transform="translate(%.0f %.0f) scale(%.2f)"/>'
                     % (x, y, sc))
        p.append('</g>')
    p.append('</g>')

    # which way round
    p.append('<g class="map-arrows">')
    for idx, t, flip in ARROWS:
        p.append(arrow_at(DRIVES[idx][0], t, flip))
    p.append('</g>')

    # parking, over the woodland rather than under it
    p.append('<g class="map-parking">')
    for x, y, w, h in PARKING:
        p.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s" opacity=".85"/>'
                 % (x, y, w, h, SAGE))
        p.append('<text class="map-sign" x="%d" y="%d" text-anchor="middle">Parking</text>'
                 % (x, y + 5))
    p.append('</g>')

    # wayfinding
    p.append('<g class="map-wayfinding">')
    for x, y, text, anchor in SIGNS:
        p.append('<text class="map-sign" x="%d" y="%d" text-anchor="%s">%s</text>'
                 % (x, y, anchor, text))
    p.append('</g>')

    # the places themselves, each a link
    p.append('<g class="map-places">')
    for key, pl in PLACES.items():
        p.append('<a class="map-place map-%s" data-place="%s" href="%s" xlink:href="%s" '
                 'aria-label="%s">' % (key, key, pl["href"], pl["href"], pl["label"]))
        p.append('<circle class="map-halo" cx="%d" cy="%d" r="74"/>' % (pl["x"], pl["y"]))
        p.append('<g class="map-art">%s</g>' % DRAW[key](pl["x"], pl["y"]))
        if opt.get("labels", True):
            p.append('<text class="map-label" x="%d" y="%d" text-anchor="middle">%s</text>'
                     % (pl.get("lx", pl["x"]), pl["ly"], pl["label"]))
        p.append('</a>')
    p.append('</g>')

    # Lookout Mountain, in the corner the sketch puts it
    p.append('<g class="map-mountains" opacity=".5">'
             '<path d="M 1748 800 L 1868 596 L 1936 704 L 1974 644 L 2000 692 L 2000 800 Z" fill="%s"/>'
             '<path d="M 1840 644 L 1868 596 L 1898 644 L 1870 660 Z" fill="%s"/>'
             '</g>' % (OLIVE, CREAM))

    # An optional line through the places in the order a weekend meets them,
    # for the variations that walk a marker along it.
    if opt.get("route"):
        order = ["magnolia", "valley", "deck", "hall", "village"]
        pts = [(PLACES[k]["x"], PLACES[k]["y"]) for k in order]
        d = "M %d %d" % pts[0]
        for i in range(1, len(pts)):
            (x0, y0), (x1, y1) = pts[i - 1], pts[i]
            # bowed, so the line reads as a walk rather than a ruler
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0 - 46
            d += " Q %.0f %.0f %d %d" % (cx, cy, x1, y1)
        p.append('<path class="map-route" d="%s" fill="none"/>' % d)
        for i, k in enumerate(order):
            p.append('<circle class="map-stop" data-stop="%d" data-place="%s" '
                     'cx="%d" cy="%d" r="9"/>' % (i, k, PLACES[k]["x"], PLACES[k]["y"]))

    p.append('</svg>')

    return "".join(p), len(trees)


def main():
    svg, n = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("%s  %d trees, %d places, %.0f KB"
          % (os.path.relpath(OUT), n, len(PLACES), len(svg) / 1024.0))


if __name__ == "__main__":
    main()
