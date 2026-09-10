"""
Draw an illustrated skin from the aerial photograph.

The point is not to reproduce the NAIP frame. It is to work out what each piece
of ground *is* and repaint it as a flat shape, the way someone would draw an
estate map — so the model wears something designed rather than a satellite
photograph chopped into facets.

What decides woodland from mown field is texture, not colour. Both are green,
and dry grass is worse than useless to a greenness test: khaki has very little
blue in it, so g - (r+b)/2 comes out high and the open fields classify as
forest. Canopy is rough at the scale of a tree crown; a mown field is smooth.
Local range over a 7px window separates them cleanly.

The rest is presentation: shrink the *class map* rather than the photograph, run
a mode filter over it until the speckle becomes shapes, ink the boundaries, and
lay a whisper of the real tone back over the top so the flat regions read as
land under light. Big flat regions also cure the faceting — a quad can only
look like a facet if its neighbours are a different colour.
"""
import os
from PIL import Image, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "aerial.webp")).convert("RGB")
FULL = src.size[0]
SMALL = 380                 # where the detail dies, on purpose
ROUGH = 31                  # local range above this is canopy (~p38 of the frame)

WOOD_D  = (58, 84, 58)      # deep canopy
WOOD_L  = (98, 126, 80)     # sunlit canopy
PASTURE = (150, 172, 110)   # mown, still green
FIELD   = (198, 196, 142)   # cut and dry — the maze, the hay ground
BARE    = (226, 216, 188)   # track, gravel, roof
WATER   = (120, 152, 170)
PALETTE = [WOOD_D, WOOD_L, PASTURE, FIELD, BARE, WATER]

# --- roughness: the one measurement that knows wood from field --------------
lum = src.convert("L").filter(ImageFilter.GaussianBlur(1.0))
rough = ImageChops.subtract(lum.filter(ImageFilter.MaxFilter(7)),
                            lum.filter(ImageFilter.MinFilter(7)))
rough = rough.filter(ImageFilter.GaussianBlur(6))    # roughness of a region
rp = rough.load()

# Light and shade are decided on a heavily blurred copy. Per-pixel, the split
# between lit and deep canopy happens at every individual tree crown and the
# result is speckle; at this scale it happens across a hillside, which is what
# is actually true and what an illustrator would draw.
soft = src.filter(ImageFilter.GaussianBlur(FULL / 110.0))
sp = soft.load()

work = src.filter(ImageFilter.MedianFilter(5))
px = work.load()

idx = []
for y in range(FULL):
    for x in range(FULL):
        r, g, b = px[x, y]
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / mx if mx else 0
        L = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
        sr, sg, sb = sp[x, y]                        # the same ground, softened
        SL = (sr * 0.299 + sg * 0.587 + sb * 0.114) / 255.0

        if (b - g) > 16 and (b - r) > 16 and L > 0.28:
            i = 5                                    # water
        elif sat < 0.13 and L > 0.50:
            i = 4                                    # roof, gravel, track
        elif rp[x, y] >= ROUGH:
            i = 1 if SL > 0.42 else 0                # canopy, lit or deep
        elif (sg - sr) > 2 and (sg - sb) > 34:
            i = 2                                    # green pasture
        else:
            i = 3 if SL > 0.44 else 2                # cut and dry
        idx.append(i)

cls = Image.new("P", (FULL, FULL))
cls.putdata(idx)
flat = [v for c in PALETTE for v in c]
cls.putpalette(flat + [0] * (768 - len(flat)))

# Shrink the class map itself. Nearest keeps it a class map rather than
# blending two land types into a third that means nothing.
cls = cls.resize((SMALL, SMALL), Image.NEAREST)
for _ in range(4):
    cls = cls.filter(ImageFilter.ModeFilter(7))

# Ink the boundaries the way an illustrator would — not an outline so much as
# a settling of the edge.
lab = cls.convert("L")
edge = ImageChops.difference(lab.filter(ImageFilter.MaxFilter(3)),
                             lab.filter(ImageFilter.MinFilter(3)))
edge = edge.point(lambda v: 196 if v > 0 else 255)

out = cls.convert("RGB").resize((FULL, FULL), Image.BICUBIC)
edge = edge.resize((FULL, FULL), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2.0))
out = ImageChops.multiply(out, edge.convert("RGB"))

# Tone, centred on mid-grey so it lifts as often as it deepens. Multiplying by
# the photograph simply made the whole estate darker.
tone = src.convert("L").filter(ImageFilter.GaussianBlur(FULL / 70.0))
mean = sum(tone.histogram()[i] * i for i in range(256)) / float(FULL * FULL)
tone = tone.point(lambda v: max(0, min(255, 128 + int((v - mean) * 0.5))))
out = Image.blend(out, ImageChops.overlay(out, tone.convert("RGB")), 0.38)

# The model can only carry one colour per cell of a 256-square mesh, and a
# region boundary crossing that grid at a shallow angle becomes a long, obvious
# staircase — there is no anti-aliasing to be had when every quad is a single
# flat fill. Softening the boundary over a couple of cells turns the staircase
# into a gradient. 7px here is about 1.3 cells; much less and the steps return,
# much more and the shapes stop reading as drawn.
out = out.filter(ImageFilter.GaussianBlur(7.0))

out.save(os.path.join(HERE, "illustrated.webp"), quality=88, method=5)
print("illustrated.webp %dx%d  %d KB"
      % (FULL, FULL, os.path.getsize(os.path.join(HERE, "illustrated.webp")) // 1024))
