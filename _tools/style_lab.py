"""
The style lab: the home page in three spa-like restyles, side by side.

    python _tools/style_lab.py      # after _build/build.py

Each option is the real, current home page with one extra stylesheet laid over
it, so every option shows the actual content, film, gallery links and forms,
and choosing one means folding its sheet into site.css. Nothing here touches
the live pages. /style-lab/ is unlinked and noindexed.

The palette does not change: the client's seven colours and white, nothing
tinted. What changes is how much of it is used. Measured against the deep ink,
only sage is light enough to fill a button behind text (6.2:1); olive (4.4),
clay (3.9) and blue (3.9) miss the 4.5 floor, so they are used for lines,
arches, bands without small text, and ornament.
"""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, "style-lab")

OPTIONS = [
    ("current", "Current", "The site as it is today."),
    ("a", "A · Sage &amp; Linen", "Ivory ground, sage buttons and bands, soft rounded photographs, a sage footer."),
    ("b", "B · Morning Light", "White and airy, arched photographs like a spa's windows, blue hairlines, italic accents."),
    ("c", "C · Warm Retreat", "Warm cream ground, photographs set on sage and olive panels, generous curves and soft shadows."),
    ("d", "D · Sage &amp; Linen, arched", "A, with B's arched photographs."),
    ("e", "E · Sage &amp; Linen, framed", "A, with C's photographs set on panels and white cards."),
]

BAR = """
<nav class="sl-bar" aria-label="Style options">
  <span class="sl-title">Spa restyle</span>
  %s
</nav>
<style>
.sl-bar{position:fixed;left:50%%;bottom:1rem;transform:translateX(-50%%);z-index:200;
  display:flex;gap:.3rem;align-items:center;flex-wrap:wrap;justify-content:center;
  max-width:calc(100vw - 1.5rem);padding:.4rem;border-radius:999px;
  background:#FFFFFF;border:1px solid #34372F;box-shadow:0 12px 34px rgba(52,55,47,.22);
  font:600 .7rem/1 "Libre Franklin",system-ui,sans-serif;letter-spacing:.06em}
.sl-title{padding:0 .6rem 0 .7rem;text-transform:uppercase;letter-spacing:.14em;color:#34372F}
.sl-bar a{color:#34372F;text-decoration:none;padding:.55rem .8rem;border-radius:999px;white-space:nowrap}
.sl-bar a:hover{background:#F5F1EA}
.sl-bar a[aria-current]{background:#34372F;color:#FFFFFF}
@media (max-width:640px){.sl-title{display:none}.sl-bar a{padding:.5rem .55rem}}
</style>
"""


def main():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    for slug, name, _ in OPTIONS:
        links = " ".join('<a href="/style-lab/%s/"%s>%s</a>' % (
            s, ' aria-current="page"' if s == slug else "", n.split(" · ")[0]) for s, n, _ in OPTIONS)
        page = src
        extra = ""
        if slug != "current":
            css = os.path.join(LAB, slug + ".css")
            v = hashlib.md5(open(css, "rb").read()).hexdigest()[:8]
            extra = '<link rel="stylesheet" href="/style-lab/%s.css?v=%s">\n' % (slug, v)
        if 'name="robots"' not in page:
            extra = '<meta name="robots" content="noindex,nofollow">\n' + extra
        page = page.replace("</head>", extra + "</head>", 1)
        page = re.sub(r"<title>[^<]*</title>", "<title>%s &middot; Spa restyle</title>" % name, page, 1)
        page = page.replace("</body>", BAR % links + "</body>", 1)
        d = os.path.join(LAB, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)
        print("  /style-lab/%s/" % slug)

    cards = "".join(
        '<a class="c" href="/style-lab/%s/"><b>%s</b><span>%s</span></a>' % (s, n, d) for s, n, d in OPTIONS)
    open(os.path.join(LAB, "index.html"), "w", encoding="utf-8").write("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Spa restyle &middot; The Valley Venues</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,400&family=Libre+Franklin:wght@400;500;600&display=swap">
<style>
body{margin:0;background:#F5F1EA;color:#34372F;font:400 16px/1.6 "Libre Franklin",system-ui,sans-serif}
.w{max-width:60rem;margin:0 auto;padding:3rem 1.2rem}
h1{font:300 clamp(2.2rem,5vw,3.4rem)/1.05 "Cormorant Garamond",Georgia,serif;margin:0 0 .8rem}
p{max-width:40rem;margin:0 0 2rem}
.g{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fill,minmax(14rem,1fr))}
.c{display:flex;flex-direction:column;gap:.4rem;padding:1.3rem;background:#fff;border:1px solid #AABEB3;
  border-radius:16px;color:inherit;text-decoration:none}
.c:hover{border-color:#34372F}
.c b{font:400 1.5rem/1.1 "Cormorant Garamond",Georgia,serif}
.c span{font-size:.9rem}
</style></head><body><div class="w">
<h1>The home page, three ways</h1>
<p>Each option is the real home page with one stylesheet over it, in the client's seven colours and
white. Use the bar at the foot of each page to flip between them.</p>
<div class="g">%s</div></div></body></html>""" % cards)
    print("  /style-lab/")


if __name__ == "__main__":
    main()
