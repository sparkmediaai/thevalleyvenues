"""
The estate as a park map.

    python _tools/park_map.py            # writes map-lab/park-preview.svg

The direction is the craft of a theme-park map inside the estate's seven
colours: puffy two-tone trees with a highlight and a shadow, buildings drawn
with character, ribbon banners, a title cartouche, a gate on the way in. The
layout is Kobi's site plan, imported from estate_map so the two drawings can
never disagree about where anything is.

The buildings are traced from the photographs rather than invented, because a
park map's buildings are caricatures of real ones and a caricature has to be
recognisable:

  Magnolia House     Greek Revival, two storeys, four columns under a pediment,
                     the porch ceiling painted blue, glass conservatory east
  Overlook Village   house-shaped cabins on stilts, dark metal roofs, and each
                     gable end painted its own colour -- which they really are
  Davis Hall         the long white hall under a dark metal roof
  The Lookout Deck   grey boards, black cattle-panel rail, a steel pergola
                     strung with lights
  The Valley         white chairs either side of a grass aisle, a white arbour
  Lost in the Woods  a timber cabin under a long black shed roof on steel posts

Every shade and highlight is one of the seven colours at an opacity, so the
drawing never leaves the palette. Nothing here animates; the markup carries the
hooks (tree delays, building delays, drawable drive paths, terrace levels) and
the page decides what to do with them.
"""
import math
import os
import random

import estate_map as em
from estate_map import IVORY, CREAM, OLIVE, CLAY, BLUE, SAGE, DEEP

W, H = 2000, 800
WHITE = "#FFFFFF"
SERIF = "'Cormorant Garamond',Georgia,'Times New Roman',serif"
SANS = "'Libre Franklin',system-ui,sans-serif"

# Where each drawing stands (its ground point) and how large it is drawn, and
# where its banner flies. Anchors follow estate_map; a park map exaggerates
# buildings, so they are scaled up and nudged onto clear ground.
STAND = {
    "village":  dict(x=1240, y=148, s=.70, bx=1240, by=198),
    "magnolia": dict(x=652,  y=408, s=.70, bx=652,  by=250),
    "lodge":    dict(x=1386, y=402, s=.52, bx=1444, by=452),
    "hall":     dict(x=1570, y=352, s=.68, bx=1560, by=232),
    "deck":     dict(x=1716, y=410, s=.66, bx=1806, by=496),
    "valley":   dict(x=1524, y=596, s=.74, bx=1524, by=690),
    "woods":    dict(x=252,  y=716, s=.74, bx=252,  by=756),
}
ORDER = ["magnolia", "valley", "deck", "hall", "lodge", "village", "woods"]


def el(tag, **a):
    """One SVG element. Trailing underscores drop, underscores become hyphens."""
    parts = []
    for k, v in a.items():
        if v is None:
            continue
        k = k.rstrip("_").replace("_", "-")
        if isinstance(v, float):
            v = ("%.2f" % v).rstrip("0").rstrip(".")
        parts.append('%s="%s"' % (k, v))
    return "<%s %s/>" % (tag, " ".join(parts))


def poly(pts, **a):
    return el("polygon", points=" ".join("%.1f,%.1f" % p for p in pts), **a)


OUT = dict(stroke=DEEP, stroke_width=2.2, stroke_linejoin="round", stroke_linecap="round")


def sh(**a):
    """Outline style merged with overrides."""
    d = dict(OUT)
    d.update(a)
    return d


# ================================================================== the trees
def tree_defs():
    """Four trees, each drawn once. The outline trick: the canopy is painted
    twice, first fat-stroked and then unstroked on top, which leaves a single
    outline around the whole cluster instead of one per circle -- the soft
    ink edge every park map has."""
    out = []

    def broadleaf(sid, blobs, trunk_h, vb):
        clip = "clip-" + sid
        c = []
        c.append('<clipPath id="%s">%s</clipPath>' % (
            clip, "".join(el("circle", cx=x, cy=y, r=r) for x, y, r in blobs)))
        c.append('<symbol id="%s" viewBox="%s" overflow="visible">' % (sid, vb))
        c.append(el("ellipse", cx=5, cy=0, rx=18, ry=4.5, fill=DEEP, opacity=.16))
        c.append(el("rect", x=-3.2, y=-trunk_h, width=6.4, height=trunk_h, rx=2,
                    fill=CLAY, stroke=DEEP, stroke_width=1.4))
        for x, y, r in blobs:
            c.append(el("circle", cx=x, cy=y, r=r, fill=DEEP, stroke=DEEP, stroke_width=3.4))
        for x, y, r in blobs:
            c.append(el("circle", cx=x, cy=y, r=r, fill="currentColor"))
        # shade on the side away from the light, kept inside the canopy
        c.append('<g clip-path="url(#%s)">%s</g>' % (clip, el(
            "circle", cx=blobs[0][0] + 12, cy=blobs[0][1] + 12, r=blobs[0][2] + 8,
            fill=DEEP, opacity=.17)))
        hx, hy, hr = blobs[-1]
        c.append(el("circle", cx=hx - hr * .38, cy=hy - hr * .36, r=hr * .42, fill=CREAM, opacity=.55))
        c.append(el("circle", cx=blobs[0][0] - 9, cy=blobs[0][1] - 2, r=3, fill=CREAM, opacity=.45))
        c.append("</symbol>")
        return "".join(c)

    def fir(sid, tiers, vb):
        c = ['<symbol id="%s" viewBox="%s" overflow="visible">' % (sid, vb)]
        c.append(el("ellipse", cx=4, cy=0, rx=13, ry=3.8, fill=DEEP, opacity=.16))
        c.append(el("rect", x=-2.6, y=-8, width=5.2, height=8, rx=1.5, fill=CLAY,
                    stroke=DEEP, stroke_width=1.3))
        paths = []
        for top, half, base in tiers:
            paths.append("M 0 %.1f C %.1f %.1f %.1f %.1f %.1f %.1f "
                         "Q 0 %.1f %.1f %.1f C %.1f %.1f %.1f %.1f 0 %.1f Z" % (
                             top, half * .35, top + 4, half * .9, base - 6, half, base,
                             base + 5, -half, base, -half * .9, base - 6, -half * .35, top + 4, top))
        d = " ".join(paths)
        c.append('<path d="%s" fill="%s" stroke="%s" stroke-width="3.4" stroke-linejoin="round"/>' % (d, DEEP, DEEP))
        c.append('<path d="%s" fill="currentColor"/>' % d)
        for top, half, base in tiers:
            c.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                     'stroke-width="2.4" stroke-linecap="round" opacity=".5"/>' % (
                         -half * .18, top + 7, -half * .52, base - 8, -half * .7, base - 2, CREAM))
            c.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f L 0 %.1f Z" fill="%s" opacity=".14"/>' % (
                half * .08, top + 5, half * .7, base - 6, half * .95, base + 1, base + 3, DEEP))
        c.append("</symbol>")
        return "".join(c)

    out.append(broadleaf("tb1", [(0, -30, 15), (-11, -21, 11), (11, -22, 11.5), (-2, -41, 10.5)], 14,
                         "-24 -54 48 58"))
    out.append(broadleaf("tb2", [(0, -26, 13), (-13, -20, 9.5), (12, -18, 10), (4, -36, 9)], 11,
                         "-24 -48 48 52"))
    out.append(fir("tf1", [(-58, 9, -34), (-44, 13, -20), (-30, 17, -7)], "-20 -60 40 64"))
    out.append(fir("tf2", [(-46, 8, -26), (-34, 12, -14), (-22, 15, -5)], "-18 -48 36 52"))
    return "".join(out)


TREE_BOX = {"tb1": (-24, -54, 48, 58), "tb2": (-24, -48, 48, 52),
            "tf1": (-20, -60, 40, 64), "tf2": (-18, -48, 36, 52)}


