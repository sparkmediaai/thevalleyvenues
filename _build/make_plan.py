"""
Draw the estate as a contour plan, from the survey rather than from imagination.

The Estate page argues that there are not four venues, there is one property.
A photograph cannot make that argument -- it can only show one place at a time,
which is the same thing the old dropdown did. A plan can, because the distance
between the places is the argument.

So this reads the heightmap the 3D model was built from (USGS 3DEP one-metre
LiDAR, resampled to a 256-square over an 800-metre box) and walks contours
through it with marching squares. The output is an SVG the page inlines, so CSS
can light each place as its section scrolls past and draw the route between
them.

    python _build/make_plan.py

Nothing here is drawn by hand. The lines are the actual shape of the ground,
which is the only reason this is worth doing at all -- an invented squiggle
would look the same to a visitor and be worth nothing to the client.
"""
import json, math, os
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "terrain")
OUT = os.path.join(os.path.dirname(HERE), "assets", "plan.svg")
ICON = os.path.join(os.path.dirname(HERE), "assets", "favicon.svg")

VIEW = 1000.0            # svg user units across the whole 800 m box
# The six places sit in the middle 40% of the box, so the drawing is cropped to
# them. Contours are still walked across the whole square -- the ridge running
# off the edge is what makes it read as a piece of a bigger landscape rather
# than an island.
# Wide enough for the labels, not just the dots: at mobile type sizes a name
# like "Magnolia House" runs about 175 units back from its mark, which the
# first crop crossed straight through.
CROP = (140, 250, 790, 560)     # x, y, w, h
STEP = 5.0               # metres between contours
INDEX_EVERY = 3          # every third line is drawn heavier

# Where each name sits relative to its dot, so six labels in a small area do
# not land on top of each other or on the route.
LABELS = {
    "arrival":  ("end",    -16,   6),
    "magnolia": ("end",    -16,  -4),
    "valley":   ("start",   16,   6),
    "deck":     ("end",    -16,  -4),
    "hall":     ("start",   16,  14),
    "village":  ("middle",   0, -26),
}

# Read from aerial imagery for the 3D model, in box-relative coordinates.
# These are approximate and want confirming against a real site plan before
# anything is published with distances on it.
PLACES = [
    ("arrival",   "Arrival",          0.443, 0.596),
    ("magnolia",  "Magnolia House",   0.398, 0.547),
    ("valley",    "The Valley",       0.727, 0.561),
    ("deck",      "Lookout Deck",     0.352, 0.450),
    ("hall",      "Davis Hall",       0.597, 0.499),
    ("village",   "Overlook Village", 0.506, 0.415),
]
# The order of a weekend, which is the order the page moves through them.
ROUTE = ["arrival", "magnolia", "valley", "deck", "hall", "village"]

# Which places have a page of their own under /the-estate/.
PAGE_FOR = {"magnolia": "magnolia-house", "valley": "the-valley",
            "deck": "lookout-deck", "hall": "davis-hall", "village": "overlook-village"}


# ---------------------------------------------------------------- contours
def marching_squares(f, n, level):
    """Line segments where the field crosses `level`.

    The textbook version, with the saddle cases resolved by the cell average.
    Ambiguity matters here: a wrong saddle joins two hillsides that are not
    joined, and on a plan of somebody's land that is a lie rather than an
    artefact.
    """
    segs = []

    def ip(x0, y0, v0, x1, y1, v1):
        t = 0.5 if v1 == v0 else (level - v0) / (v1 - v0)
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)

    for j in range(n - 1):
        row, nxt = j * n, (j + 1) * n
        for i in range(n - 1):
            a, b = f[row + i], f[row + i + 1]
            c, d = f[nxt + i + 1], f[nxt + i]
            code = (1 if a > level else 0) | (2 if b > level else 0) \
                 | (4 if c > level else 0) | (8 if d > level else 0)
            if code == 0 or code == 15:
                continue
            top = ip(i, j, a, i + 1, j, b)
            right = ip(i + 1, j, b, i + 1, j + 1, c)
            bottom = ip(i + 1, j + 1, c, i, j + 1, d)
            left = ip(i, j + 1, d, i, j, a)
            if code in (1, 14):
                segs.append((left, top))
            elif code in (2, 13):
                segs.append((top, right))
            elif code in (3, 12):
                segs.append((left, right))
            elif code in (4, 11):
                segs.append((right, bottom))
            elif code in (6, 9):
                segs.append((top, bottom))
            elif code in (7, 8):
                segs.append((left, bottom))
            elif code in (5, 10):
                mid = (a + b + c + d) / 4.0
                if (mid > level) == (code == 5):
                    segs.append((left, top)); segs.append((right, bottom))
                else:
                    segs.append((left, bottom)); segs.append((top, right))
    return segs


