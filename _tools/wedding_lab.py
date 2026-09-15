"""
The Weddings page, ten ways. For the owner to choose a direction from.

    python _tools/wedding_lab.py        # writes /wedding-lab/, noindex, unlinked

Brief, from the owner (2026-09-15): the rounded, panelled style read as
"bloggy", "stickers", "Canva not Adobe". She wants what a luxury resort site
looks like: large images, elegant type, generous space, nothing bubbly. Olive
with a yellow undertone rather than sage. Short, and quick to get through on a
phone, since most visitors arrive from Instagram.

Every direction uses the same words and photographs so only the design
differs, and all of them keep to the owner's own colours:

    ink       #2B1B00  her pamphlet's text brown (15.9:1 on parchment)
    parchment #FFF9F3  her base, read from her Canva Welcome Book
    olive     #7B7951  her grey olive (4.3:1: large type and rules only)
    accent    #FC5324  used sparingly -- a line, a mark, never a field of it
    white     #FFFFFF

Nothing here has rounded corners. No photograph of Magnolia House from before
the May 2025 fire, and no itinerary ("where you marry" etc.).
"""
import json
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "wedding-lab")
GAL = {g["id"]: g for g in json.load(open(os.path.join(ROOT, "assets", "gallery.json"), encoding="utf-8"))}

INK, PARCH, OLIVE, ACCENT, WHITE = "#2B1B00", "#FFF9F3", "#7B7951", "#FC5324", "#FFFFFF"