def use_tree(kind, x, y, s, colour, delay):
    bx, by, bw, bh = TREE_BOX[kind]
    return ('<use class="t" href="#%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
            'style="color:%s;--d:%.2fs"/>' % (
                kind, x + bx * s, y + by * s, bw * s, bh * s, colour, delay))


# ============================================================== the buildings
def magnolia():
    b = []
    b.append(el("ellipse", cx=8, cy=4, rx=190, ry=22, fill=DEEP, opacity=.12))
    # the magnolias the house is named for, flanking it
    for tx in (-206, 214):
        b.append(el("rect", x=tx - 4, y=-30, width=8, height=30, rx=2, fill=CLAY, **sh(stroke_width=1.6)))
        for cx, cy, r in ((0, -46, 22), (-15, -36, 15), (15, -37, 16), (0, -62, 14)):
            b.append(el("circle", cx=tx + cx, cy=cy, r=r, fill=DEEP, stroke=DEEP, stroke_width=3.6))
        for cx, cy, r in ((0, -46, 22), (-15, -36, 15), (15, -37, 16), (0, -62, 14)):
            b.append(el("circle", cx=tx + cx, cy=cy, r=r, fill=OLIVE))
        for cx, cy in ((-10, -54), (8, -60), (14, -42), (-16, -38), (2, -34), (-4, -66), (18, -52)):
            b.append(el("circle", cx=tx + cx, cy=cy, r=4.2, fill=WHITE, stroke=DEEP, stroke_width=.8))
            b.append(el("circle", cx=tx + cx, cy=cy, r=1.4, fill=CLAY))
    # west wing
    b.append(el("rect", x=-176, y=-74, width=92, height=74, fill=WHITE, **sh()))
    b.append(poly([(-184, -74), (-168, -98), (-92, -98), (-80, -74)], fill=DEEP, **sh()))
    for wx in (-160, -124):
        b.append(el("rect", x=wx, y=-56, width=20, height=26, fill=BLUE, fill_opacity=.5, **sh(stroke_width=1.6)))
        b.append(el("line", x1=wx + 10, y1=-56, x2=wx + 10, y2=-30, stroke=WHITE, stroke_width=1.6))
    # conservatory, glass on three sides
    b.append(el("rect", x=86, y=-78, width=82, height=78, fill=BLUE, fill_opacity=.34, **sh()))
    b.append(poly([(80, -78), (127, -112), (174, -78)], fill=BLUE, fill_opacity=.26, **sh()))
    for gx in range(98, 168, 14):
        b.append(el("line", x1=gx, y1=-78, x2=gx, y2=0, stroke=WHITE, stroke_width=2))
    b.append(el("line", x1=86, y1=-40, x2=168, y2=-40, stroke=WHITE, stroke_width=2))
    b.append(el("path", d="M 104 -90 L 127 -106 L 150 -90", fill="none", stroke=WHITE, stroke_width=1.8))
    b.append(el("rect", x=96, y=-72, width=16, height=66, fill=CREAM, opacity=.35))
    # the house
    b.append(el("rect", x=-88, y=-128, width=176, height=128, fill=WHITE, **sh()))
    b.append(poly([(-104, -128), (-72, -160), (72, -160), (104, -128)], fill=DEEP, **sh()))
    b.append(el("line", x1=-66, y1=-154, x2=40, y2=-154, stroke=CREAM, stroke_width=2.4, opacity=.35))
    # pediment over the portico
    b.append(poly([(-84, -128), (0, -180), (84, -128)], fill=WHITE, **sh()))
    b.append(poly([(-66, -134), (0, -170), (66, -134)], fill=SAGE, opacity=.28))
    b.append(el("circle", cx=0, cy=-146, r=8, fill=BLUE, fill_opacity=.55, **sh(stroke_width=1.6)))
    b.append(el("rect", x=-86, y=-132, width=172, height=8, fill=WHITE, **sh(stroke_width=1.8)))
    # the porch ceiling, painted blue the way Southern porches are
    b.append(el("rect", x=-78, y=-124, width=156, height=9, fill=BLUE, opacity=.6))
    # windows, three up and two down, and the door
    for wx in (-40, 0, 40):
        b.append(el("rect", x=wx - 10, y=-108, width=20, height=28, fill=BLUE, fill_opacity=.45, **sh(stroke_width=1.6)))
        b.append(el("path", d="M %d -108 V -80 M %d -94 H %d" % (wx, wx - 10, wx + 10),
                    stroke=WHITE, stroke_width=1.6))
    for wx in (-40, 40):
        b.append(el("rect", x=wx - 10, y=-58, width=20, height=30, fill=BLUE, fill_opacity=.45, **sh(stroke_width=1.6)))
        b.append(el("path", d="M %d -58 V -28 M %d -43 H %d" % (wx, wx - 10, wx + 10),
                    stroke=WHITE, stroke_width=1.6))
    b.append(el("path", d="M -13 -8 V -46 A 13 13 0 0 1 13 -46 V -8 Z", fill=CLAY, **sh(stroke_width=1.8)))
    b.append(el("path", d="M -13 -8 V -46 A 13 13 0 0 1 13 -46 V -8 Z", fill=DEEP, opacity=.28))
    b.append(el("line", x1=0, y1=-52, x2=0, y2=-8, stroke=DEEP, stroke_width=1.4))
    # four columns, the full two storeys
    for cx in (-62, -20, 20, 62):
        b.append(el("rect", x=cx - 7, y=-122, width=14, height=112, fill=WHITE, **sh(stroke_width=1.8)))
        b.append(el("rect", x=cx + 1.5, y=-120, width=4, height=108, fill=SAGE, opacity=.55))
        b.append(el("rect", x=cx - 10, y=-126, width=20, height=6, fill=WHITE, **sh(stroke_width=1.5)))
        b.append(el("rect", x=cx - 10, y=-12, width=20, height=6, fill=WHITE, **sh(stroke_width=1.5)))
    # steps and the hydrangea hedges either side
    for i, (w, y) in enumerate(((70, -6), (86, 0), (102, 6))):
        b.append(el("rect", x=-w / 2.0, y=y, width=w, height=6, fill=CREAM, **sh(stroke_width=1.4)))
    for side in (-1, 1):
        for k in range(4):
            hx = side * (40 + k * 16)
            b.append(el("circle", cx=hx, cy=-4, r=10, fill=DEEP, stroke=DEEP, stroke_width=3))
        for k in range(4):
            hx = side * (40 + k * 16)
            b.append(el("circle", cx=hx, cy=-4, r=10, fill=OLIVE))
            b.append(el("circle", cx=hx - 3, cy=-8, r=3.4, fill=WHITE, opacity=.9))
            b.append(el("circle", cx=hx + 4, cy=-2, r=2.4, fill=CREAM))
    return "".join(b)