def chain(segs):
    """Join loose segments into polylines, so each contour is one path."""
    ends = {}
    def key(p):
        return (round(p[0], 4), round(p[1], 4))
    for s in segs:
        ends.setdefault(key(s[0]), []).append(s)
        ends.setdefault(key(s[1]), []).append(s)
    used, lines = set(), []
    for s0 in segs:
        if id(s0) in used:
            continue
        used.add(id(s0))
        line = [s0[0], s0[1]]
        for end in (0, 1):                       # grow both ways
            while True:
                tip = line[-1] if end == 0 else line[0]
                nxt = None
                for cand in ends.get(key(tip), ()):
                    if id(cand) in used:
                        continue
                    nxt = cand
                    break
                if nxt is None:
                    break
                used.add(id(nxt))
                far = nxt[1] if key(nxt[0]) == key(tip) else nxt[0]
                if end == 0:
                    line.append(far)
                else:
                    line.insert(0, far)
        if len(line) > 6:                        # drop specks
            lines.append(line)
    return lines


def smooth(pts, rounds=2):
    """Chaikin. The ground is not polygonal and neither is a survey drawing."""
    closed = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6
    for _ in range(rounds):
        out = [] if closed else [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out.append((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25))
            out.append((a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75))
        if closed:
            out.append(out[0])
        else:
            out.append(pts[-1])
        pts = out
    return pts


def thin(pts, tol):
    """Keep a point only once the line has wandered `tol` from the last kept
    one. Crude beside Douglas-Peucker and quite good enough: this is the
    difference between 180KB of path data inline on the page and 30."""
    out = [pts[0]]
    for p in pts[1:-1]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) >= tol:
            out.append(p)
    out.append(pts[-1])
    return out


def write_icon(rings, scale):
    """A favicon cut from the estate's own high ground.

    Three nested closed contours around the highest point on the property,
    normalised into a 32-square. A drawn monogram would have done the job, but
    this is the same drawing as the map and the same hill as the deck looks
    from, which is a better reason for a shape to exist.
    """
    tops = [r for r in rings if len(r[1]) > 12]
    if not tops:
        return
    peak = max(lv for lv, _ in tops)
    # the ring nearest the top, then the two below it that contain it
    def centre(line):
        return (sum(p[0] for p in line) / len(line),
                sum(p[1] for p in line) / len(line))
    highest = [r for r in tops if r[0] == peak]
    cx0, cy0 = centre(highest[0][1])
    chosen = []
    for lv in sorted({lv for lv, _ in tops}, reverse=True)[:3]:
        same = [ln for l2, ln in tops if l2 == lv]
        same.sort(key=lambda ln: math.hypot(centre(ln)[0] - cx0, centre(ln)[1] - cy0))
        chosen.append(same[0])

    pts = [p for ln in chosen for p in ln]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) or 1.0
    k = 26.0 / span
    ox = 16 - (x0 + x1) / 2 * k
    oy = 16 - (y0 + y1) / 2 * k

    paths = []
    for i, ln in enumerate(chosen):
        d = "M" + " L".join("%.1f %.1f" % (x * k + ox, y * k + oy)
                            for x, y in ln) + " Z"
        paths.append('<path d="%s" stroke-width="%.2f"/>' % (d, 1.5 - i * 0.25))

    icon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32" rx="6" fill="#23291F"/>'
            '<g fill="none" stroke="#F7E7CE" stroke-linejoin="round">%s</g>'
            '</svg>') % "".join(paths)
    open(ICON, "w", encoding="utf-8").write(icon)
    print("%s  three rings from the high ground" % ICON)


