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
PLACES = {
    "village":  dict(x=1230, y=112, label="Overlook Village",
                     href="/the-estate/overlook-village/", lx=1230, ly=246),
    "magnolia": dict(x=650,  y=372, label="Magnolia House",
                     href="/the-estate/magnolia-house/", lx=650, ly=316),
    # One structure, two named spaces: the deck is the hall's own wrap-around,
    # which is what the site plan shows and what the pamphlet says.
    "hall":     dict(x=1500, y=352, label="Davis Hall",
                     href="/the-estate/davis-hall/", lx=1452, ly=300),
    "deck":     dict(x=1640, y=386, label="The Lookout Deck",
                     href="/the-estate/lookout-deck/", lx=1706, ly=440),
    "valley":   dict(x=1370, y=560, label="The Valley",
                     href="/the-estate/the-valley/", lx=1370, ly=642),
    "woods":    dict(x=210,  y=690, label="Lost in the Woods",
                     href="/stay/", lx=210, ly=762),
}

# ----------------------------------------------------------------- the roads
# Estate drives, in the order they are travelled. Each is (path, kind).
DRIVES = [
    # the entrance, up off Pope Creek Road
    ("M 1075 800 C 1075 720 1040 660 1010 610 C 980 560 975 520 975 470", "drive"),
    # the one-way east arm, past the courtyard toward the hall
    ("M 975 470 C 1080 470 1160 456 1228 444 C 1292 432 1340 424 1392 420", "drive"),
    # the one-way loop around Magnolia House, closed
    ("M 975 470 C 900 486 840 492 786 490 "
     "C 676 498 566 486 522 456 C 486 430 508 398 572 386 "
     "C 652 372 742 378 792 400 C 828 416 822 450 792 468 "
     "C 784 474 790 484 786 490", "drive"),
    # out of the loop, heading west
    ("M 522 456 C 460 468 380 470 300 466", "drive"),
    # the vendor spur, behind the house
    ("M 560 390 C 512 362 476 342 440 334", "spur"),
    # exit only, running west
    ("M 300 466 C 240 470 190 466 150 452", "drive"),
    # the long climb north-east to the village
    ("M 150 452 C 108 430 112 372 128 318 C 146 258 200 222 268 206 "
     "C 420 172 700 140 900 118 C 1010 106 1100 98 1180 94", "drive"),
    # down to the cottage in the woods
    ("M 150 452 C 118 490 96 540 92 592 C 88 648 118 686 165 700", "drive"),
    # the hall's own approach and its parking
    ("M 1392 420 C 1420 398 1436 360 1452 330 C 1470 296 1508 282 1548 282", "drive"),
    # down to the meadow
    ("M 1392 420 C 1388 460 1380 492 1372 520", "spur"),
]

# Pope Creek Road is public and is drawn differently: it is the only thing on
# the map that does not belong to the estate.
POPE = ("M 0 372 C 60 372 96 388 118 420 C 150 466 156 520 168 566 "
        "C 182 620 236 646 320 656 C 470 674 700 700 880 740 "
        "C 980 762 1040 780 1075 800")

# Lookout Creek, which the pamphlet names and the sketch leaves out.
CREEK = ("M 236 800 C 288 744 318 694 362 656 C 416 610 472 596 546 592 "
         "C 630 588 706 610 772 646 C 840 682 896 716 946 754")

# ------------------------------------------------------- parking and wayfinding
PARKING = [(1596, 268, 104, 34), (1286, 458, 72, 24), (1112, 590, 80, 28)]

SIGNS = [
    (286, 452, "Exit only", "middle"),
    (640, 512, "One way", "middle"),
    (896, 456, "One way", "middle"),
    (962, 648, "Entrance", "end"),
    (416, 326, "Vendor drop-off", "middle"),
]

# Woodland, as polygons the trees are scattered inside.
WOODS = [
    [(120, 150), (620, 92), (1160, 60), (1160, 132), (620, 176), (150, 246)],
    [(96, 250), (330, 214), (360, 300), (300, 420), (150, 430), (86, 340)],
    [(180, 480), (330, 470), (360, 560), (300, 660), (150, 640), (120, 540)],
    [(420, 500), (900, 480), (980, 700), (700, 760), (440, 700)],
    [(1040, 470), (1300, 440), (1340, 560), (1150, 640), (1040, 580)],
    [(1180, 600), (1700, 590), (1980, 640), (1980, 780), (1300, 780)],
    [(1400, 180), (1760, 170), (1800, 300), (1500, 320)],
    [(1770, 250), (2000, 230), (2000, 600), (1800, 560)],
    [(1000, 150), (1330, 120), (1380, 300), (1060, 330)],
    [(1420, 460), (1620, 470), (1660, 570), (1440, 580)],
]

# Which way the one-ways run. (index into DRIVES, fraction along it, flip)
ARROWS = [
    # The path is drawn from the road upward and that is the way the traffic
    # goes, so this one is not flipped.
    (0, .52, False),   # in off Pope Creek Road
    (1, .34, False),   # east toward the hall
    (1, .78, False),
    (2, .18, False),   # round the loop, anticlockwise
    (2, .56, False),
    (2, .86, False),
    (3, .55, False),   # out west
    (5, .50, False),   # exit only
    (6, .42, False),   # up to the village
    (7, .55, False),   # down to the woods
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