def village():
    """House-shaped cabins stepping up the hill on stilts. Each gable end is
    painted its own colour, which is true of the real cabins and is the most
    park-map thing on the whole estate."""
    b = []
    b.append(el("path", d="M -214 40 C -150 6 -50 -14 60 -40 C 130 -56 190 -62 232 -60 "
                          "L 232 40 Z", fill=OLIVE, opacity=.42))
    b.append(el("path", d="M -206 32 C -140 2 -44 -18 64 -42 C 132 -57 190 -62 228 -60",
                fill="none", stroke=CREAM, stroke_width=4, stroke_linecap="round", opacity=.55))
    faces = [CLAY, OLIVE, BLUE, SAGE]
    for i in range(4):
        gx = -150 + i * 102
        gy = 18 - i * 22
        body_bottom = gy - 22
        # stilts
        for sx in (-18, 0, 18):
            b.append(el("line", x1=gx + sx, y1=body_bottom, x2=gx + sx, y2=gy + 4, stroke=DEEP, stroke_width=3.6))
        # side wall in dark metal, then the painted gable end
        b.append(poly([(gx - 30, body_bottom), (gx - 30, body_bottom - 44), (gx, body_bottom - 82),
                       (gx + 30, body_bottom - 44), (gx + 30, body_bottom)], fill=faces[i], **sh()))
        b.append(poly([(gx + 8, body_bottom), (gx + 8, body_bottom - 70), (gx + 30, body_bottom - 44),
                       (gx + 30, body_bottom)], fill=DEEP, opacity=.16))
        # the roof, a heavy dark edge over the gable
        b.append(el("path", d="M %d %d L %d %d L %d %d" % (gx - 36, body_bottom - 38, gx, body_bottom - 88,
                                                          gx + 36, body_bottom - 38),
                    fill="none", stroke=DEEP, stroke_width=8, stroke_linecap="round", stroke_linejoin="round"))
        b.append(el("path", d="M %d %d L %d %d" % (gx - 30, body_bottom - 44, gx - 4, body_bottom - 80),
                    fill="none", stroke=CREAM, stroke_width=1.6, opacity=.5))
        # the big window, lit, and the balcony rail
        b.append(el("rect", x=gx - 15, y=body_bottom - 50, width=30, height=34, rx=2,
                    fill=CREAM, **sh(stroke_width=1.8)))
        b.append(el("rect", x=gx - 11, y=body_bottom - 46, width=9, height=26, fill=WHITE, opacity=.7))
        b.append(el("line", x1=gx, y1=body_bottom - 50, x2=gx, y2=body_bottom - 16, stroke=DEEP, stroke_width=1.4))
        b.append(el("path", d="M %d %d H %d M %d %d V %d M %d %d V %d M %d %d V %d" % (
            gx - 34, body_bottom - 8, gx + 34, gx - 22, body_bottom - 8, body_bottom,
            gx, body_bottom - 8, body_bottom, gx + 22, body_bottom - 8, body_bottom),
            stroke=DEEP, stroke_width=2.2, fill="none"))
    return "".join(b)


def hall():
    b = []
    b.append(el("ellipse", cx=0, cy=4, rx=150, ry=16, fill=DEEP, opacity=.12))
    b.append(el("rect", x=-134, y=-66, width=228, height=66, fill=WHITE, **sh()))
    b.append(poly([(-146, -66), (-112, -104), (72, -104), (106, -66)], fill=DEEP, **sh()))
    b.append(el("line", x1=-104, y1=-98, x2=40, y2=-98, stroke=CREAM, stroke_width=2.6, opacity=.3))
    # the gable end facing east
    b.append(poly([(94, -66), (94, -4), (106, -66)], fill=SAGE, opacity=.3))
    # tall dark windows, and the double doors
    for wx in (-116, -92, -68, 24, 48, 72):
        b.append(el("rect", x=wx - 7, y=-54, width=14, height=36, rx=1.5, fill=DEEP, **sh(stroke_width=1.2)))
        b.append(el("rect", x=wx - 5, y=-52, width=4, height=14, fill=CREAM, opacity=.35))
    b.append(el("rect", x=-36, y=-58, width=48, height=58, fill=WHITE, **sh(stroke_width=2)))
    b.append(el("path", d="M -12 -58 V 0", stroke=DEEP, stroke_width=1.8, fill="none"))
    for dx in (-24, 0):
        b.append(el("rect", x=dx - 6, y=-50, width=12, height=20, rx=1, fill=CREAM, **sh(stroke_width=1)))
    for dx in (-17, 5):
        b.append(el("circle", cx=dx, cy=-26, r=1.8, fill=DEEP))
    # lights along the eave
    for k in range(-126, 92, 12):
        b.append(el("circle", cx=k, cy=-62 + (3 if k % 24 else 0), r=2.3, fill=CREAM, stroke=DEEP, stroke_width=.6))
    return "".join(b)


def deck():
    b = []
    b.append(el("ellipse", cx=40, cy=40, rx=130, ry=14, fill=DEEP, opacity=.12))
    b.append(poly([(-150, -2), (120, -2), (150, 34), (-120, 34)], fill=SAGE, **sh()))
    for k in range(-138, 140, 13):
        b.append(el("line", x1=k, y1=-2, x2=k + 30, y2=34, stroke=DEEP, stroke_width=1, opacity=.18))
    # the steel pergola
    for px in (-10, 80):
        b.append(el("rect", x=px - 3, y=-92, width=6, height=92, fill=DEEP))
    b.append(el("rect", x=-22, y=-98, width=116, height=9, fill=DEEP))
    for k in range(-14, 90, 12):
        b.append(el("line", x1=k, y1=-98, x2=k + 4, y2=-89, stroke=CREAM, stroke_width=1, opacity=.4))
    b.append(el("path", d="M -6 -86 Q 35 -66 76 -86", fill="none", stroke=DEEP, stroke_width=1))
    for t in (.1, .25, .4, .55, .7, .85):
        x = -6 + 82 * t
        y = -86 + 20 * (4 * t * (1 - t))
        b.append(el("circle", cx=x, cy=y + 2, r=2.6, fill=CREAM, stroke=DEEP, stroke_width=.6))
    # cocktail tables
    for tx, ty in ((-80, 16), (-40, 22), (20, 14), (110, 20)):
        b.append(el("line", x1=tx, y1=ty - 18, x2=tx, y2=ty, stroke=DEEP, stroke_width=2))
        b.append(el("ellipse", cx=tx, cy=ty - 19, rx=9, ry=3, fill=WHITE, **sh(stroke_width=1.4)))
    # the black cattle-panel rail on the two open sides
    b.append(el("path", d="M -120 34 L 150 34 L 120 -2", fill="none", stroke=DEEP, stroke_width=3.2,
                stroke_linejoin="round"))
    b.append(el("path", d="M -120 18 L 150 18", fill="none", stroke=DEEP, stroke_width=2))
    for k in range(-120, 152, 9):
        b.append(el("line", x1=k, y1=18, x2=k, y2=34, stroke=DEEP, stroke_width=1))
    for k in range(-120, 152, 45):
        b.append(el("line", x1=k, y1=8, x2=k, y2=34, stroke=DEEP, stroke_width=3))
    return "".join(b)


def valley():
    b = []
    b.append(el("ellipse", cx=0, cy=10, rx=150, ry=70, fill=OLIVE, opacity=.4))
    b.append(el("ellipse", cx=-14, cy=0, rx=110, ry=46, fill=CREAM, opacity=.18))
    b.append(el("path", d="M -12 -38 L 12 -38 L 26 64 L -26 64 Z", fill=CREAM, opacity=.7))
    for side in (-1, 1):
        for r in range(6):
            for c in range(6):
                cx = side * (30 + c * 14 + r * 2)
                cy = -26 + r * 15
                b.append(el("rect", x=cx - 4.5, y=cy - 5, width=9, height=10, rx=2,
                            fill=WHITE, **sh(stroke_width=1.1)))
                b.append(el("rect", x=cx - 4.5, y=cy - 5, width=9, height=3, rx=1.5, fill=SAGE, opacity=.5))
    # the white arbour and its flowers
    for px in (-30, 22):
        b.append(el("rect", x=px, y=-104, width=9, height=66, fill=WHITE, **sh(stroke_width=1.8)))
        b.append(el("rect", x=px + 5, y=-102, width=3, height=62, fill=SAGE, opacity=.6))
    b.append(el("rect", x=-42, y=-114, width=84, height=12, rx=2, fill=WHITE, **sh(stroke_width=1.8)))
    for fx, fy, r, c in ((-40, -114, 9, OLIVE), (-30, -120, 8, WHITE), (-44, -104, 7, CREAM),
                         (-34, -96, 6, OLIVE), (-38, -86, 6, WHITE), (-24, -118, 6, CLAY),
                         (38, -116, 8, OLIVE), (30, -121, 7, WHITE), (42, -106, 6, CREAM),
                         (26, -114, 5, CLAY)):
        b.append(el("circle", cx=fx, cy=fy, r=r, fill=c, **sh(stroke_width=1.2)))
    return "".join(b)