def webp_size(path):
    h = open(path, "rb").read(30)
    f = h[12:16]
    if f == b"VP8X":
        return struct.unpack("<I", h[24:27] + b"\0")[0] + 1, struct.unpack("<I", h[27:30] + b"\0")[0] + 1
    if f == b"VP8L":
        b = struct.unpack("<I", h[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    w, hh = struct.unpack("<HH", h[26:30])
    return w & 0x3FFF, hh & 0x3FFF


def im(key, alt, cls="", sizes="100vw", eager=False):
    """A photograph from the gallery (by id) or the site (img:name)."""
    load = "eager" if eager else "lazy"
    c = ' class="%s"' % cls if cls else ""
    if key.startswith("img:"):
        name = key[4:]
        w, h = webp_size(os.path.join(ROOT, "assets", "img", name + ".webp"))
        return '<img src="/assets/img/%s.webp" alt="%s" width="%d" height="%d"%s loading="%s" decoding="async">' % (
            name, alt, w, h, c, load)
    g = GAL[key]
    k = min(1.0, 1600.0 / max(g["w"], g["h"]))
    sk = min(1.0, 640.0 / max(g["w"], g["h"]))
    return ('<img src="/assets/gallery/%s.webp" srcset="/assets/gallery/%s-sm.webp %dw, /assets/gallery/%s.webp %dw" '
            'sizes="%s" alt="%s" width="%d" height="%d"%s loading="%s" decoding="async">' % (
                key, key, round(g["w"] * sk), key, round(g["w"] * k), sizes, alt,
                round(g["w"] * k), round(g["h"] * k), c, load))


# ------------------------------------------------------------------ the words
C = dict(
    eyebrow="Weddings at The Valley Venues",
    h1="More than a wedding day.",
    stand="One wedding at a time, on seventy-four private acres beneath Lookout Mountain. "
          "The whole estate is yours, for a day or a weekend.",
    cta="Download the Wedding Pamphlet", cta_href="/pricing/",
    line="The ceremony takes thirty minutes. The rest of it is what you will remember.",
    ways_h="Three ways to celebrate",
    ways=[
        dict(name="Single Day Celebration", kind="One day",
             text="The whole estate, closed around one wedding for the day.",
             href="/weddings/single-day/", img="aybee-dominy-3700",
             alt="A bride and groom walking back up the aisle in the meadow"),
        dict(name="The Estate Weekend", kind="Two nights",
             text="The estate from the day before, the rehearsal dinner set up for you, "
                  "and two nights of lodging on the property.",
             href="/stay/", img="copy-of-dsc05971-arw-1",
             alt="A couple at a picnic breakfast laid in the meadow"),
        dict(name="All-Inclusive Estate Experience", kind="Everything handled",
             text="Design, coordination, catering, the bar and the music, from one team, "
                  "with Kobi's own hand in the design.",
             href="/weddings/whats-included/", img="copy-of-the-valley-venues-kristen-thomison-photo-63",
             alt="A reception table dressed in blue and white"),
    ],
    claim_h="One wedding on the property. Never two.",
    claim="No second ceremony on the lawn, no reset between parties, nobody else's guests. "
          "For as long as it is yours, the estate is closed to everyone you did not invite.",
    spaces_h="Every space is part of it.",
    spaces="Magnolia House, The Valley, Davis Hall and its Lookout Deck, and the cottages of "
           "Overlook Village. However you arrange the day, all of it is yours.",
    spaces_href="/the-estate/",
    gal_h="Weddings that happened here",
    gal_href="/gallery/",
    book_h="What it costs, and everything it includes.",
    book="The Wedding Pamphlet has every figure and every space. It comes to your email and "
         "your phone in about a minute.",
)
HERO_WIDE = "img:weddings"          # the meadow ceremony, guests seated toward the ridge
HERO_ALT = "A ceremony in the meadow, guests seated toward the ridge"
AERIAL = "dji-0673"
SPACES = [("img:included", "The conservatory at Magnolia House, lit for a reception"),
          ("copy-of-3i0a4529vh", "A couple laughing on the Lookout Deck"),
          ("img:stay-village", "The cottages of Overlook Village on the hillside"),
          ("4k6a0982anthonyalexa", "A couple in the meadow"),
          ("img:davis-hall", "Davis Hall lit for the first dance")]
STRIP = ["copy-of-thevalley-6-1", "copy-of-3i0a4588vh", "copy-of-the-valley-venues-kristen-thomison-photo-96",
         "misty-lancaster-dsc03782-1", "sarah-larae-engagement-75", "copy-of-thevalley"]

LOGO = '<a class="lw-mark" href="/">The Valley Venues</a>'


def head_bar(extra=""):
    return ('<header class="lw-head">%s<nav class="lw-nav" aria-label="Primary">'
            '<a href="/weddings/">Weddings</a><a href="/the-estate/">The Estate</a><a href="/stay/">Stay</a>'
            '<a href="/gallery/">Gallery</a><a href="/about/">About</a></nav>'
            '<a class="lw-cta" href="%s">%s</a>%s</header>' % (LOGO, C["cta_href"], C["cta"], extra))


def ways_items(tpl, sizes="(max-width:760px) 100vw, 33vw"):
    return "".join(tpl % dict(w, photo=im(w["img"], w["alt"], sizes=sizes)) for w in C["ways"])


def strip(n=6, sizes="(max-width:760px) 50vw, 17vw"):
    return "".join("<figure>%s</figure>" % im(k, "A wedding at The Valley Venues", sizes=sizes) for k in STRIP[:n])


# ================================================================ directions
D = []


def direction(slug, name, idea, fonts):
    def wrap(fn):
        D.append(dict(slug=slug, name=name, idea=idea, fonts=fonts, fn=fn))
        return fn
    return wrap


BASE_CSS = """
*{box-sizing:border-box}html,body{margin:0}img{display:block;max-width:100%%;height:auto}
body{background:%(parch)s;color:%(ink)s;-webkit-font-smoothing:antialiased;padding-bottom:4rem}
a{color:inherit}
:focus-visible{outline:2px solid %(accent)s;outline-offset:3px}
.lw-head{display:flex;align-items:center;gap:1.5rem;padding:1.1rem clamp(1.2rem,4vw,3.5rem)}
.lw-mark{text-decoration:none;white-space:nowrap}
.lw-nav{display:flex;gap:1.6rem;margin-left:auto}
.lw-nav a,.lw-cta{text-decoration:none}
@media (max-width:900px){.lw-nav{display:none}.lw-cta{margin-left:auto}}
@media (max-width:480px){.lw-cta{display:none}}
.sr{position:absolute;left:-9999px}
.lab-switch{position:fixed;left:50%%;bottom:.8rem;transform:translateX(-50%%);z-index:99;display:flex;gap:2px;
  background:%(ink)s;padding:3px;font:600 11px/1 system-ui,sans-serif;max-width:calc(100vw - 1rem);overflow-x:auto}
.lab-switch a{color:%(parch)s;text-decoration:none;padding:.55rem .6rem;white-space:nowrap}
.lab-switch a[aria-current]{background:%(parch)s;color:%(ink)s}
""" % dict(parch=PARCH, ink=INK, accent=ACCENT)


# ---------------------------------------------------------------------- 01
@direction("01", "Aegean",
           "The resort site: a full-screen photograph, the headline set large and light beneath it, "
           "and a great deal of empty parchment. Everything centred and quiet.",
           "Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@400;500")
def d01():
    css = """
body{font:400 17px/1.7 Jost,sans-serif}
.lw-head{background:#FFF9F3}
.lw-mark{font:400 1.5rem/1 'Cormorant Garamond',serif;letter-spacing:.02em}
.lw-nav a,.lw-cta{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase}
.lw-cta{border-bottom:1px solid currentColor;padding-bottom:.2rem}
.hero{position:relative;height:calc(100svh - 4rem);min-height:30rem}
.hero img{width:100%;height:100%;object-fit:cover}
.intro{text-align:center;padding:clamp(4rem,12vw,9rem) 1.4rem clamp(3rem,9vw,7rem);max-width:52rem;margin:0 auto}
.eyebrow{font-size:.72rem;letter-spacing:.3em;text-transform:uppercase;color:#7B7951}
h1,h2{font-family:'Cormorant Garamond',serif;font-weight:300;margin:0;line-height:1.02}
h1{font-size:clamp(3rem,9vw,7rem);margin:1.2rem 0 1.6rem}
.intro p{font-size:1.1rem;max-width:34rem;margin:0 auto 2.4rem}
.btn{display:inline-block;text-decoration:none;font-size:.74rem;letter-spacing:.24em;text-transform:uppercase;
  padding:1.1rem 2.2rem;border:1px solid #2B1B00;transition:background .4s,color .4s}
.btn:hover{background:#2B1B00;color:#FFF9F3}
.line{font:300 italic clamp(1.8rem,4.6vw,3.4rem)/1.2 'Cormorant Garamond',serif;text-align:center;
  max-width:44rem;margin:0 auto;padding:0 1.4rem clamp(4rem,10vw,8rem)}
.ways{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(1rem,2vw,2rem);padding:0 clamp(1.2rem,4vw,3.5rem) 3rem}
.way img{width:100%;aspect-ratio:3/4;object-fit:cover}
.way h3{font:400 1.8rem/1.1 'Cormorant Garamond',serif;margin:1.4rem 0 .6rem}
.way p{margin:0 0 1rem;font-size:.98rem}
.way a{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid #7B7951}
.center-h{text-align:center;font-size:clamp(2.2rem,5vw,3.6rem);padding:clamp(5rem,12vw,9rem) 1.4rem clamp(2rem,5vw,3.5rem)}
.full{margin-top:clamp(5rem,12vw,9rem)}
.full img{width:100%;height:80svh;object-fit:cover}
.claim{text-align:center;max-width:46rem;margin:0 auto;padding:clamp(3.5rem,9vw,6rem) 1.4rem}
.claim h2{font-size:clamp(2.2rem,5.4vw,4rem);margin-bottom:1.4rem}
.book{background:#7B7951;color:#FFF9F3;text-align:center;padding:clamp(4.5rem,11vw,8rem) 1.4rem;margin-top:clamp(3rem,8vw,6rem)}
.book h2{font-size:clamp(2.2rem,5vw,3.8rem);max-width:40rem;margin:0 auto 1.4rem}
.book p{max-width:32rem;margin:0 auto 2.4rem;font-size:1.05rem}
.book .btn{border-color:#FFF9F3}.book .btn:hover{background:#FFF9F3;color:#2B1B00}
@media (max-width:760px){.ways{grid-template-columns:1fr;gap:3rem}.way img{aspect-ratio:4/5}.full img{height:60svh}}
"""
    body = """
<section class="hero">%(hero)s</section>
<section class="intro"><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1><p>%(stand)s</p>
  <a class="btn" href="%(cta_href)s">%(cta)s</a></section>
<p class="line">%(line)s</p>
<h2 class="center-h">%(ways_h)s</h2>
<section class="ways">%(ways)s</section>
<figure class="full" style="margin-left:0;margin-right:0">%(aerial)s</figure>
<section class="claim"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="book"><h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
""" % dict(C, hero=im(HERO_WIDE, HERO_ALT, eager=True), aerial=im(AERIAL, "The estate from the air"),
           ways=ways_items('<article class="way">%(photo)s<h3>%(name)s</h3><p>%(text)s</p>'
                           '<a href="%(href)s">Discover</a></article>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 02
@direction("02", "Folio",
           "A magazine spread. The headline is set enormous in a high-contrast serif beside a tall "
           "photograph; the three experiences are full-width feature spreads with a drop cap.",
           "Bodoni+Moda:ital,opsz,wght@0,6..96,400;1,6..96,400&family=Libre+Franklin:wght@400;500")
def d02():
    css = """
body{font:400 16px/1.7 'Libre Franklin',sans-serif}
.lw-head{border-bottom:1px solid #2B1B00}
.lw-mark{font:italic 400 1.45rem/1 'Bodoni Moda',serif}
.lw-nav a,.lw-cta{font-size:.78rem;letter-spacing:.06em}
.lw-cta{font-weight:500}
.spread{display:grid;grid-template-columns:1.1fr 1fr;height:calc(100svh - 4.2rem);min-height:36rem}
.spread figure{margin:0;min-height:0;overflow:hidden}.spread img{width:100%;height:100%;object-fit:cover}
.spread-text{padding:clamp(2rem,6vw,5rem);display:flex;flex-direction:column;justify-content:flex-end}
.kick{font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;border-top:1px solid #2B1B00;padding-top:.8rem;margin-bottom:auto}
h1,h2,h3{font-family:'Bodoni Moda',serif;font-weight:400;margin:0}
h1{font-size:clamp(3.2rem,min(6.4vw,11svh),7rem);line-height:.92;letter-spacing:-.02em}
h1 em{font-style:italic}
.spread-text p{max-width:26rem;font-size:1.05rem;margin:1.8rem 0}
.btn{align-self:flex-start;text-decoration:none;background:#2B1B00;color:#FFF9F3;padding:1rem 1.6rem;font-size:.82rem;letter-spacing:.06em}
.btn:hover{background:#7B7951}
.pull{font:italic 400 clamp(2rem,5vw,4.2rem)/1.08 'Bodoni Moda',serif;padding:clamp(4rem,10vw,8rem) clamp(1.2rem,8vw,8rem);
  border-bottom:1px solid #2B1B00;max-width:70rem}
.feature{display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid #2B1B00}
.feature:nth-child(even) figure{order:2}
.feature figure{margin:0}.feature img{width:100%;height:100%;min-height:70svh;object-fit:cover}
.feature div{padding:clamp(2rem,6vw,5.5rem);align-self:center}
.feature .kind{font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:#7B7951}
.feature h3{font-size:clamp(2.2rem,4.4vw,3.8rem);line-height:1;margin:.8rem 0 1.4rem}
.feature p::first-letter{font:400 3.6em/.8 'Bodoni Moda',serif;float:left;margin:.08em .12em 0 0}
.feature p{max-width:28rem;font-size:1.05rem}
.feature a{font-weight:500;text-decoration-thickness:1px;text-underline-offset:.3em}
.claim{display:grid;grid-template-columns:1fr 1fr;gap:clamp(2rem,6vw,5rem);padding:clamp(4rem,10vw,8rem) clamp(1.2rem,8vw,8rem);border-bottom:1px solid #2B1B00}
.claim h2{font-size:clamp(2.4rem,5vw,4.4rem);line-height:1}
.claim p{font-size:1.1rem;align-self:end}
.book{padding:clamp(4rem,10vw,8rem) clamp(1.2rem,8vw,8rem);text-align:left}
.book h2{font:italic 400 clamp(2.4rem,6vw,5rem)/1 'Bodoni Moda',serif;max-width:14ch;margin-bottom:1.6rem}
.book p{max-width:30rem;margin-bottom:2rem}
@media (max-width:820px){.spread{height:auto}.spread,.feature,.claim{grid-template-columns:1fr}.spread figure{height:62svh}
  .feature:nth-child(even) figure{order:0}.feature img{min-height:0;aspect-ratio:4/5}}
"""
    body = """
<section class="spread"><figure>%(hero)s</figure><div class="spread-text"><div class="kick">%(eyebrow)s</div>
  <h1>More than a <em>wedding</em> day.</h1><p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
<p class="pull">%(line)s</p>
%(ways)s
<section class="claim"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="book"><h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
""" % dict(C, hero=im("copy-of-thevalley", "A couple between two floral arches in the meadow", eager=True,
                      sizes="(max-width:820px) 100vw, 55vw"),
           ways=ways_items('<article class="feature"><figure>%(photo)s</figure><div><div class="kind">%(kind)s</div>'
                           '<h3>%(name)s</h3><p>%(text)s</p><a href="%(href)s">Read more</a></div></article>',
                           sizes="(max-width:820px) 100vw, 50vw"))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 03
@direction("03", "Horizon",
           "The estate as a sequence of wide landscapes. Each section is one panoramic photograph and "
           "one line beneath it, nothing else. The shortest page of the ten.",
           "Italiana&family=Jost:wght@300;400;500")
def d03():
    css = """
body{font:300 17px/1.75 Jost,sans-serif}
.lw-mark{font:400 1.5rem/1 Italiana,serif;letter-spacing:.08em;text-transform:uppercase}
.lw-nav a,.lw-cta{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;font-weight:400}
.pano{margin:0}.pano img{width:100%;aspect-ratio:21/9;object-fit:cover}
.cap{display:grid;grid-template-columns:1fr 1.3fr;gap:clamp(1.5rem,5vw,5rem);align-items:baseline;
  padding:clamp(2rem,5vw,3.5rem) clamp(1.2rem,5vw,4.5rem) clamp(4rem,10vw,7rem)}
h1,h2,h3{font-family:Italiana,serif;font-weight:400;margin:0;line-height:1.05;letter-spacing:.01em}
h1{font-size:clamp(2.8rem,6.6vw,5.6rem)}
h2{font-size:clamp(2.2rem,4.6vw,3.8rem)}
.cap p{margin:0 0 1.4rem;max-width:34rem}
.eyebrow{font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:#7B7951;margin-bottom:1rem}
.link{font-size:.74rem;letter-spacing:.22em;text-transform:uppercase;text-decoration:none;font-weight:500;
  display:inline-flex;gap:.8rem;align-items:center}
.link::after{content:"";width:2.6rem;height:1px;background:#FC5324}
.ways{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#2B1B00;border-block:1px solid #2B1B00}
.way{background:#FFF9F3}
.way img{width:100%;aspect-ratio:21/9;object-fit:cover}
.way div{padding:1.8rem clamp(1.2rem,3vw,2.2rem) 2.4rem}
.way h3{font-size:1.9rem;margin-bottom:.6rem}
.way p{margin:0 0 1.2rem;font-size:.96rem}
@media (max-width:820px){.cap{grid-template-columns:1fr;gap:.4rem}.ways{grid-template-columns:1fr}.pano img{aspect-ratio:4/3}.way img{aspect-ratio:16/9}}
"""
    body = """
<figure class="pano">%(hero)s</figure>
<section class="cap"><div><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1></div>
  <div><p>%(stand)s</p><a class="link" href="%(cta_href)s">%(cta)s</a></div></section>
<figure class="pano">%(aerial)s</figure>
<section class="cap"><h2>%(line_short)s</h2><div><p>%(line)s</p></div></section>
<section class="ways">%(ways)s</section>
<section class="cap"><h2>%(claim_h)s</h2><div><p>%(claim)s</p></div></section>
<figure class="pano">%(estate)s</figure>
<section class="cap"><h2>%(book_h)s</h2><div><p>%(book)s</p><a class="link" href="%(cta_href)s">%(cta)s</a></div></section>
""" % dict(C, hero=im(HERO_WIDE, HERO_ALT, eager=True), aerial=im(AERIAL, "The estate from the air"),
           estate=im("img:estate", "The meadow opening beneath the ridge"), line_short="The rest of it.",
           ways=ways_items('<article class="way">%(photo)s<div><h3>%(name)s</h3><p>%(text)s</p>'
                           '<a class="link" href="%(href)s">Discover</a></div></article>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 04
@direction("04", "Atelier",
           "A design studio's precision: a strict grid, small letterspaced labels, fine olive rules, "
           "photographs set off-grid at different sizes, and a restrained serif for the words that matter.",
           "EB+Garamond:ital,wght@0,400;1,400&family=Tenor+Sans")
def d04():
    css = """
body{font:400 18px/1.65 'EB Garamond',serif}
.lw-head{border-bottom:1px solid #7B7951}
.lw-mark,.lw-nav a,.lw-cta,.lab,.btn{font-family:'Tenor Sans',sans-serif;text-transform:uppercase;letter-spacing:.18em;font-size:.72rem}
.lw-mark{font-size:.86rem;letter-spacing:.24em}
.g{display:grid;grid-template-columns:repeat(12,1fr);gap:0 clamp(.8rem,2vw,1.6rem);padding:0 clamp(1.2rem,4vw,3.5rem)}
.lab{color:#7B7951;display:block;margin-bottom:1rem}
h1,h2,h3{font-weight:400;margin:0;line-height:1.05}
.hero{padding-top:clamp(2.5rem,7vw,6rem);align-items:end}
.hero h1{grid-column:1/8;font-size:clamp(3rem,7.6vw,6.8rem);letter-spacing:-.01em}
.hero .side{grid-column:9/13;padding-bottom:.6rem}
.hero .side p{margin:0 0 1.6rem}
.btn{display:inline-block;text-decoration:none;padding:1rem 1.4rem;border:1px solid #2B1B00}
.btn:hover{background:#2B1B00;color:#FFF9F3}
.hero-img{grid-column:1/13;margin:clamp(2rem,5vw,3.5rem) 0 0}
.hero-img img{width:100%;height:78svh;object-fit:cover}
.line{grid-column:3/11;font-style:italic;font-size:clamp(1.7rem,3.6vw,2.8rem);line-height:1.2;
  padding:clamp(4rem,10vw,8rem) 0;text-align:center}
.rule{grid-column:1/13;border-top:1px solid #7B7951;padding-top:1rem}
.way{grid-column:span 4;padding:1.4rem 0 clamp(3rem,6vw,5rem)}
.way:nth-child(2){margin-top:clamp(3rem,8vw,7rem)}
.way img{width:100%;aspect-ratio:4/5;object-fit:cover;margin-bottom:1.2rem}
.way h3{font-size:1.9rem}
.way p{margin:.6rem 0 1rem}
.way a{font-family:'Tenor Sans',sans-serif;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase}
.claim{padding-block:clamp(4rem,9vw,7rem);align-items:start}
.claim h2{grid-column:1/7;font-size:clamp(2.4rem,4.8vw,4.2rem)}
.claim p{grid-column:8/13;margin:0}
.claim-img{grid-column:5/13}.claim-img img{width:100%;aspect-ratio:16/9;object-fit:cover}
.book{padding-block:clamp(4rem,9vw,7rem) clamp(3rem,6vw,5rem)}
.book h2{grid-column:1/8;font-size:clamp(2.2rem,4.4vw,3.8rem)}
.book .side{grid-column:9/13}
@media (max-width:820px){.g>*{grid-column:1/13!important}.hero .side{margin-top:1.4rem}.way{margin-top:0!important}.hero-img img{height:56svh}
  .line{text-align:left}.claim-img{margin-top:2rem}}
"""
    body = """
<section class="g hero"><h1>%(h1)s</h1><div class="side"><span class="lab">%(eyebrow)s</span><p>%(stand)s</p>
  <a class="btn" href="%(cta_href)s">%(cta)s</a></div>
  <figure class="hero-img">%(hero)s</figure></section>
<section class="g"><p class="line">%(line)s</p></section>
<section class="g"><div class="rule"><span class="lab">%(ways_h)s</span></div>%(ways)s</section>
<section class="g claim"><div class="rule" style="margin-bottom:2rem"></div><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="g"><figure class="claim-img" style="margin:0">%(aerial)s</figure></section>
<section class="g book"><h2>%(book_h)s</h2><div class="side"><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
""" % dict(C, hero=im(HERO_WIDE, HERO_ALT, eager=True), aerial=im(AERIAL, "The estate from the air"),
           ways=ways_items('<article class="way">%(photo)s<span class="lab">%(kind)s</span><h3>%(name)s</h3>'
                           '<p>%(text)s</p><a href="%(href)s">Discover</a></article>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 05
@direction("05", "Promenade",
           "Built for the phone. The headline sits over the bottom of a full-screen photograph on a solid "
           "parchment band, and the three experiences are full-height panels you swipe through sideways.",
           "Marcellus&family=Jost:wght@400;500")
def d05():
    css = """
body{font:400 16px/1.7 Jost,sans-serif}
.lw-mark{font:400 1.35rem/1 Marcellus,serif;letter-spacing:.06em}
.lw-nav a,.lw-cta{font-size:.74rem;letter-spacing:.16em;text-transform:uppercase}
.hero{position:relative;height:calc(100svh - 4rem);min-height:32rem;display:flex;align-items:flex-end}
.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero-band{position:relative;background:#FFF9F3;width:min(44rem,100%);padding:clamp(1.6rem,4vw,2.8rem) clamp(1.2rem,4vw,3rem) 0;margin-left:clamp(0rem,4vw,3.5rem)}
h1,h2,h3{font-family:Marcellus,serif;font-weight:400;margin:0;line-height:1.08}
h1{font-size:clamp(2.6rem,6.4vw,5rem)}
.eyebrow{font-size:.7rem;letter-spacing:.26em;text-transform:uppercase;color:#7B7951;margin-bottom:.9rem}
.hero-band p{margin:1rem 0 1.4rem;max-width:32rem}
.btn{display:inline-block;background:#7B7951;color:#fff;text-decoration:none;padding:1rem 1.6rem;font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;font-weight:500}
.btn:hover{background:#2B1B00}
.line{font:400 clamp(1.6rem,3.8vw,2.8rem)/1.25 Marcellus,serif;padding:clamp(3.5rem,9vw,7rem) clamp(1.2rem,6vw,5rem);max-width:56rem}
.rail-head{display:flex;justify-content:space-between;align-items:end;padding:0 clamp(1.2rem,4vw,3.5rem) 1.2rem}
.rail-head h2{font-size:clamp(1.8rem,3.4vw,2.6rem)}
.rail-head span{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:#7B7951}
.rail{display:flex;gap:.8rem;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 clamp(1.2rem,4vw,3.5rem) 1rem;scrollbar-width:thin}
.panel{flex:0 0 min(84vw,30rem);scroll-snap-align:start;position:relative;height:min(78svh,44rem);display:flex;align-items:flex-end}
.panel img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.panel div{position:relative;background:#FFF9F3;margin:0 0 0 0;padding:1.4rem 1.4rem 1.6rem;width:88%}
.panel .kind{font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;color:#7B7951}
.panel h3{font-size:1.7rem;margin:.4rem 0 .5rem}
.panel p{margin:0 0 .8rem;font-size:.94rem}
.panel a{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;font-weight:500}
.claim{background:#7B7951;color:#FFF9F3;margin-top:clamp(3.5rem,9vw,6rem);padding:clamp(3.5rem,9vw,7rem) clamp(1.2rem,6vw,5rem)}
.claim h2{font-size:clamp(2.2rem,5vw,4rem);max-width:18ch;margin-bottom:1.2rem}
.claim p{max-width:36rem;margin:0}
.book{padding:clamp(3.5rem,9vw,7rem) clamp(1.2rem,6vw,5rem)}
.book h2{font-size:clamp(2rem,4.4vw,3.4rem);max-width:20ch;margin-bottom:1rem}
.book p{max-width:32rem;margin:0 0 1.6rem}
@media (max-width:600px){.hero-band{margin:0}}
"""
    body = """
<section class="hero">%(hero)s<div class="hero-band"><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1>
  <p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
<p class="line">%(line)s</p>
<div class="rail-head"><h2>%(ways_h)s</h2><span>Swipe</span></div>
<section class="rail">%(ways)s</section>
<section class="claim"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="book"><h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
""" % dict(C, hero=im("copy-of-3i0a4529vh", "A couple laughing on the Lookout Deck", eager=True),
           ways=ways_items('<article class="panel">%(photo)s<div><div class="kind">%(kind)s</div><h3>%(name)s</h3>'
                           '<p>%(text)s</p><a href="%(href)s">Discover</a></div></article>', sizes="(max-width:760px) 84vw, 30rem"))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 06
@direction("06", "Diptych",
           "Two halves. A photograph holds still on the left while the words move on the right, and the "
           "photograph changes as each section arrives. On a phone the photograph sits above its words.",
           "Cormorant:ital,wght@0,400;1,400&family=Figtree:wght@400;500")
def d06():
    css = """
body{font:400 16px/1.75 Figtree,sans-serif}
.lw-head{border-bottom:1px solid #7B7951}
.lw-mark{font:italic 400 1.5rem/1 Cormorant,serif}
.lw-nav a,.lw-cta{font-size:.8rem}.lw-cta{font-weight:500}
.dip{display:grid;grid-template-columns:1fr 1fr}
.dip-img{position:sticky;top:0;height:100svh;margin:0;overflow:hidden}
.dip-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity 1s ease}
.dip-img img.on{opacity:1}
.dip-text section{min-height:100svh;display:flex;flex-direction:column;justify-content:center;padding:clamp(2rem,6vw,6rem)}
h1,h2,h3{font-family:Cormorant,serif;font-weight:400;margin:0;line-height:1.02}
h1{font-size:clamp(3rem,6vw,5.6rem)}
h2{font-size:clamp(2.2rem,4.4vw,3.8rem)}
h3{font-size:2rem}
.eyebrow{font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:#7B7951;margin-bottom:1.2rem}
.dip-text p{max-width:30rem;margin:1.2rem 0}
.btn{align-self:flex-start;text-decoration:none;border-bottom:1px solid #FC5324;padding-bottom:.35rem;font-weight:500;letter-spacing:.04em}
.line{font:italic 400 clamp(2rem,4vw,3.2rem)/1.2 Cormorant,serif}
.way{border-top:1px solid #7B7951;padding:1.6rem 0}
.way p{margin:.4rem 0 .6rem!important}
.way a{font-weight:500}
.mob{display:none}
@media (max-width:820px){.dip{grid-template-columns:1fr}.dip-img{display:none}.mob{display:block;width:100%;aspect-ratio:4/5;object-fit:cover}
  .dip-text section{min-height:0;padding:0 1.2rem 3.5rem}.dip-text section .mob{margin:0 -1.2rem 2rem;width:calc(100% + 2.4rem)}}
"""
    shots = [(HERO_WIDE, HERO_ALT), ("aybee-dominy-3700", "A bride and groom walking back up the aisle"),
             (AERIAL, "The estate from the air"), ("copy-of-the-valley-venues-kristen-thomison-photo-63", "A reception table dressed in blue and white")]
    imgs = "".join(im(k, a, cls="on" if i == 0 else "", eager=i == 0, sizes="50vw").replace("<img ", '<img data-i="%d" ' % i)
                   for i, (k, a) in enumerate(shots))
    mob = lambda i: im(shots[i][0], shots[i][1], cls="mob", sizes="100vw", eager=i == 0)
    ways = "".join('<div class="way"><div class="eyebrow" style="margin:0">%(kind)s</div><h3>%(name)s</h3><p>%(text)s</p>'
                   '<a href="%(href)s">Discover</a></div>' % w for w in C["ways"])
    body = """
<div class="dip"><figure class="dip-img">%(imgs)s</figure><div class="dip-text">
<section data-i="0">%(m0)s<div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1><p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
<section data-i="1">%(m1)s<p class="line">%(line)s</p><h2 style="margin-top:2.5rem">%(ways_h)s</h2>%(ways)s</section>
<section data-i="2">%(m2)s<h2>%(claim_h)s</h2><p>%(claim)s</p><p>%(spaces)s</p><a class="btn" href="%(spaces_href)s">See the estate</a></section>
<section data-i="3">%(m3)s<h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
</div></div>
<script>
(function(){
  var imgs=[].slice.call(document.querySelectorAll('.dip-img img'));
  if(!('IntersectionObserver' in window))return;
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;var i=e.target.dataset.i;
    imgs.forEach(function(x){x.classList.toggle('on',x.dataset.i===i);});
  });},{rootMargin:'-45%% 0px -45%% 0px'});
  document.querySelectorAll('.dip-text section').forEach(function(s){io.observe(s);});
})();
</script>
""" % dict(C, imgs=imgs, ways=ways, m0=mob(0), m1=mob(1), m2=mob(2), m3=mob(3))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 07
@direction("07", "Invitation",
           "Stationery rather than a website: a narrow centred column, engraved capitals, fine double "
           "rules and photographs set in thin olive keylines, like the pages of a letterpress invitation.",
           "Cinzel:wght@400;500&family=EB+Garamond:ital,wght@0,400;1,400")
def d07():
    css = """
body{font:400 19px/1.7 'EB Garamond',serif;background:#FFF9F3}
.lw-head{justify-content:center;flex-wrap:wrap;border-bottom:3px double #7B7951}
.lw-mark{font:500 1.1rem/1 Cinzel,serif;letter-spacing:.24em;text-transform:uppercase;width:100%;text-align:center}
.lw-nav{margin:0 auto}.lw-nav a,.lw-cta{font:400 .7rem/1 Cinzel,serif;letter-spacing:.2em;text-transform:uppercase}
.lw-cta{position:absolute;right:clamp(1.2rem,4vw,3.5rem);top:1.2rem}
.col{max-width:40rem;margin:0 auto;padding:0 1.4rem;text-align:center}
.cap{font:500 .78rem/1.4 Cinzel,serif;letter-spacing:.3em;text-transform:uppercase;color:#7B7951}
h1,h2,h3{font-family:Cinzel,serif;font-weight:400;margin:0;line-height:1.2;letter-spacing:.06em;text-transform:uppercase}
h1{font-size:clamp(2rem,5.4vw,3.6rem);margin:1.4rem 0}
h2{font-size:clamp(1.5rem,3.4vw,2.2rem);margin-bottom:1.2rem}
h3{font-size:1.15rem;letter-spacing:.12em}
.orn{display:block;margin:2.2rem auto;width:7rem;height:10px;border-top:1px solid #7B7951;border-bottom:1px solid #7B7951}
.plate{margin:clamp(2.5rem,6vw,4rem) auto;padding:10px;border:1px solid #7B7951;max-width:62rem;width:calc(100% - 2.8rem)}
.plate img{width:100%;aspect-ratio:16/10;object-fit:cover}
.plate.tall{max-width:30rem}.plate.tall img{aspect-ratio:4/5}
.btn{display:inline-block;text-decoration:none;font:500 .74rem/1 Cinzel,serif;letter-spacing:.24em;text-transform:uppercase;
  padding:1.1rem 2rem;border:1px solid #2B1B00;outline:1px solid #2B1B00;outline-offset:3px;margin-top:1rem}
.btn:hover{background:#2B1B00;color:#FFF9F3}
.line{font-style:italic;font-size:clamp(1.5rem,3.4vw,2.2rem);line-height:1.35}
.ways{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(1.2rem,3vw,2.4rem);max-width:64rem;margin:0 auto;padding:0 1.4rem;text-align:center}
.way .plate{margin:0 0 1.4rem;width:100%}.way .plate img{aspect-ratio:3/4}
.way p{font-size:1.02rem;margin:.6rem 0}
.way a{font:400 .7rem/1 Cinzel,serif;letter-spacing:.2em;text-transform:uppercase}
section{padding:clamp(1.5rem,4vw,2.5rem) 0}
@media (max-width:760px){.ways{grid-template-columns:1fr;gap:3rem}.lw-cta{display:none}}
"""
    body = """
<section class="col" style="padding-top:clamp(3rem,8vw,5rem)"><div class="cap">%(eyebrow)s</div><h1>%(h1)s</h1>
  <p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
<figure class="plate">%(hero)s</figure>
<section class="col"><span class="orn"></span><p class="line">%(line)s</p><span class="orn"></span></section>
<section class="col"><h2>%(ways_h)s</h2></section>
<section class="ways">%(ways)s</section>
<section class="col"><span class="orn"></span><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<figure class="plate tall">%(tall)s</figure>
<section class="col" style="padding-bottom:clamp(4rem,10vw,7rem)"><h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
""" % dict(C, hero=im(HERO_WIDE, HERO_ALT, eager=True), tall=im("copy-of-thevalley", "A couple between two floral arches in the meadow"),
           ways=ways_items('<article class="way"><figure class="plate">%(photo)s</figure><div class="cap">%(kind)s</div>'
                           '<h3>%(name)s</h3><p>%(text)s</p><a href="%(href)s">Discover</a></article>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 08
@direction("08", "Cinema",
           "The estate film opens the page at full screen, with nothing laid over it. The headline follows "
           "in a wide, calm band, and the three experiences are full-width stills you scroll through.",
           "Gilda+Display&family=Jost:wght@400;500")
def d08():
    css = """
body{font:400 16px/1.75 Jost,sans-serif}
.lw-head{position:absolute;inset:0 0 auto;z-index:5;background:#FFF9F3}
.lw-mark{font:400 1.4rem/1 'Gilda Display',serif}
.lw-nav a,.lw-cta{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase}
.film{height:100svh;min-height:32rem;position:relative;background:#7B7951;overflow:hidden}
.film img,.film video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.band{display:grid;grid-template-columns:1.2fr 1fr;gap:clamp(2rem,6vw,6rem);align-items:end;padding:clamp(3rem,8vw,6rem) clamp(1.2rem,5vw,4.5rem)}
h1,h2,h3{font-family:'Gilda Display',serif;font-weight:400;margin:0;line-height:1.04}
h1{font-size:clamp(3rem,7.4vw,6.4rem)}
.eyebrow{font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:#7B7951;margin-bottom:1.2rem}
.band p{margin:0 0 1.6rem;max-width:30rem}
.btn{display:inline-block;text-decoration:none;background:#2B1B00;color:#FFF9F3;padding:1.05rem 1.8rem;font-size:.74rem;letter-spacing:.2em;text-transform:uppercase}
.btn:hover{background:#7B7951}
.still{position:relative;margin:0}
.still img{width:100%;height:92svh;object-fit:cover}
.still figcaption{display:grid;grid-template-columns:auto 1fr auto;gap:clamp(1rem,4vw,3rem);align-items:baseline;
  padding:1.4rem clamp(1.2rem,5vw,4.5rem) clamp(3rem,7vw,5rem)}
.still .kind{font-size:.7rem;letter-spacing:.26em;text-transform:uppercase;color:#7B7951;white-space:nowrap}
.still h3{font-size:clamp(1.8rem,3.4vw,2.8rem)}
.still p{margin:0;max-width:30rem}
.still a{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;white-space:nowrap}
.line{font:400 clamp(1.8rem,4.4vw,3.4rem)/1.2 'Gilda Display',serif;text-align:center;max-width:48rem;margin:0 auto;padding:clamp(3rem,8vw,6rem) 1.4rem}
.claim{background:#7B7951;color:#FFF9F3;text-align:center;padding:clamp(4rem,10vw,8rem) 1.4rem}
.claim h2{font-size:clamp(2.2rem,5.6vw,4.4rem);max-width:18ch;margin:0 auto 1.4rem}
.claim p{max-width:34rem;margin:0 auto}
@media (max-width:820px){.band{grid-template-columns:1fr}.still figcaption{grid-template-columns:1fr;gap:.4rem}.still img{height:64svh}}
"""
    body = """
<section class="film"><img src="/assets/video/hero-poster.webp" alt="" aria-hidden="true">
  <video autoplay muted loop playsinline poster="/assets/video/hero-poster.webp" aria-hidden="true">
  <source src="/assets/video/hero.webm" type="video/webm"><source src="/assets/video/hero.mp4" type="video/mp4"></video></section>
<section class="band"><div><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1></div>
  <div><p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
<p class="line">%(line)s</p>
%(ways)s
<section class="claim"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="band"><div><h2 style="font-size:clamp(2.2rem,5vw,4rem)">%(book_h)s</h2></div>
  <div><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
""" % dict(C, ways=ways_items('<figure class="still">%(photo)s<figcaption><span class="kind">%(kind)s</span>'
                             '<div><h3>%(name)s</h3><p>%(text)s</p></div><a href="%(href)s">Discover</a></figcaption></figure>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 09
@direction("09", "Olive Grove",
           "Colour does the work. Whole sections are laid in the owner's olive with parchment type, "
           "alternating with parchment ones, so the page reads as a few large, confident blocks.",
           "Libre+Caslon+Display&family=Libre+Caslon+Text:ital@0;1&family=Jost:wght@500")
def d09():
    css = """
body{font:400 17px/1.75 'Libre Caslon Text',serif}
.lw-head{background:#7B7951;color:#FFF9F3}
.lw-mark{font:400 1.45rem/1 'Libre Caslon Display',serif}
.lw-nav a,.lw-cta{font:500 .72rem/1 Jost,sans-serif;letter-spacing:.18em;text-transform:uppercase}
.olive{background:#7B7951;color:#FFF9F3}
h1,h2,h3{font-family:'Libre Caslon Display',serif;font-weight:400;margin:0;line-height:1.02}
.hero{display:grid;grid-template-columns:1fr 1fr;min-height:calc(100svh - 4rem)}
.hero-text{padding:clamp(2rem,6vw,5.5rem);display:flex;flex-direction:column;justify-content:center}
.hero h1{font-size:clamp(3.2rem,7vw,6.6rem)}
.eyebrow{font:500 .72rem/1 Jost,sans-serif;letter-spacing:.24em;text-transform:uppercase;margin-bottom:1.6rem;opacity:.9}
.hero-text p{font-size:1.12rem;max-width:28rem;margin:1.6rem 0 2.2rem}
.hero figure{margin:0}.hero img{width:100%;height:100%;object-fit:cover}
.btn{align-self:flex-start;display:inline-block;text-decoration:none;font:500 .74rem/1 Jost,sans-serif;letter-spacing:.2em;text-transform:uppercase;
  padding:1.1rem 1.8rem;background:#FFF9F3;color:#2B1B00}
.btn:hover{background:#2B1B00;color:#FFF9F3}
.btn.dark{background:#2B1B00;color:#FFF9F3}.btn.dark:hover{background:#7B7951}
.line{font:italic 400 clamp(1.8rem,4.2vw,3.2rem)/1.25 'Libre Caslon Text',serif;padding:clamp(4rem,10vw,8rem) clamp(1.2rem,8vw,9rem);max-width:64rem}
.ways{display:grid;grid-template-columns:repeat(3,1fr)}
.way{display:flex;flex-direction:column}
.way img{width:100%;aspect-ratio:1/1;object-fit:cover}
.way div{padding:2rem clamp(1.2rem,3vw,2.6rem) 3rem;flex:1}
.way:nth-child(2) div{background:#7B7951;color:#FFF9F3}
.way h3{font-size:2rem;margin-bottom:.8rem}
.way p{margin:0 0 1.2rem}
.way a{font:500 .72rem/1 Jost,sans-serif;letter-spacing:.2em;text-transform:uppercase}
.claim{padding:clamp(4.5rem,11vw,9rem) clamp(1.2rem,8vw,9rem)}
.claim h2{font-size:clamp(2.6rem,6.6vw,5.6rem);max-width:16ch;margin-bottom:1.6rem}
.claim p{max-width:36rem;font-size:1.1rem;margin:0}
.book{display:grid;grid-template-columns:1fr 1fr;align-items:center}
.book figure{margin:0}.book img{width:100%;aspect-ratio:4/3;object-fit:cover}
.book div{padding:clamp(2rem,6vw,5.5rem)}
.book h2{font-size:clamp(2.2rem,4.6vw,3.8rem);margin-bottom:1.2rem}
.book p{margin:0 0 2rem}
@media (max-width:820px){.hero,.ways,.book{grid-template-columns:1fr}.hero figure{height:56svh;order:-1}}
"""
    body = """
<section class="hero olive"><div class="hero-text"><div class="eyebrow">%(eyebrow)s</div><h1>%(h1)s</h1>
  <p>%(stand)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></div><figure>%(hero)s</figure></section>
<p class="line">%(line)s</p>
<section class="ways">%(ways)s</section>
<section class="claim olive"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="book"><figure>%(aerial)s</figure><div><h2>%(book_h)s</h2><p>%(book)s</p>
  <a class="btn dark" href="%(cta_href)s">%(cta)s</a></div></section>
""" % dict(C, hero=im("copy-of-thevalley-6-1", "A couple in the meadow", eager=True, sizes="(max-width:820px) 100vw, 50vw"),
           aerial=im(AERIAL, "The estate from the air", sizes="(max-width:820px) 100vw, 50vw"),
           ways=ways_items('<article class="way">%(photo)s<div><h3>%(name)s</h3><p>%(text)s</p>'
                           '<a href="%(href)s">Discover</a></div></article>'))
    return css, head_bar() + body


# ---------------------------------------------------------------------- 10
@direction("10", "Mosaic",
           "The type is the architecture: the headline runs the full width of the page, huge, over a "
           "tiled mosaic of real weddings. The owner's orange appears once, as a single thread.",
           "Newsreader:ital,opsz,wght@0,6..72,300;1,6..72,300&family=Instrument+Sans:wght@400;500")
def d10():
    css = """
body{font:400 16px/1.7 'Instrument Sans',sans-serif;background:#fff}
.lw-head{background:#fff}
.lw-mark{font:italic 300 1.45rem/1 Newsreader,serif}
.lw-nav a,.lw-cta{font-size:.8rem}.lw-cta{font-weight:500;border-bottom:2px solid #FC5324;padding-bottom:.2rem}
h1,h2,h3{font-family:Newsreader,serif;font-weight:300;margin:0;line-height:.95;letter-spacing:-.02em}
.mast{padding:clamp(1.5rem,4vw,3rem) clamp(1.2rem,3vw,2.5rem) 0}
.mast h1{font-size:clamp(3.4rem,12.6vw,13rem)}
.mast h1 em{font-style:italic}
.mast-row{display:grid;grid-template-columns:1fr 1fr;gap:2rem;align-items:end;margin:clamp(1.4rem,3vw,2.4rem) 0 clamp(1.4rem,3vw,2.4rem)}
.mast-row p{margin:0;max-width:30rem;font-size:1.08rem}
.thread{height:2px;background:#FC5324;width:clamp(4rem,12vw,9rem);margin-bottom:1rem}
.btn{justify-self:end;text-decoration:none;background:#2B1B00;color:#fff;padding:1.1rem 1.8rem;font-weight:500;font-size:.9rem}
.btn:hover{background:#7B7951}
.mosaic{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:clamp(7rem,15vw,15rem);gap:4px;padding:0 4px}
.mosaic figure{margin:0;overflow:hidden}.mosaic img{width:100%;height:100%;object-fit:cover;transition:transform 1.2s ease}
.mosaic figure:hover img{transform:scale(1.04)}
.m1{grid-column:1/4;grid-row:span 3}.m2{grid-column:4/6;grid-row:span 2}.m3{grid-column:6/7;grid-row:span 2}
.m4{grid-column:4/5;grid-row:span 1}.m5{grid-column:5/7;grid-row:span 1}
.line{font:italic 300 clamp(2rem,5vw,4.2rem)/1.08 Newsreader,serif;padding:clamp(4rem,10vw,8rem) clamp(1.2rem,3vw,2.5rem);max-width:62rem}
.ways{border-top:1px solid #2B1B00}
.way{display:grid;grid-template-columns:1.2fr 2fr 1.4fr auto;gap:clamp(1rem,3vw,2.5rem);align-items:center;
  padding:1.4rem clamp(1.2rem,3vw,2.5rem);border-bottom:1px solid #2B1B00;text-decoration:none;transition:background .3s}
.way:hover{background:#FFF9F3}
.way img{width:100%;aspect-ratio:3/2;object-fit:cover}
.way h3{font-size:clamp(1.8rem,3.4vw,3rem)}
.way p{margin:0}
.way span{font-size:1.4rem}
.claim{display:grid;grid-template-columns:1fr 1fr;gap:clamp(2rem,6vw,5rem);padding:clamp(4rem,10vw,8rem) clamp(1.2rem,3vw,2.5rem);background:#FFF9F3}
.claim h2{font-size:clamp(2.6rem,6vw,5.4rem)}
.claim p{align-self:end;margin:0;font-size:1.1rem}
.book{padding:clamp(4rem,10vw,8rem) clamp(1.2rem,3vw,2.5rem)}
.book h2{font-size:clamp(2.4rem,6.4vw,6rem);max-width:15ch;margin-bottom:1.6rem}
.book p{max-width:30rem;margin:0 0 2rem}
@media (max-width:820px){.mast-row,.claim{grid-template-columns:1fr}.btn{justify-self:start}
  .mosaic{grid-template-columns:repeat(2,1fr);grid-auto-rows:9rem}.m1{grid-column:1/3;grid-row:span 2}
  .m2,.m3,.m4,.m5{grid-column:auto;grid-row:span 1}
  .way{grid-template-columns:1fr;gap:.6rem}.way span{display:none}}
"""
    tiles = [("m1", HERO_WIDE, HERO_ALT), ("m2", "copy-of-3i0a4529vh", "A couple on the Lookout Deck"),
             ("m3", "copy-of-thevalley", "A couple between floral arches"), ("m4", "copy-of-the-valley-venues-kristen-thomison-photo-63", "A table dressed in blue"),
             ("m5", AERIAL, "The estate from the air")]
    mosaic = "".join('<figure class="%s">%s</figure>' % (c, im(k, a, eager=True, sizes="50vw")) for c, k, a in tiles)
    body = """
<section class="mast"><h1>More than a <em>wedding</em> day.</h1>
  <div class="mast-row"><div><div class="thread"></div><p>%(stand)s</p></div><a class="btn" href="%(cta_href)s">%(cta)s</a></div></section>
<section class="mosaic">%(mosaic)s</section>
<p class="line">%(line)s</p>
<section class="ways">%(ways)s</section>
<section class="claim"><h2>%(claim_h)s</h2><p>%(claim)s</p></section>
<section class="book"><h2>%(book_h)s</h2><p>%(book)s</p><a class="btn" href="%(cta_href)s">%(cta)s</a></section>
""" % dict(C, mosaic=mosaic,
           ways=ways_items('<a class="way" href="%(href)s">%(photo)s<h3>%(name)s</h3><p>%(text)s</p><span aria-hidden="true">&rarr;</span></a>',
                           sizes="(max-width:820px) 100vw, 22vw"))
    return css, head_bar() + body


# ===================================================================== write
INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<title>The Weddings page, ten ways &middot; The Valley Venues</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@400;500&display=swap">
<style>
*{box-sizing:border-box}html,body{margin:0}img{display:block;max-width:100%;height:auto}
body{background:__PARCH__;color:__INK__;font:400 17px/1.7 Jost,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid __ACCENT__;outline-offset:4px}
.wrap{max-width:86rem;margin:0 auto;padding:clamp(2.5rem,7vw,6rem) clamp(1.2rem,4vw,3.5rem) clamp(4rem,9vw,7rem)}
.lede{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:clamp(1.5rem,5vw,5rem);align-items:end;
  padding-bottom:clamp(2rem,5vw,3.5rem);border-bottom:1px solid __OLIVE__}
.eyebrow{font-size:.72rem;letter-spacing:.3em;text-transform:uppercase;color:__OLIVE__;margin:0 0 1.2rem}
h1{font-family:'Cormorant Garamond',serif;font-weight:300;font-size:clamp(2.8rem,7vw,6rem);line-height:.98;margin:0}
h1 em{font-style:italic}
.lede p{margin:0 0 1rem;max-width:34rem}
.chips{display:flex;gap:.4rem;margin-top:1.4rem}
.chips span{width:2.2rem;height:2.2rem;border:1px solid __OLIVE__}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(1.8rem,4vw,3.5rem);margin-top:clamp(2.5rem,6vw,4.5rem)}
.pick{display:block}
.pick-shot{display:block;overflow:hidden;background:__CREAM__;border:1px solid __OLIVE__}
.pick-shot img{width:100%;transition:scale 1.4s cubic-bezier(.16,1,.3,1)}
.pick:hover .pick-shot img,.pick:focus-visible .pick-shot img{scale:1.04}
.pick-line{display:flex;align-items:baseline;gap:1rem;margin:1.1rem 0 .3rem;
  border-bottom:1px solid __OLIVE__;padding-bottom:.7rem;position:relative}
.pick-line::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:__ACCENT__;
  transform:scaleX(0);transform-origin:left;transition:transform .6s cubic-bezier(.16,1,.3,1)}
.pick:hover .pick-line::after,.pick:focus-visible .pick-line::after{transform:scaleX(1)}
.pick-line b{font:500 .72rem/1 Jost,sans-serif;letter-spacing:.22em;color:__OLIVE__}
.pick-line em{font:400 clamp(1.5rem,2.6vw,2.2rem)/1 'Cormorant Garamond',serif;font-style:normal;margin-right:auto}
.pick-idea{display:block;font-size:.98rem;max-width:44rem}
.foot{margin-top:clamp(3rem,7vw,5rem);padding-top:1.4rem;border-top:1px solid __OLIVE__;
  display:flex;flex-wrap:wrap;gap:.6rem 2rem;font-size:.92rem}
.foot a{border-bottom:1px solid __OLIVE__;padding-bottom:.15rem}
@media (max-width:860px){.lede{grid-template-columns:minmax(0,1fr)}.grid{grid-template-columns:minmax(0,1fr)}}
</style></head>
<body><div class="wrap">
<div class="lede">
  <div><p class="eyebrow">The Valley Venues &middot; for Kobi</p>
    <h1>The Weddings page,<br><em>ten ways</em>.</h1></div>
  <div><p>The same words and the same photographs, designed %(n)s ways. Every one is in your
    colours, with nothing rounded, and every one is built for a phone first.</p>
    <p>Open any of them and scroll. Pick the one that feels like the estate, or the parts you
      want from several, and the rest of the site follows it.</p>
    <div class="chips">%(chips)s</div></div>
</div>
<div class="grid">%(cards)s</div>
<div class="foot">
  <span>Nothing here is linked from the site, and none of it is indexed.</span>
  <a href="/weddings/">See the current Weddings page</a>
  <a href="/gallery/">The gallery</a>
</div>
</div></body></html>
"""


def index_page(cards, chips, n):
    out = INDEX
    for token, value in (("__PARCH__", PARCH), ("__INK__", INK), ("__OLIVE__", OLIVE),
                         ("__ACCENT__", ACCENT), ("__CREAM__", "#FFF7F0"),
                         ("%(cards)s", cards), ("%(chips)s", chips), ("%(n)s", str(n))):
        out = out.replace(token, value)
    return out


SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<title>%(n)s %(name)s &middot; Weddings, ten ways</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=%(fonts)s&display=swap">
<link rel="stylesheet" href="/wedding-lab/motion.css?v=%(mv)s">
<style>%(base)s%(css)s</style></head>
<body data-dir="%(n)s">
%(body)s
<nav class="lab-switch" aria-label="Directions">%(switch)s</nav>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
<script src="/wedding-lab/motion.js?v=%(mv)s"></script>
</body></html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    import hashlib, shutil
    here = os.path.dirname(os.path.abspath(__file__))
    mv = ""
    for src, dst in (("wedding_lab_motion.js", "motion.js"), ("wedding_lab_motion.css", "motion.css")):
        shutil.copyfile(os.path.join(here, src), os.path.join(OUT, dst))
        mv += hashlib.md5(open(os.path.join(here, src), "rb").read()).hexdigest()[:4]
    for d in D:
        css, body = d["fn"]()
        switch = '<a href="/wedding-lab/">All</a>' + "".join(
            '<a href="/wedding-lab/%s/"%s>%s %s</a>' % (x["slug"], ' aria-current="page"' if x is d else "", x["slug"], x["name"])
            for x in D)
        path = os.path.join(OUT, d["slug"])
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as f:
            f.write(SHELL % dict(n=d["slug"], name=d["name"], fonts=d["fonts"], base=BASE_CSS, css=css, body=body, switch=switch, mv=mv))
        print("  /wedding-lab/%s/  %s" % (d["slug"], d["name"]))
    cards = "".join(
        '''<a class="pick" href="/wedding-lab/%(slug)s/">
      <span class="pick-shot"><img src="/wedding-lab/thumbs/%(slug)s.webp" alt="" width="900" height="525" loading="%(load)s" decoding="async"></span>
      <span class="pick-line"><b>%(slug)s</b><em>%(name)s</em></span>
      <span class="pick-idea">%(idea)s</span>
    </a>''' % dict(d, load="eager" if i < 2 else "lazy") for i, d in enumerate(D))
    chips = "".join('<span style="background:%s"></span>' % c for c in (INK, PARCH, OLIVE, ACCENT))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(cards, chips, len(D)))
    print("  /wedding-lab/")


if __name__ == "__main__":
    main()