def main():
    meta = json.load(open(os.path.join(SRC, "terrain.json"), encoding="utf-8"))
    lo, hi, n = meta["minElev"], meta["maxElev"], meta["grid"]

    im = Image.open(os.path.join(SRC, "terrain.png")).convert("L")
    # A light blur before contouring. The source is one-metre LiDAR and every
    # tree stump in it becomes a closed ring otherwise.
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    px = list(im.convert("L").tobytes())
    field = [lo + (v / 255.0) * (hi - lo) for v in px]

    scale = VIEW / (n - 1)
    levels = []
    e = math.ceil(lo / STEP) * STEP
    while e < hi:
        levels.append(e)
        e += STEP

    body, minor, major = [], 0, 0
    rings = []                       # closed contours, for the favicon
    for k, level in enumerate(levels):
        paths = []
        for line in chain(marching_squares(field, n, level)):
            line = thin(smooth(line), 1.15)
            if len(line) < 4:
                continue
            if math.hypot(line[0][0] - line[-1][0], line[0][1] - line[-1][1]) < 1.5:
                rings.append((level, line))
            d = "M" + " L".join("%.1f %.1f" % (x * scale, y * scale)
                                for x, y in line)
            paths.append(d)
        if not paths:
            continue
        index = (k % INDEX_EVERY == 0)
        cls = "c-index" if index else "c-line"
        if index:
            major += len(paths)
        else:
            minor += len(paths)
        body.append('<g class="%s" data-elev="%d">%s</g>' % (
            cls, level, "".join('<path d="%s"/>' % d for d in paths)))

    # --- the places and the route ------------------------------------------
    at = {k: (u * VIEW, v * VIEW) for k, _, u, v in PLACES}

    # One path per leg, not one path for the route, because each leg is drawn
    # by its own section of the page as that section scrolls into view.
    #
    # The legs bow, alternately left and right. Two of them run nearly along the
    # same line -- the meadow is east and the deck is west, so the walk doubles
    # back across the property -- and drawn straight they lie on top of one
    # another. The bow is a diagram convention rather than a claim about a
    # footpath: these are distances between points, and the labels say so.
    legs = []
    for i, (a, b) in enumerate(zip(ROUTE, ROUTE[1:])):
        (x0, y0), (x1, y1) = at[a], at[b]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        k = 0.13 * L * (1 if i % 2 == 0 else -1)
        cx, cy = mx - dy / L * k, my + dx / L * k
        metres = L / VIEW * meta["metresWide"]

        # Length of the curve, walked in a hundred steps. CSS needs a number to
        # animate stroke-dashoffset from, and getTotalLength() would mean
        # shipping JavaScript to do arithmetic that can be done once, here.
        arc, px_, py_ = 0.0, x0, y0
        for t in (n_ / 100.0 for n_ in range(1, 101)):
            u_ = 1 - t
            qx = u_ * u_ * x0 + 2 * u_ * t * cx + t * t * x1
            qy = u_ * u_ * y0 + 2 * u_ * t * cy + t * t * y1
            arc += math.hypot(qx - px_, qy - py_)
            px_, py_ = qx, qy

        # The distance label sits at the apex of the bow, pushed a little
        # further out so it clears the line it belongs to.
        tx = 0.25 * x0 + 0.5 * cx + 0.25 * x1 - dy / L * (k * 0.95)
        ty = 0.25 * y0 + 0.5 * cy + 0.25 * y1 + dx / L * (k * 0.95)
        # Only the two long legs are labelled on the drawing. Every distance is
        # already written into the step beside it, and five figures on a map
        # this size pile up around Davis Hall, where three of the places are
        # within two hundred metres of each other.
        label = ('<text class="leg-m" x="%.1f" y="%.1f">%d m</text>'
                 % (tx, ty, round(metres))) if metres >= 250 else ""
        legs.append(
            '<g class="leg-g lg-%d">'
            '<path class="leg" style="--len:%.0f" d="M%.1f %.1f Q%.1f %.1f %.1f %.1f"/>'
            '%s</g>'
            % (i + 1, arc, x0, y0, cx, cy, x1, y1, label))

    marks = []
    for k, name, u, v in PLACES:
        x, y = u * VIEW, v * VIEW
        anchor, lx, ly = LABELS[k]
        # Each place is a door to its own page. The plan is inlined, so SVG's own
        # <a> works and the group keeps its class for the scroll animation.
        # Arrival is a moment, not a place, and gets no link.
        g = ('<g class="pl pl-%s">'
             '<circle class="pl-halo" cx="%.1f" cy="%.1f" r="30"/>'
             '<circle class="pl-ring" cx="%.1f" cy="%.1f" r="13"/>'
             '<circle class="pl-dot" cx="%.1f" cy="%.1f" r="5.5"/>'
             '<text class="pl-name" x="%.1f" y="%.1f" text-anchor="%s">%s</text>'
             '</g>' % (k, x, y, x, y, x, y, x + lx, y + ly, anchor, name))
        if k in PAGE_FOR:
            g = '<a class="pl-link" href="/the-estate/%s/"><title>%s</title>%s</a>' % (
                PAGE_FOR[k], name, g)
        marks.append(g)

    svg = (
        '<svg class="plan" viewBox="%d %d %d %d" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-label="A contour plan of the estate showing six places '
        'and the walk between them across a wedding weekend">'
        '<g class="contours">%s</g>'
        '<g class="legs">%s</g>'
        '<g class="places">%s</g>'
        '</svg>'
    ) % (CROP + ("".join(body), "".join(legs), "".join(marks)))

    open(OUT, "w", encoding="utf-8").write(svg)
    write_icon(rings, scale)
    print("%s\n%d levels every %.0f m (%d index, %d intermediate paths), %d KB"
          % (OUT, len(levels), STEP, major, minor, len(svg) // 1024))

    # the walk, in metres, so the page can say something true about it
    wide = meta["metresWide"]
    tot = 0.0
    for a, b in zip(ROUTE, ROUTE[1:]):
        (x0, y0), (x1, y1) = at[a], at[b]
        d = math.hypot(x1 - x0, y1 - y0) / VIEW * wide
        tot += d
        print("   %-9s -> %-9s %4.0f m" % (a, b, d))
    print("   whole walk %.0f m (%.2f miles)" % (tot, tot / 1609.34))


if __name__ == "__main__":
    main()