def woods():
    b = []
    b.append(el("ellipse", cx=30, cy=6, rx=150, ry=22, fill=CREAM, opacity=.6))
    b.append(el("ellipse", cx=30, cy=6, rx=150, ry=22, fill=OLIVE, opacity=.18))
    # the cabin, horizontal timber
    b.append(el("rect", x=-70, y=-66, width=112, height=66, fill=CLAY, **sh()))
    for k in range(-60, 0, 8):
        b.append(el("line", x1=-70, y1=k, x2=42, y2=k, stroke=DEEP, stroke_width=1, opacity=.2))
    b.append(el("rect", x=-70, y=-66, width=18, height=66, fill=DEEP, opacity=.12))
    # the long black shed roof, out over the porch on steel posts
    b.append(poly([(-84, -66), (-84, -78), (130, -90), (130, -78)], fill=DEEP, **sh()))
    for px in (86, 124):
        b.append(el("line", x1=px, y1=-82, x2=px, y2=0, stroke=DEEP, stroke_width=4))
    b.append(el("rect", x=40, y=-6, width=92, height=8, fill=SAGE, **sh(stroke_width=1.6)))
    # lit glass door and window
    b.append(el("rect", x=-6, y=-54, width=32, height=54, fill=CREAM, **sh(stroke_width=1.8)))
    b.append(el("rect", x=-2, y=-50, width=10, height=46, fill=WHITE, opacity=.8))
    b.append(el("line", x1=10, y1=-54, x2=10, y2=0, stroke=DEEP, stroke_width=1.4))
    b.append(el("rect", x=-58, y=-50, width=38, height=24, fill=CREAM, **sh(stroke_width=1.8)))
    # lights strung between the posts
    b.append(el("path", d="M 42 -70 Q 64 -50 86 -72 Q 105 -54 124 -74", fill="none", stroke=DEEP, stroke_width=1))
    for x, y in ((52, -62), (64, -58), (76, -62), (96, -64), (105, -61), (114, -65)):
        b.append(el("circle", cx=x, cy=y, r=2.6, fill=CREAM, stroke=DEEP, stroke_width=.6))
    # the fire pit
    b.append(el("ellipse", cx=176, cy=4, rx=20, ry=7, fill=SAGE, **sh(stroke_width=1.8)))
    b.append(el("path", d="M 166 0 Q 170 -24 176 -30 Q 181 -20 186 -14 Q 190 -6 184 0 Z",
                fill=CLAY, **sh(stroke_width=1.4)))
    b.append(el("path", d="M 172 -1 Q 175 -14 178 -18 Q 182 -10 181 -1 Z", fill=CREAM))
    b.append(el("path", d="M 178 -34 q -8 -10 0 -20 q 8 -10 0 -20", class_="smoke", fill="none", stroke=SAGE,
                stroke_width=3, stroke_linecap="round", opacity=.7))
    return "".join(b)

def lodge():
    """The lodge on the drive below the village: one gable, a deep porch, and
       the two rooms that matter on the day lit behind it."""
    b = []
    b.append(el("ellipse", cx=8, cy=6, rx=104, ry=16, fill=DEEP, opacity=.12))
    # the body, white board under a dark metal roof
    b.append(el("rect", x=-66, y=-62, width=132, height=62, fill=WHITE, **sh()))
    b.append(poly([(-80, -62), (0, -108), (80, -62)], fill=DEEP, **sh()))
    b.append(el("line", x1=-66, y1=-70, x2=66, y2=-70, stroke=CREAM, stroke_width=2.2, opacity=.25))
    # the porch, out over the drive on two posts
    b.append(poly([(-92, -40), (-66, -52), (-66, -30), (-92, -22)], fill=SAGE, opacity=.45))
    for px in (-88, -70):
        b.append(el("line", x1=px, y1=-26, x2=px, y2=0, stroke=DEEP, stroke_width=3.4))
    b.append(el("rect", x=-96, y=-4, width=36, height=6, fill=SAGE, **sh(stroke_width=1.6)))
    # the door, and the lit windows of the two suites
    b.append(el("rect", x=-14, y=-44, width=28, height=44, fill=CLAY, **sh(stroke_width=1.8)))
    b.append(el("circle", cx=8, cy=-22, r=1.8, fill=CREAM))
    for wx in (-46, 40):
        b.append(el("rect", x=wx - 12, y=-46, width=24, height=26, rx=1.5, fill=CREAM, **sh(stroke_width=1.6)))
        b.append(el("line", x1=wx, y1=-46, x2=wx, y2=-20, stroke=DEEP, stroke_width=1.2))
    b.append(el("rect", x=-13, y=-92, width=26, height=18, rx=1.5, fill=CREAM, **sh(stroke_width=1.5)))
    # a hedge along the front
    for k in range(-58, 64, 22):
        b.append(el("circle", cx=k, cy=0, r=9, fill=OLIVE, **sh(stroke_width=1.4)))
        b.append(el("circle", cx=k - 3, cy=-3, r=2.6, fill=WHITE, opacity=.8))
    return "".join(b)


DRAW = dict(magnolia=magnolia, village=village, hall=hall, deck=deck, valley=valley,
            woods=woods, lodge=lodge)


# ================================================================ the banners
def banner(x, y, text, delay):
    w = len(text) * 15.4 + 52
    L, R = x - w / 2.0, x + w / 2.0
    g = ['<g class="ban" style="--bd:%.2fs">' % delay]
    for sgn, edge in ((-1, L), (1, R)):
        tail_in, tail_out = edge + sgn * -2, edge + sgn * 30
        g.append(poly([(tail_in, y - 9), (tail_out, y - 9), (tail_out - sgn * 11, y + 4),
                       (tail_out, y + 17), (tail_in, y + 17)], fill=CLAY, **sh(stroke_width=1.6)))
        g.append(poly([(edge, y + 15), (edge + sgn * -1, y + 21), (edge + sgn * 12, y + 15)],
                      fill=DEEP, opacity=.55))
    g.append(el("rect", x=L, y=y - 17, width=w, height=34, rx=3, fill=CREAM, **sh(stroke_width=1.8)))
    g.append(el("line", x1=L + 7, y1=y - 11, x2=R - 7, y2=y - 11, stroke=CLAY, stroke_width=1, opacity=.6))
    g.append(el("line", x1=L + 7, y1=y + 11, x2=R - 7, y2=y + 11, stroke=CLAY, stroke_width=1, opacity=.6))
    g.append('<text class="ban-text" x="%.1f" y="%.1f" dy=".36em" text-anchor="middle" '
             'font-family="%s" font-size="21" font-weight="600" letter-spacing="1.6" '
             'fill="%s">%s</text>' % (x, y, SERIF, DEEP, text.upper()))
    g.append("</g>")
    return "".join(g)


