"""The social preview card, and the touch icon.

Without these, pasting the site into a message previews as a blank rectangle,
which is the first impression the client gets before the page has loaded at
all. The card reuses the heroes' scrim so the preview looks like the site
rather than like a stock template with a logo on it.

    python _build/make_social.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "assets")

# The same ramp site.css uses on a photograph hero, kept in step by hand.
HORIZ = [(0, .79), (.46, .75), (.62, .62), (.76, .34), (.88, .12), (.97, 0), (1, 0)]


def interp(stops, t):
    for i in range(1, len(stops)):
        x0, y0 = stops[i - 1]
        x1, y1 = stops[i]
        if t <= x1:
            return y1 if x1 == x0 else y0 + (y1 - y0) * (t - x0) / (x1 - x0)
    return stops[-1][1]
W, H = 1200, 630

src = Image.open(os.path.join(ROOT, "img", "hero-3.webp")).convert("RGB")
r = max(W / src.width, H / src.height)
src = src.resize((int(src.width * r), int(src.height * r)), Image.LANCZOS)
src = src.crop(((src.width - W) // 2, int((src.height - H) * 0.45),
                (src.width - W) // 2 + W, int((src.height - H) * 0.45) + H))

# the same two-axis scrim the heroes use, so the card looks like the site
ink = Image.new("RGB", (W, H), (16, 20, 14))
mask = Image.new("L", (W, H))
d = mask.load()
for y in range(H):
    v = 0.0 if y < H * .25 else 0.45 * (y - H * .25) / (H * .75)
    for x in range(W):
        px = x / W
        a = interp(HORIZ, px)
        d[x, y] = int(255 * (1 - (1 - a) * (1 - v)))
card = Image.composite(ink, src, mask)

dr = ImageDraw.Draw(card)
def font(name, size):
    for p in (r"C:\Windows\Fonts\%s" % name,):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

dr.text((72, 300), "ONE ESTATE.  ONE COUPLE.  ONE WEEKEND.",
        font=font("segoeuib.ttf", 21), fill=(247, 231, 206))
dr.text((70, 348), "The Valley Venues", font=font("georgia.ttf", 86), fill=(255, 255, 255))
dr.text((72, 470), "Seventy-four private acres beneath Lookout Mountain,",
        font=font("segoeui.ttf", 27), fill=(255, 255, 255))
dr.text((72, 508), "fifteen minutes from Chattanooga.",
        font=font("segoeui.ttf", 27), fill=(255, 255, 255))
card.save(os.path.join(ROOT, "og.jpg"), quality=86)
print("og.jpg", os.path.getsize(os.path.join(ROOT, "og.jpg")) // 1024, "KB")

# touch icon: the same three rings, rasterised the simple way
icon = Image.new("RGB", (180, 180), (35, 41, 31))
di = ImageDraw.Draw(icon)
import re
svg = open(os.path.join(ROOT, "favicon.svg"), encoding="utf-8").read()
for i, m in enumerate(re.finditer(r'd="M([^"]+?) Z"', svg)):
    pts = []
    for pair in m.group(1).replace("M", "").split(" L"):
        x, y = pair.split()
        pts.append((float(x) / 32 * 180, float(y) / 32 * 180))
    di.line(pts + [pts[0]], fill=(247, 231, 206), width=max(3, 8 - i * 2), joint="curve")
icon.save(os.path.join(ROOT, "icon-180.png"))
print("icon-180.png", os.path.getsize(os.path.join(ROOT, "icon-180.png")) // 1024, "KB")