# ============================================================== the furniture
def cartouche():
    x, y = 1752, 80
    g = ['<g class="cart">']
    g.append(el("rect", x=x - 196, y=y - 46, width=392, height=96, rx=10, fill=CREAM, **sh(stroke_width=2.2)))
    for cx in (x - 196, x + 196):
        g.append(el("circle", cx=cx, cy=y + 2, r=16, fill=CREAM, **sh(stroke_width=2.2)))
        g.append(el("circle", cx=cx, cy=y + 2, r=7, fill=CLAY, **sh(stroke_width=1.4)))
    g.append(el("rect", x=x - 180, y=y - 36, width=360, height=76, rx=6, fill="none",
                stroke=CLAY, stroke_width=1.2))
    g.append('<text x="%d" y="%d" text-anchor="middle" font-family="%s" font-size="36" '
             'font-style="italic" font-weight="500" fill="%s">The Valley Venues</text>' % (x, y + 6, SERIF, DEEP))
    g.append('<text x="%d" y="%d" text-anchor="middle" font-family="%s" font-size="11" font-weight="600" '
             'letter-spacing="2.2" fill="%s">AN ESTATE MAP &#183; WILDWOOD, GEORGIA</text>' % (x, y + 28, SANS, DEEP))
    g.append("</g>")
    # the compass
    cx, cy = 1930, 196
    g.append('<g class="cart compass">')
    g.append(el("circle", cx=cx, cy=cy, r=30, fill=CREAM, **sh(stroke_width=1.8)))
    g.append(el("circle", cx=cx, cy=cy, r=24, fill="none", stroke=CLAY, stroke_width=1))
    for ang, big in ((0, 1), (90, 1), (180, 1), (270, 1), (45, 0), (135, 0), (225, 0), (315, 0)):
        r = 25 if big else 15
        a = math.radians(ang - 90)
        tipx, tipy = cx + r * math.cos(a), cy + r * math.sin(a)
        lx, ly = cx + 5 * math.cos(a - math.pi / 2), cy + 5 * math.sin(a - math.pi / 2)
        rx_, ry_ = cx + 5 * math.cos(a + math.pi / 2), cy + 5 * math.sin(a + math.pi / 2)
        g.append(poly([(lx, ly), (tipx, tipy), (cx, cy)], fill=CLAY if ang == 0 else DEEP, opacity=1 if big else .55))
        g.append(poly([(rx_, ry_), (tipx, tipy), (cx, cy)], fill=CREAM if ang else CLAY,
                      stroke=DEEP, stroke_width=.8))
    g.append('<text x="%d" y="%d" text-anchor="middle" font-family="%s" font-size="14" font-weight="700" '
             'fill="%s">N</text>' % (cx, cy - 36, SERIF, DEEP))
    g.append("</g>")
    return "".join(g)


def gate():
    """Two stone piers where the drive leaves Pope Creek Road. The site says
    the gate closes behind you, so the map should show one."""
    g = ['<g class="gate">']
    for px in (996, 1078):
        g.append(el("rect", x=px - 11, y=500, width=22, height=46, fill=CREAM, **sh(stroke_width=2)))
        g.append(el("rect", x=px - 15, y=492, width=30, height=10, rx=2, fill=CLAY, **sh(stroke_width=1.8)))
        g.append(el("circle", cx=px, cy=486, r=6, fill=CREAM, **sh(stroke_width=1.6)))
        for k in (512, 524, 536):
            g.append(el("line", x1=px - 11, y1=k, x2=px + 11, y2=k, stroke=DEEP, stroke_width=.8, opacity=.35))
    g.append('<path d="M 1007 512 Q 1037 492 1067 512" fill="none" stroke="%s" stroke-width="3"/>' % DEEP)
    g.append("</g>")
    return "".join(g)


def cloud(x, y, s):
    blobs = [(0, 0, 22), (-24, 6, 15), (24, 6, 17), (-8, -12, 16), (12, -10, 14)]
    c = ['<g class="cloud" transform="translate(%d %d) scale(%.2f)">' % (x, y, s)]
    for bx, by, r in blobs:
        c.append(el("circle", cx=bx, cy=by, r=r, fill=DEEP, stroke=DEEP, stroke_width=3, opacity=.9))
    for bx, by, r in blobs:
        c.append(el("circle", cx=bx, cy=by, r=r, fill=CREAM))
    c.append(el("path", d="M -36 14 Q 0 26 40 14 L 40 22 L -36 22 Z", fill=SAGE, opacity=.5))
    c.append(el("rect", x=-40, y=18, width=84, height=10, fill=CREAM))
    c.append("</g>")
    return "".join(c)


def mountains():
    m = ['<g class="range">']
    m.append(el("path", d="M 1640 800 C 1700 720 1740 660 1790 612 C 1812 590 1830 596 1850 618 "
                          "C 1880 650 1900 632 1922 604 C 1944 578 1968 584 2000 630 L 2000 800 Z",
                fill=OLIVE, **sh(stroke_width=2.4)))
    m.append(el("path", d="M 1790 612 C 1812 590 1830 596 1850 618 C 1830 640 1810 680 1780 720 "
                          "C 1770 690 1780 640 1790 612 Z", fill=CREAM, opacity=.35))
    m.append(el("path", d="M 1922 604 C 1944 578 1968 584 2000 630 L 2000 700 C 1968 670 1950 640 1922 604 Z",
                fill=DEEP, opacity=.16))
    m.append("</g>")
    return "".join(m)


# =============================================================== the fairy tale
# Rooftop pennants, in each drawing's own units: the pediment of Magnolia House,
# both ends of the hall, the ridge of every cabin, the pergola, the arbour.
FLAGS = {
    "magnolia": [(0, -180), (-130, -98), (127, -112)],
    "hall":     [(-112, -104), (72, -104)],
    "village":  [(-150, -92), (-48, -114), (54, -136), (156, -158)],
    "deck":     [(-22, -98), (94, -98)],
    "valley":   [(0, -114)],
    "woods":    [(130, -90)],
    "lodge":    [(-74, -96)],
}

STAR = "M 0 -10 Q 1.4 -1.4 10 0 Q 1.4 1.4 0 10 Q -1.4 1.4 -10 0 Q -1.4 -1.4 0 -10 Z"


def pennant(x, y, colour, delay):
    return ('<g class="flag"><line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>'
            '<circle cx="%d" cy="%d" r="3.6" fill="%s" stroke="%s" stroke-width="1.4"/>'
            '<path class="pennant" style="--fd:%.2fs" d="M %d %d L %d %d L %d %d L %d %d L %d %d Z" '
            'fill="%s" stroke="%s" stroke-width="1.8" stroke-linejoin="round"/></g>' % (
                x, y, x, y - 44, DEEP, x, y - 46, CREAM, DEEP, delay,
                x + 1, y - 43, x + 38, y - 38, x + 28, y - 33, x + 38, y - 28, x + 1, y - 25, colour, DEEP))


def star(x, y, s, fill, cls="tw", delay=0.0):
    # the position lives on the wrapper so a CSS transform on the star itself
    # can twinkle it without throwing it to the corner of the map
    return ('<g transform="translate(%.0f %.0f) scale(%.2f)"><path class="%s" style="--tw:%.2fs" d="%s" '
            'fill="%s" stroke="%s" stroke-width="1.4" stroke-linejoin="round"/></g>' % (
                x, y, s, cls, delay, STAR, fill, DEEP))


def bird(x, y, s):
    return ('<g class="bird" transform="translate(%d %d) scale(%.2f)">'
            '<path class="wing wb" d="M -2 -2 Q -16 -22 -30 -12 Q -16 -10 -4 2 Z" fill="%s" stroke="%s" stroke-width="2"/>'
            '<path d="M -22 2 Q -8 -10 12 -4 Q 22 -2 26 2 Q 14 6 0 8 Q -12 8 -22 2 Z" fill="%s" stroke="%s" stroke-width="2.2"/>'
            '<path d="M 26 1 L 34 3 L 26 5 Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
            '<circle cx="17" cy="0" r="1.8" fill="%s"/>'
            '<path d="M -8 2 Q 2 4 10 3" fill="none" stroke="%s" stroke-width="1.4" opacity=".6"/>'
            '<path class="wing wf" d="M 0 -2 Q 6 -28 -14 -30 Q -6 -14 -8 0 Z" fill="%s" stroke="%s" stroke-width="2"/>'
            '</g>' % (x, y, s, BLUE, DEEP, BLUE, DEEP, CLAY, DEEP, DEEP, CREAM, SAGE, DEEP))


def butterfly(x, y, colour):
    return ('<g class="bfly" transform="translate(%d %d)"><g class="bf">'
            '<path class="bw" d="M 0 0 Q -12 -14 -14 -4 Q -14 4 0 2 Q -10 10 -6 13 Q 0 10 0 2 Z" fill="%s" stroke="%s" stroke-width="1.3"/>'
            '<path class="bw bw2" d="M 0 0 Q 12 -14 14 -4 Q 14 4 0 2 Q 10 10 6 13 Q 0 10 0 2 Z" fill="%s" stroke="%s" stroke-width="1.3"/>'
            '<line x1="0" y1="-4" x2="0" y2="8" stroke="%s" stroke-width="2"/></g></g>' % (
                x, y, colour, DEEP, colour, DEEP, DEEP))


def fairy_layer(rng, avoid, segs):
    """Twinkles over the open ground, bluebirds, butterflies over the meadow."""
    g = ['<g class="fairy">']
    placed = []
    for _ in range(3000):
        if len(placed) >= 30:
            break
        x, y = rng.uniform(60, W - 60), rng.uniform(40, H - 60)
        if any(em.inside(q, x, y) for q in em.WOODS):
            continue
        if any(math.hypot(x - ax, y - ay) < r * .8 for ax, ay, r in avoid):
            continue
        if any(math.hypot(x - px_, y - py_) < 90 for px_, py_ in placed):
            continue
        placed.append((x, y))
    for n, (x, y) in enumerate(placed):
        g.append(star(x, y, rng.uniform(.55, 1.05), rng.choice([WHITE, WHITE, CREAM, SAGE]), "tw",
                      rng.uniform(0, 3)))
    g.append('<g transform="translate(300 118)"><g class="birds">%s%s%s</g></g>' % (
        bird(0, 0, .9), bird(-60, 26, .72), bird(-104, -10, .6)))
    for x, y, c in ((760, 300, WHITE), (880, 360, CLAY), (1180, 520, BLUE), (560, 250, SAGE)):
        g.append(butterfly(x, y, c))
    g.append("</g>")
    return "".join(g)


# ================================================================== the terrain
def fit_affine(pairs):
    """Least squares for x' = a u + b v + c, y' = d u + e v + f. Pure Python,
    because this machine has no numpy and six unknowns do not need one."""
    def solve3(A, bvec):
        M = [row[:] + [bvec[i]] for i, row in enumerate(A)]
        for col in range(3):
            piv = max(range(col, 3), key=lambda r: abs(M[r][col]))
            M[col], M[piv] = M[piv], M[col]
            for r in range(3):
                if r != col:
                    f = M[r][col] / M[col][col]
                    for c in range(col, 4):
                        M[r][c] -= f * M[col][c]
        return [M[i][3] / M[i][i] for i in range(3)]
    ata = [[0.0] * 3 for _ in range(3)]
    atx = [0.0] * 3
    aty = [0.0] * 3
    for (u, v), (x, y) in pairs:
        row = (u, v, 1.0)
        for i in range(3):
            for j in range(3):
                ata[i][j] += row[i] * row[j]
            atx[i] += row[i] * x
            aty[i] += row[i] * y
    return solve3(ata, atx), solve3(ata, aty)


# Where the terrain model puts each place on the survey grid, against where the
# site plan puts it. The deck is left out on purpose: the model has it west of
# Magnolia House, where two of the client's own documents say it is not.
CONTROL = [((.727, .561), (1370, 560)), ((.597, .499), (1500, 352)),
           ((.506, .415), (1230, 112)), ((.398, .547), (650, 372)),
           ((.443, .596), (1046, 700))]


def terrain_levels(n_levels=9, step=10):
    """Sample the LiDAR heightmap into the site plan's frame and return filled
    terrace loops per level: [(level, [points...]), ...]."""
    from PIL import Image
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hm = Image.open(os.path.join(root, "terrain", "terrain.png")).convert("L")
    N = hm.size[0]
    px = hm.load()
    fx, fy = fit_affine(CONTROL)
    # invert the 2x2
    a, b, c = fx
    d, e, f = fy
    det = a * e - b * d
    ia, ib, id_, ie = e / det, -b / det, -d / det, a / det

    def height(x, y):
        u = ia * (x - c) + ib * (y - f)
        v = id_ * (x - c) + ie * (y - f)
        gx = max(0.0, min(N - 1.001, u * (N - 1)))
        gy = max(0.0, min(N - 1.001, v * (N - 1)))
        x0, y0 = int(gx), int(gy)
        tx, ty = gx - x0, gy - y0
        h00, h10 = px[x0, y0], px[x0 + 1, y0]
        h01, h11 = px[x0, y0 + 1], px[x0 + 1, y0 + 1]
        return (h00 * (1 - tx) + h10 * tx) * (1 - ty) + (h01 * (1 - tx) + h11 * tx) * ty

    cols, rows = W // step + 1, H // step + 1
    grid = [[height(i * step, j * step) for i in range(cols)] for j in range(rows)]
    # soften it: a park map's hills are pillows, not a survey
    for _ in range(4):
        g2 = [row[:] for row in grid]
        for j in range(rows):
            for i in range(cols):
                acc, n = 0.0, 0
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        jj, ii = j + dj, i + di
                        if 0 <= jj < rows and 0 <= ii < cols:
                            acc += grid[jj][ii]
                            n += 1
                g2[j][i] = acc / n
        grid = g2
    lo = min(min(r) for r in grid)
    hi = max(max(r) for r in grid)
    # pad so every contour closes
    P = [[lo - 50] * (cols + 2)] + [[lo - 50] + r + [lo - 50] for r in grid] + [[lo - 50] * (cols + 2)]
    out = []
    for k in range(1, n_levels + 1):
        L = lo + (hi - lo) * k / (n_levels + 1.0)
        segs = marching(P, L, step)
        for loop in join_loops(segs):
            if len(loop) < 8:
                continue
            cx = sum(p[0] for p in loop) / len(loop)
            cy = sum(p[1] for p in loop) / len(loop)
            if abs(area(loop)) < step * step * 6:
                continue
            out.append((k, chaikin(loop, 2)))
    return out, (fx, fy), residuals((fx, fy))


def residuals(fit):
    fx, fy = fit
    r = []
    for (u, v), (x, y) in CONTROL:
        px_ = fx[0] * u + fx[1] * v + fx[2]
        py_ = fy[0] * u + fy[1] * v + fy[2]
        r.append(math.hypot(px_ - x, py_ - y))
    return r


def marching(P, L, step):
    rows, cols = len(P), len(P[0])
    segs = []

    def lerp(a, b, va, vb):
        t = (L - va) / (vb - va) if vb != va else .5
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    for j in range(rows - 1):
        for i in range(cols - 1):
            v0, v1, v2, v3 = P[j][i], P[j][i + 1], P[j + 1][i + 1], P[j + 1][i]
            idx = (v0 > L) | (v1 > L) << 1 | (v2 > L) << 2 | (v3 > L) << 3
            if idx in (0, 15):
                continue
            x, y = (i - 1) * step, (j - 1) * step
            p0, p1, p2, p3 = (x, y), (x + step, y), (x + step, y + step), (x, y + step)
            top = lerp(p0, p1, v0, v1)
            right = lerp(p1, p2, v1, v2)
            bottom = lerp(p3, p2, v3, v2)
            left = lerp(p0, p3, v0, v3)
            table = {1: [(left, top)], 2: [(top, right)], 3: [(left, right)], 4: [(right, bottom)],
                     5: [(left, top), (right, bottom)], 6: [(top, bottom)], 7: [(left, bottom)],
                     8: [(bottom, left)], 9: [(bottom, top)], 10: [(top, right), (bottom, left)],
                     11: [(bottom, right)], 12: [(right, left)], 13: [(right, top)], 14: [(top, left)]}
            segs.extend(table[idx])
    return segs


def join_loops(segs):
    key = lambda p: (round(p[0], 2), round(p[1], 2))
    nxt = {}
    for a, b in segs:
        nxt.setdefault(key(a), []).append(b)
    loops = []
    used = set()
    for a, b in segs:
        ka = key(a)
        if (ka, key(b)) in used:
            continue
        loop = [a]
        cur = a
        for _ in range(20000):
            cands = [q for q in nxt.get(key(cur), []) if (key(cur), key(q)) not in used]
            if not cands:
                break
            q = cands[0]
            used.add((key(cur), key(q)))
            loop.append(q)
            cur = q
            if key(cur) == ka:
                break
        if len(loop) > 3:
            loops.append(loop)
    return loops


def area(pts):
    return sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))) / 2.0


def chaikin(pts, n):
    for _ in range(n):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q.append((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25))
            q.append((a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75))
        pts = q
    return pts[::2] if len(pts) > 600 else pts


def loop_d(pts):
    return "M " + " L ".join("%.0f %.0f" % p for p in pts) + " Z"


# ==================================================================== build
def build(**opt):
    """The whole map as markup.

    ground  "hills" (default) or "terraces" for the LiDAR relief
    icons   "drawn" (default) or "photo" to use badges cut from photographs
    """
    rng = random.Random(opt.get("seed", 13))
    ground = opt.get("ground", "hills")
    icons = opt.get("icons", "drawn")
    fairy = opt.get("fairy", False)
    p = []
    p.append('<svg class="park-map estate-map" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
             'xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="An illustrated map of the '
             'estate in the manner of a park map: six places, the drives between them, and the gate on '
             'Pope Creek Road">' % (W, H))
    p.append("<defs>%s</defs>" % tree_defs())

    # ------------------------------------------------------------- the land
    p.append('<g class="land">')
    p.append(el("rect", width=W, height=H, fill=CREAM))
    meta = {}
    if ground == "terraces":
        levels, fit, res = terrain_levels()
        meta["fit_residuals"] = res
        p.append('<g class="terraces">')
        by_level = {}
        for k, loop in levels:
            by_level.setdefault(k, []).append(loop)
        for k in sorted(by_level):
            d = " ".join(loop_d(l) for l in by_level[k])
            p.append('<g class="lvl" style="--l:%d">' % k)
            p.append('<path d="%s" fill="%s" opacity=".16" transform="translate(0 6)"/>' % (d, DEEP))
            p.append('<path d="%s" fill="%s" fill-opacity="%.2f"/>' % (d, SAGE if k % 2 else OLIVE,
                                                                     .2 + .04 * k if k % 2 else .1 + .025 * k))
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-opacity=".8"/>' % (d, CREAM))
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-opacity=".4" '
                     'transform="translate(0 3)"/>' % (d, DEEP))
            p.append("</g>")
        p.append("</g>")
    else:
        for (cx, cy, rx, ry, o) in ((360, 300, 420, 190, .20), (900, 640, 520, 200, .22),
                                    (1500, 640, 560, 220, .24), (1550, 230, 460, 160, .18),
                                    (620, 140, 520, 120, .16), (180, 640, 260, 190, .2)):
            p.append(el("ellipse", cx=cx, cy=cy + 8, rx=rx, ry=ry, fill=DEEP, opacity=.05))
            p.append(el("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, fill=OLIVE, opacity=o))
            p.append(el("ellipse", cx=cx - rx * .18, cy=cy - ry * .32, rx=rx * .62, ry=ry * .42,
                        fill=CREAM, opacity=.22))
    p.append(mountains())
    p.append("</g>")

    # ------------------------------------------------------ water and roads
    p.append('<g class="water">')
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="22" stroke-linecap="round"/>' % (em.CREEK, DEEP))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="17" stroke-linecap="round"/>' % (em.CREEK, BLUE))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" '
             'stroke-dasharray="10 22" opacity=".7"/>' % (em.CREEK, CREAM))
    p.append("</g>")

    p.append('<g class="roads">')
    p.append('<path class="rd-edge" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="26" '
             'stroke-linecap="round"/>' % (em.POPE, DEEP))
    p.append('<path class="rd-body" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="20" '
             'stroke-linecap="round" stroke-opacity=".82"/>' % (em.POPE, DEEP))
    p.append('<path class="rd-dash" d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="11 12" '
             'opacity=".7"/>' % (em.POPE, CREAM))
    for d, kind in em.DRIVES:
        w = 22 if kind == "drive" else 14
        p.append('<path class="rd-edge" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="%d" '
                 'stroke-linecap="round" stroke-linejoin="round"/>' % (d, DEEP, w + 5))
    for d, kind in em.DRIVES:
        w = 22 if kind == "drive" else 14
        p.append('<path class="rd-body" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="%d" '
                 'stroke-linecap="round" stroke-linejoin="round"/>' % (d, CLAY, w))
        p.append('<path class="rd-shine" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                 'stroke-linecap="round" opacity=".3" transform="translate(-1.5 -2.5)"/>' % (d, CREAM, w * .32))
    for d, kind in em.DRIVES:
        if kind == "drive":
            p.append('<path class="rd-dash" d="%s" fill="none" stroke="%s" stroke-width="2" '
                     'stroke-dasharray="10 12" opacity=".75"/>' % (d, CREAM))
    p.append("</g>")

    p.append(gate())

    # ------------------------------------------------------------ parking
    p.append('<g class="parking">')
    for x, y, rx, ry in ((1668, 290, 92, 28), (1228, 448, 58, 20), (1132, 602, 76, 26)):
        p.append(el("ellipse", cx=x, cy=y, rx=rx, ry=ry, fill=SAGE, **sh(stroke_width=2)))
        p.append(el("circle", cx=x - rx + 24, cy=y, r=12, fill=CREAM, **sh(stroke_width=1.6)))
        p.append('<text x="%d" y="%d" dy=".35em" text-anchor="middle" font-family="%s" font-size="14" '
                 'font-weight="700" fill="%s">P</text>' % (x - rx + 24, y, SANS, DEEP))
        p.append('<text x="%d" y="%d" dy=".35em" text-anchor="middle" font-family="%s" font-size="12" '
                 'font-weight="600" letter-spacing="1.5" fill="%s">PARKING</text>' % (x + 12, y, SANS, DEEP))
    p.append("</g>")

    # -------------------------------------------------------------- trees
    keep = []
    for d, _ in em.DRIVES:
        keep += em.flatten(d)
    keep += em.flatten(em.POPE) + em.flatten(em.CREEK)
    segs = [(keep[i], keep[i + 1]) for i in range(len(keep) - 1)
            if math.hypot(keep[i + 1][0] - keep[i][0], keep[i + 1][1] - keep[i][1]) < 60]
    avoid = [(st["x"], st["y"] - 40 * st["s"], 150 * st["s"] + 40) for st in STAND.values()]
    avoid += [(st["bx"], st["by"], 110) for st in STAND.values()]
    avoid += [(1752, 80, 220), (1930, 196, 50), (1046, 706, 70), (1720, 262, 100), (1170, 446, 80), (1880, 700, 190), (1960, 620, 90),
              (1112, 592, 90)]
    trees = []
    for poly_ in em.WOODS:
        xs = [q[0] for q in poly_]
        ys = [q[1] for q in poly_]
        target = int((max(xs) - min(xs)) * (max(ys) - min(ys)) / 2700)
        tries = placed = 0
        while placed < target and tries < target * 60:
            tries += 1
            x = rng.uniform(min(xs), max(xs))
            y = rng.uniform(min(ys), max(ys))
            if not em.inside(poly_, x, y):
                continue
            if any(math.hypot(x - ax, y - ay) < r for ax, ay, r in avoid):
                continue
            if any(em.pt_seg(x, y, a[0], a[1], b[0], b[1]) < 30 for a, b in segs):
                continue
            if any(math.hypot(x - tx, y - ty) < 22 for ty, tx, _, _, _ in trees):
                continue
            trees.append((y, x, rng.choice(["tb1", "tb2", "tf1", "tf2", "tf1"]),
                          rng.uniform(.82, 1.2), rng.random()))
            placed += 1
    trees.sort()
    p.append('<g class="forest">')
    for y, x, kind, s, t in trees:
        colour = SAGE if t > .78 else OLIVE
        delay = .9 * (x / W) + .25 * (y / H) + rng.uniform(0, .12)
        p.append(use_tree(kind, x, y, s, colour, delay))
    p.append("</g>")

    # ----------------------------------------------------------- the details
    # Grass tufts and wildflowers on the open ground: the small things that
    # make a park map feel walked rather than surveyed.
    p.append('<g class="meadow">')
    done = 0
    for _ in range(4000):
        if done >= 90:
            break
        x, y = rng.uniform(40, W - 40), rng.uniform(60, H - 40)
        if any(em.inside(q, x, y) for q in em.WOODS):
            continue
        if any(math.hypot(x - ax, y - ay) < r for ax, ay, r in avoid):
            continue
        if any(em.pt_seg(x, y, a[0], a[1], b[0], b[1]) < 26 for a, b in segs):
            continue
        done += 1
        if rng.random() < .55:
            p.append('<path d="M %.0f %.0f q 2 -9 4 0 q 2 -13 5 0 q 2 -8 4 0" fill="none" stroke="%s" '
                     'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity=".75"/>'
                     % (x, y, OLIVE))
        else:
            for dx, dy in ((0, 0), (7, 3), (-6, 4), (2, 8)):
                if rng.random() < .8:
                    p.append(el("circle", cx=x + dx, cy=y + dy, r=2.6,
                                fill=rng.choice([WHITE, WHITE, CLAY, BLUE]), stroke=DEEP, stroke_width=.7))
    p.append("</g>")

    p.append('<g class="sky">%s%s%s' % (cloud(430, 60, .95), cloud(820, 62, .75), cloud(120, 212, .7)))
    for bx, by in ((520, 58), (544, 50), (560, 64), (900, 52)):
        p.append('<path d="M %d %d q 6 -6 12 0 q 6 -6 12 0" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linecap="round" opacity=".55"/>' % (bx, by, DEEP))
    p.append("</g>")

    p.append('<g class="signs">')
    for x, y, text in ((248, 444, "Exit only"), (470, 484, "One way"), (880, 470, "One way"),
                       (856, 636, "Entrance"), (486, 322, "Vendors")):
        w = len(text) * 8.4 + 18
        p.append(el("line", x1=x, y1=y + 4, x2=x, y2=y + 22, stroke=DEEP, stroke_width=3))
        p.append(el("rect", x=x - w / 2.0, y=y - 12, width=w, height=18, rx=3, fill=CREAM, **sh(stroke_width=1.6)))
        p.append('<text x="%d" y="%d" dy=".33em" text-anchor="middle" font-family="%s" font-size="11" '
                 'font-weight="600" letter-spacing=".8" fill="%s">%s</text>' % (x, y - 3, SANS, DEEP, text.upper()))
    p.append("</g>")

    # ----------------------------------------------------------- the places
    p.append('<g class="map-places">')
    photos = opt.get("photo_hrefs", {})
    for i, key in enumerate(ORDER):
        st = STAND[key]
        pl = em.PLACES[key]
        bd = .1 * i
        p.append('<a class="map-place map-%s" data-place="%s" href="%s" xlink:href="%s" aria-label="%s">'
                 % (key, key, pl["href"], pl["href"], pl["label"]))
        p.append(el("circle", class_="map-halo", fill="transparent", cx=st["x"], cy=st["y"] - 50 * st["s"], r=140 * st["s"]))
        badge = icons == "photo" and key in photos
        # a framed picture stands taller than a drawn building; the village sits
        # hard against the top edge, so its frame and banner come down the hill
        dy = 20 if badge and key == "village" else 0
        s = st["s"] * ((.7 if key == "village" else .82) if badge else 1)
        p.append('<g transform="translate(%d %d) scale(%.2f)"><g class="b" style="--bd:%.2fs">'
                 '<g class="map-art">' % (st["x"], st["y"] + dy, s, bd))
        p.append(photo_badge(key, photos[key]) if badge else DRAW[key]())
        if fairy and not badge:
            for n, (fx, fy) in enumerate(FLAGS[key]):
                p.append(pennant(fx, fy, CLAY if n % 2 == 0 else BLUE, (i * 3 + n) * .17))
        p.append("</g></g></g>")
        p.append(banner(st["bx"], st["by"], pl["label"], bd))
        p.append("</a>")
    p.append("</g>")

    if fairy:
        p.append(fairy_layer(rng, avoid, segs))
    p.append(cartouche())
    # the frame, olive like the sketch's border
    p.append(el("rect", class_="frame", x=6, y=6, width=W - 12, height=H - 12, rx=18, fill="none",
                stroke=OLIVE, stroke_width=12))
    p.append(el("rect", x=16, y=16, width=W - 32, height=H - 32, rx=12, fill="none", stroke=DEEP,
                stroke_width=1.6, opacity=.6))
    p.append("</svg>")
    return "".join(p), dict(trees=len(trees), **meta)


def photo_badge(key, href):
    """An arched window with the photograph of the real building in it."""
    g = []
    d = "M -110 -6 V -128 Q -110 -176 0 -186 Q 110 -176 110 -128 V -6 Z"
    cid = "arch-%s" % key
    g.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    g.append(el("ellipse", cx=12, cy=10, rx=140, ry=18, fill=DEEP, opacity=.14))
    # a little flagpole on the crown, the way a park map marks an attraction
    g.append(el("line", x1=0, y1=-196, x2=0, y2=-236, stroke=DEEP, stroke_width=3))
    g.append(poly([(1, -236), (34, -227), (1, -218)], fill=CLAY, **sh(stroke_width=1.6)))
    g.append(el("circle", cx=0, cy=-238, r=4, fill=CREAM, **sh(stroke_width=1.4)))
    g.append('<path d="M -124 8 V -130 Q -124 -190 0 -200 Q 124 -190 124 -130 V 8 Z" fill="%s" stroke="%s" '
             'stroke-width="2.6" stroke-linejoin="round"/>' % (CREAM, DEEP))
    g.append('<image href="%s" x="-110" y="-186" width="220" height="180" preserveAspectRatio="xMidYMid slice" '
             'clip-path="url(#%s)"/>' % (href, cid))
    g.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, DEEP))
    g.append('<path d="M -117 2 V -129 Q -117 -183 0 -193 Q 117 -183 117 -129 V 2" fill="none" stroke="%s" '
             'stroke-width="1.4" opacity=".8"/>' % CLAY)
    # the sill, with a hedge along it
    g.append(el("rect", x=-134, y=0, width=268, height=14, rx=4, fill=CREAM, **sh(stroke_width=2.2)))
    for k in range(-116, 124, 26):
        g.append(el("circle", cx=k, cy=0, r=12, fill=DEEP, stroke=DEEP, stroke_width=3))
    for k in range(-116, 124, 26):
        g.append(el("circle", cx=k, cy=0, r=12, fill=OLIVE))
        g.append(el("circle", cx=k - 4, cy=-4, r=3.2, fill=WHITE, opacity=.85))
    return "".join(g)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "map-lab")
    os.makedirs(out, exist_ok=True)
    svg, meta = build()
    open(os.path.join(out, "park-preview.svg"), "w", encoding="utf-8").write(svg)
    print("park map: %(trees)d trees" % meta, "%.0f KB" % (len(svg) / 1024.0))


if __name__ == "__main__":
    main()
