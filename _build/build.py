"""
Build the prototype site.

Eleven pages share one header, one footer and one stylesheet. Writing them by
hand would mean changing the navigation in eleven places the first time it
moves, and it will move — the structure is a proposal, not a decision. So the
pages are data and the shell is code.

Run:  python _build/build.py
"""
import os, re, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")


def json_str(value):
    """A JavaScript string literal that cannot end the script element early."""
    return ('"' + str(value).replace("\\", "\\\\").replace('"', '\\"')
            .replace("<", "\\x3c") + '"')


def webp_size(path):
    """Width and height of a WebP, without a dependency.

    Every img on this site carries width and height attributes so the page
    reserves the right space before the bytes arrive. Typing those by hand is
    how they end up wrong, and a wrong height is not a cosmetic problem: the
    attributes set a presentational height, and a presentational height
    silently defeats aspect-ratio. Three separate bugs on this site had that
    one cause. So the numbers are read from the file instead.
    """
    with open(path, "rb") as f:
        head = f.read(30)
    fmt = head[12:16]
    if fmt == b"VP8X":
        w = struct.unpack("<I", head[24:27] + b"\0")[0] + 1
        h = struct.unpack("<I", head[27:30] + b"\0")[0] + 1
        return w, h
    if fmt == b"VP8L":
        b = struct.unpack("<I", head[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if fmt == b"VP8 ":
        w, h = struct.unpack("<HH", head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    raise ValueError("not a webp: %s" % path)


_IMG = re.compile(r"\{\{img:([^|}]+)\|([^|}]*)\|?([^}]*)\}\}")
_INLINE = re.compile(r"\{\{inline:([^}]+)\}\}")


def expand(body):
    """Turn {{img:file.webp|alt text|extra attributes}} into a real img tag."""
    def one(m):
        name, alt, extra = m.group(1), m.group(2), m.group(3)
        w, h = webp_size(os.path.join(IMG, name))
        return ('<img src="%sassets/img/%s" alt="%s" width="%d" '
                'height="%d" loading="lazy" decoding="async"%s>'
                % (URL_ROOT, name, alt, w, h, (" " + extra) if extra else ""))
    body = _IMG.sub(one, body)

    # {{inline:plan.svg}} drops a generated asset straight into the markup.
    # The plan has to be inline: CSS animates individual marks and legs inside
    # it, and nothing reaches inside an <img>.
    def inline(m):
        path = os.path.join(ROOT, "assets", m.group(1).strip())
        return open(path, encoding="utf-8").read().strip()
    return _INLINE.sub(inline, body)

SITE = "The Valley Venues"

# Where the site lives. ROOT is the path every internal link is written against
# and BASE is the absolute origin the og: tags need; nothing else in this file
# or in any stylesheet knows the site's address.
#
# The site sits at a domain root now, which is why URL_ROOT is "/". It spent its
# first weeks as a folder inside the agency site at "/", and when
# thevalleyvenues.com is pointed here the only change is BASE.
# The opening band, above the hero on every page until it takes itself down.
OPENING = '\n<aside class="opening" id="opening" data-until="2026-09-13T20:00:00Z"\n       data-through="2026-09-13T23:00:00Z">\n  <div class="opening-inner">\n    <div class="opening-what">\n      <span class="eyebrow">Grand opening</span>\n      <p><b>Magnolia House</b> opens Sunday 13 September, 4&ndash;7pm EDT</p>\n      <p class="opening-with">Free food and drink &middot; Live music &middot; Estate tours</p>\n    </div>\n    <p class="opening-count" aria-hidden="true"></p>\n  </div>\n</aside>\n'

URL_ROOT = "/"
BASE = "https://thevalley.sparkmedia.ai/"

# Where the inquiry forms post: GoHighLevel, straight from the browser.
#
# This is a decision taken against the CRM spec's own advice, which says to
# post server side because the URL is the endpoint's only authentication and
# GHL bills Inbound Webhook per execution. Client-side was chosen anyway, and
# the URL not rotated, so two things follow.
#
#   It is public. Not only in page source -- this repo is public too, so it is
#   in GitHub where secret scrapers look first.
#   The honeypot in assets/forms.js is the only thing between a scraper and
#   the invoice. Do not remove it.
#
# Verified 10 Sep 2026: the endpoint answers a CORS preflight with
# Access-Control-Allow-Origin: *, so the browser allows this in normal cors
# mode and the response can be read -- which is what lets a failed post show
# the visitor an email address instead of losing what they wrote.
FORM_ENDPOINT = ("https://services.leadconnectorhq.com/hooks/"
                 "oDcqfZdwDgTOXwK0GS98/webhook-trigger/"
                 "53fd0129-80af-4311-bfb2-e0955fb2ebe0")
TAGLINE = "One Private Mountain Estate. All for You."

# Primary navigation. Five destinations and one invitation — the Venues
# dropdown is deliberately absent; it is what made the estate read as four
# separate places.
NAV = [
    ("The Difference", "/the-difference/"),
    ("Weddings", "/weddings/"),
    ("Stay", "/stay/"),
    ("The Estate", "/the-estate/"),
    ("Planners", "/planners/"),
    ("About", "/about/"),
]
CTA = ("Speak with us", "/inquire/")

FOOTER = [
    ("Celebrate", [
        ("The Difference", "/the-difference/"),
        ("The Estate Weekend", "/weddings/"),
        ("What's Included", "/weddings/whats-included/"),
        ("Real Weddings", "/weddings/real-weddings/"),
        ("Single-Day Celebrations", "/weddings/single-day/"),
    ]),
    ("Stay", [
        ("Lodging on the Estate", "/stay/"),
    ]),
    ("The Estate", [
        ("The whole property", "/the-estate/"),
        ("Magnolia House", "/the-estate/magnolia-house/"),
        ("The Valley", "/the-estate/the-valley/"),
        ("Lookout Deck", "/the-estate/lookout-deck/"),
        ("Davis Hall", "/the-estate/davis-hall/"),
        ("Overlook Village", "/the-estate/overlook-village/"),
    ]),
    ("Trade", [
        ("For Planners", "/planners/"),
        ("Register as a Planner", "/planners/register/"),
    ]),
    ("The Valley Venues", [
        ("About &amp; Kobi", "/about/"),
        ("Speak with our team", "/inquire/"),
    ]),
]


def shell(page, path="index.html"):
    """Wrap one page's body in the site chrome."""
    depth_root = URL_ROOT
    url = BASE + (path[:-len("index.html")] if path.endswith("index.html") else path)
    nav = "\n".join(
        '        <li><a href="%s"%s>%s</a></li>'
        % (href, ' aria-current="page"' if page["nav"] == label else "", label)
        for label, href in NAV)

    foot = "\n".join(
        '        <div>\n          <h3>%s</h3>\n          <ul>%s</ul>\n        </div>'
        % (head, "".join('\n            <li><a href="%s">%s</a></li>' % (h, t)
                         for t, h in links) + "\n          ")
        for head, links in FOOTER)

    # Two kinds of hero, and both put the words on the photograph. The home
    # page brings its own markup because its hero is a clock; every other page
    # gets one frame and the shared scrim over it.
    hero, hero_class = page.get("hero_html", ""), "hero-clock"
    if not hero and page.get("hero_img"):
        w, h = webp_size(os.path.join(IMG, page["hero_img"]))
        hero_class = "hero-photo"
        hero = ('  <img class="hero-bg" src="%sassets/img/%s" alt="%s" '
                'width="%d" height="%d" fetchpriority="high" decoding="async">\n'
                % (depth_root, page["hero_img"], page["hero_alt"], w, h))
    elif not hero:
        hero_class = ""
    actions = ""
    if page.get("actions"):
        actions = '\n    <div class="hero-actions">%s</div>' % "".join(
            '\n      <a class="btn%s" href="%s">%s</a>' % (
                " btn-solid" if i == 0 else "", h, t)
            for i, (t, h) in enumerate(page["actions"])) + "\n    "

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" href="%(root)sassets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%(root)sassets/icon-180.png">
<meta name="theme-color" content="#34372F">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%(site)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(base)sassets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The ceremony aisle set out in the meadow beneath Lookout Mountain">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Libre+Franklin:wght@400;500;600&display=swap">
<link rel="stylesheet" href="%(root)sassets/site.css">
<link rel="stylesheet" href="%(root)sassets/motion.css">
<link rel="stylesheet" href="%(root)sassets/opening.css">
<link rel="stylesheet" href="%(root)sassets/forms.css">
%(head)s<script>document.documentElement.classList.add("js");if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches){document.documentElement.classList.add("io");setTimeout(function(){if(!window.__reveal)document.documentElement.classList.remove("io")},3000)}window.FORM_ENDPOINT=%(endpoint)s;if(/[?&]notes\b/.test(location.search))document.documentElement.classList.add("notes")</script>
</head>
<body>

<a class="skip" href="#main">Skip to content</a>

<header class="site-head">
  <div class="inner">
    <a class="wordmark" href="%(root)s"><img src="%(root)sassets/logo-mark.webp" alt="" width="240" height="240" decoding="async"><span>%(site)s</span></a>
    <nav class="site-nav" aria-label="Primary">
      <ul>
%(nav)s
      </ul>
    </nav>
    <a class="btn btn-solid" href="%(cta_href)s">%(cta_text)s</a>
  </div>
</header>
%(banner)s
<header class="hero %(hero_class)s">
%(hero)s  <div class="hero-body">
    <div class="eyebrow">%(eyebrow)s</div>
    <h1>%(h1)s</h1>
    <p>%(standfirst)s</p>%(actions)s
  </div>
</header>

<main id="main">
%(body)s
</main>

<footer class="site-foot">
  <a class="foot-mark" href="%(root)s" aria-label="%(site)s, home">
    <img src="%(root)sassets/logo.webp" alt="" width="460" height="304"
         loading="lazy" decoding="async">
  </a>
  <div class="inner">
%(foot)s
    <div>
      <h3>Visit</h3>
      <address class="addr">
        1860 Pope Creek Rd<br>Wildwood, Georgia<br>
        Fifteen minutes from downtown Chattanooga
      </address>
    </div>
  </div>
  <div class="colophon">
    <span>Prototype for The Valley Venues. Photography is existing estate imagery.</span>
    <a class="notes-on" href="?notes">Show working notes</a>
    <a class="notes-off" href="?">Hide working notes</a>
  </div>
</footer>
%(foot_js)s
<script src="%(root)sassets/reveal.js" defer></script>
<script src="%(root)sassets/opening.js" defer></script>
<script src="%(root)sassets/forms.js" defer></script>
</body>
</html>
""" % {
        "title": page["title"], "desc": page["desc"], "root": depth_root,
        "url": url, "base": BASE,
        "endpoint": json_str(FORM_ENDPOINT),
        "site": SITE, "nav": nav, "cta_href": CTA[1], "cta_text": CTA[0],
        "hero": hero, "eyebrow": page["eyebrow"], "h1": page["h1"],
        "standfirst": page["standfirst"], "actions": actions,
        "body": expand(page["body"]), "foot": foot,
        "hero_class": hero_class,
        "banner": page.get("banner", OPENING),
        "head": page.get("head", ""), "foot_js": page.get("foot_js", ""),
    }


# ---------------------------------------------------------------- the pages
PAGES = {}

PAGES["index.html"] = dict(
    nav=None, title="%s | %s" % (SITE, TAGLINE), desc=TAGLINE,
    head=         '<link rel="stylesheet" href="/assets/home.css">\n'
         '<link rel="preload" as="image" href="/assets/img/hero-1.webp"\n'
         '      imagesrcset="/assets/img/hero-1-sm.webp 1100w, /assets/img/hero-1.webp 2200w"\n'
         '      imagesizes="100vw">\n',
    foot_js='<script src="/assets/home.js" defer></script>',
    hero_html='  <div class="hero-stage">\n    <figure class="slide is-on" data-moment="The arrival"><img src="/assets/img/hero-1.webp" srcset="/assets/img/hero-1-sm.webp 1100w, /assets/img/hero-1.webp 2200w" sizes="100vw" alt="Magnolia House, white columns above the lawn" width="2200" height="1100" fetchpriority="high" decoding="async"></figure>\n    <figure class="slide" data-moment="The morning"><img data-src="/assets/img/hero-2.webp" data-srcset="/assets/img/hero-2-sm.webp 1100w, /assets/img/hero-2.webp 2200w" sizes="100vw" alt="A groom having his bow tie straightened, both of them laughing" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="The meadow, set"><img data-src="/assets/img/hero-3.webp" data-srcset="/assets/img/hero-3-sm.webp 1100w, /assets/img/hero-3.webp 2200w" sizes="100vw" alt="The ceremony aisle set out, the ridge behind it" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="Golden hour"><img data-src="/assets/img/hero-4.webp" data-srcset="/assets/img/hero-4-sm.webp 1100w, /assets/img/hero-4.webp 2200w" sizes="100vw" alt="A couple in the meadow as the light goes" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="After dark"><img data-src="/assets/img/hero-5.webp" data-srcset="/assets/img/hero-5-sm.webp 1100w, /assets/img/hero-5.webp 2200w" sizes="100vw" alt="The conservatory at Magnolia House, lit for dinner" width="2200" height="1100" decoding="async"></figure>\n    <div class="hero-marks">\n      <button type="button" class="hero-step" data-step="-1" aria-label="Previous moment"><svg viewBox="0 0 12 20" aria-hidden="true" focusable="false"><path d="M9 1 2 10 9 19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>\n      <p class="hero-hour"><span>The arrival</span></p>\n      <div class="hero-dots" role="group" aria-label="Choose a moment">\n        <button type="button" aria-current="true"><span class="skip">The arrival</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">The morning</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">The meadow, set</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">Golden hour</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">After dark</span><i></i></button>\n      </div>\n      <button type="button" class="hero-step" data-step="1" aria-label="Next moment"><svg viewBox="0 0 12 20" aria-hidden="true" focusable="false"><path d="M3 1 10 10 3 19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>\n    </div>\n  </div>\n',
    eyebrow="Wildwood, Georgia &middot; Fifteen minutes from downtown Chattanooga",
    h1="One Private Mountain Estate. All for You.",
    standfirst="Seventy-four private acres beneath Lookout Mountain, fifteen minutes from "
               "downtown Chattanooga. One wedding at a time, ever. For your two days the gate closes "
               "behind one family, and every field, every porch and every bed is yours.",
    actions=[("Speak with our team", "/inquire/"),
             ("Walk the Estate", "/the-estate/")],
    body="""
<section>
 <div class="stakes">
  <div class="lede reveal">
    <div class="eyebrow">Why any of this matters</div>
    <h2>This is one of the best days of your life.</h2>
    <p>It is also one of the only times in a life when nearly everyone you love is in one
       place. Parents and grandparents. Childhood friends and college friends. Brothers and
       sisters. People who moved across the country and have not been in the same room in
       years.</p>
    <p>Most venues compress all of that into a handful of scheduled hours &mdash; arrive,
       ceremony, cocktail hour, reception, leave. Everything below follows from thinking
       that is the wrong way round.</p>
  </div>
  <div class="cluster">
    <figure class="cl-1"><img src="/assets/img/note-1.webp"
      alt="The wedding party throwing petals over the couple" width="900" height="1200"
      loading="lazy" decoding="async"></figure>
    <figure class="cl-2"><img src="/assets/img/note-2.webp"
      alt="A hand resting on a shoulder before the ceremony" width="900" height="1200"
      loading="lazy" decoding="async"></figure>
    <figure class="cl-3"><img src="/assets/img/note-3.webp"
      alt="The couple holding each other in the meadow" width="900" height="1200"
      loading="lazy" decoding="async"></figure>
  </div>
 </div>
</section>

<section class="claim">
  {{img:band-estate.webp|The estate from above, two people alone in the meadow|class="claim-img"}}
  <div class="claim-fade" aria-hidden="true"></div>
  <div class="claim-body">
    <div class="eyebrow">What makes this different</div>
    <h2 class="rise-words"><span>One</span> <span>estate.</span> <span>One</span> <span>couple.</span> <span>One</span> <span>weekend.</span></h2>
    <p>Larger estates in this region run two and sometimes three weddings on a
       single Saturday. It is how the acreage pays for itself &mdash; and it means
       another bride is on the property, another family&rsquo;s flowers are going out
       the far door, and another cocktail hour is audible from the ceremony.
       Someone else&rsquo;s arch is coming down while yours goes up.</p>
    <ul class="nots">
      <li>No second wedding on the property</li>
      <li>Nothing flipped or reset around you</li>
      <li>Nothing shared, overheard, or hurried</li>
      <li>Every gate, every field, every bed</li>
    </ul>
    <p class="close">For two days, the only people on seventy&#8209;four acres are
       the ones you invited.</p>
    <a class="btn" href="/the-difference/">Why that changes everything</a>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The weekend</div>
    <h2>More than a wedding day.</h2>
    <p>The ceremony takes thirty minutes. Most venues sell those thirty minutes and the
       eight hours around them. This estate sells the two days you live inside.</p>
  </div>
  <ol class="weekend">
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-fri.webp" alt="Groomsmen in the clubhouse, late" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Arriving</span>
      <b>You arrive once</b>
      <p>Through the gate, and for the next two days this is simply where you are. The
         rehearsal happens where the vows will, and nobody goes back to a hotel.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-dawn.webp" alt="A suite on the estate in the morning" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">The morning</span>
      <b>Sunrise comes with the room</b>
      <p>Light comes up over Lookout Mountain and fills the room you are already standing
         in. Hair can start at five. There is no commute in a wedding dress.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-gold.webp" alt="A couple dancing on the deck as the light goes" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Golden hour</span>
      <b>The mountain turns gold</b>
      <p>Guests walk from the ceremony to the overlook. Nobody drives, nobody follows
         directions, and nobody starts looking for their keys at eleven.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-sun.webp" alt="The cottages on the hill at dusk" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">The morning after</span>
      <b>Goodnight instead of goodbye</b>
      <p>Two nights means three mornings, and the last thing you do together is breakfast
         rather than a parking lot.</p>
    </li>
  </ol>
</section>

<section>
  <div class="lede reveal">
    <div class="eyebrow">Everyone stays</div>
    <h2>Nobody drives home.</h2>
    <p>Cottages, suites and lodges spread across the property, each with a name rather
       than a number. Your family is not at a hotel by the interstate; they are up the
       hill, and they come down for breakfast.</p>
  </div>
  <div class="names" aria-hidden="true">
    <div class="names-track"><span>Phoenix</span><span>Bluebird</span><span>Goldfinch</span><span>Hummingbird</span><span>Willow</span><span>Mahogany</span><span>Overlook Village</span><span>The Lodge</span><span>Lost in the Woods</span><span>Phoenix</span><span>Bluebird</span><span>Goldfinch</span><span>Hummingbird</span><span>Willow</span><span>Mahogany</span><span>Overlook Village</span><span>The Lodge</span><span>Lost in the Woods</span></div>
  </div>
  <p class="skip">Phoenix, Bluebird, Goldfinch, Hummingbird, Willow, Mahogany,
     Overlook Village, The Lodge, and Lost in the Woods.</p>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">Two ways to be here</div>
    <h2>Celebrate, or simply stay.</h2>
  </div>
  <div class="grid">
    <article class="card card-door reveal">
      <figure class="frame">{{img:weddings.webp|A ceremony under way in the meadow|class="wipe"}}</figure>
      <div class="eyebrow">Celebrate</div>
      <h3>The Estate Weekend</h3>
      <p>Friday afternoon to Sunday morning, the property held for one couple.</p>
      <a class="btn" href="/weddings/">Weddings</a>
    </article>
    <article class="card card-door reveal">
      <figure class="frame">{{img:stay.webp|A cottage in the woods|class="wipe"}}</figure>
      <div class="eyebrow">Stay</div>
      <h3>Lodging on the estate</h3>
      <p>Cottages facing the ridge, open when there is no wedding on the property.</p>
      <a class="btn" href="/stay/">Stay</a>
    </article>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A cottage in the woods, lit at night"
       style="background-image:url('/assets/img/close-woods.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">And then</div>
    <h2>You disappear, without leaving.</h2>
    <p>A cottage in the woods at the far edge of the property, a short ride from the music.
       Married, alone, and thirty seconds from everyone you love.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["weddings/index.html"] = dict(
    nav="Weddings", title="Weddings | %s" % SITE,
    desc="The Estate Weekend at The Valley Venues.",
    hero_img="weddings.webp", hero_alt="A ceremony under way in the meadow, guests seated toward the ridge",
    eyebrow="Celebrate",
    h1="More Than a Wedding Day",
    standfirst="There will be a ceremony. There will be dinner. There will be dancing. "
               "And then there is everything around it.",
    actions=[("Speak with our team", "/inquire/"),
             ("What's Included", "/weddings/whats-included/")],
    body="""
<section>
  <div class="lede">
    <h2>The Estate Weekend</h2>
    <p>The night before, when your friends are still up at one in the morning. Sunrise over
       Lookout Mountain through the window of the room where you are already getting ready.
       Breakfast with your grandparents before anyone drives anywhere.</p>
    <p>The ceremony takes thirty minutes. The weekend is what you will remember.</p>
  </div>
  <div class="grid">
    <article class="card">
      {{img:w-weekend.webp|A ceremony under way in the meadow, the congregation seated|class="wipe"}}
      <div class="eyebrow">Hero experience</div>
      <h3>The Estate Weekend</h3>
      <p>Two nights, the whole property, one couple. Wedding, lodging, time and privacy
         as a single thing rather than four invoices.</p>
    </article>
    <article class="card">
      {{img:w-premium.webp|Bridesmaids beside tall floral arrangements at golden hour|class="wipe"}}
      <div class="eyebrow">Premium</div>
      <h3>All-Inclusive Estate Experience</h3>
      <p>Adds deeper design, planning, food, beverage, coordination and vendor support &mdash;
         and Kobi's own hand in the design.</p>
    </article>
    <article class="card">
      {{img:w-single.webp|The ceremony set out and waiting, seen through the tall grass|class="wipe"}}
      <div class="eyebrow">Alternate</div>
      <h3>Single-Day Celebration</h3>
      <p>A real offering for couples who want the day rather than the weekend.
         <a href="/weddings/single-day/">See single-day celebrations</a>.</p>
    </article>
  </div>
</section>

<section class="band">
  {{img:band-vows.webp|The meadow with the arch standing in it, and nothing else|class="band-img"}}
  <p>Nobody else&rsquo;s arch comes down while yours goes up.</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">What you are actually booking</div>
    <h2 class="rise-words"><span>You</span> <span>are</span> <span>not</span> <span>renting</span> <span>a</span> <span>room.</span> <span>You</span> <span>are</span> <span>moving</span> <span>in</span> <span>for</span> <span>the</span> <span>weekend.</span></h2>
    <p>A venue sells you a room and a window of hours. Everything in that model
       follows from the room having to be used again. The doors open at four
       because they were being reset until three, and they close at eleven
       because somebody has to be in at seven.</p>
    <p class="close">Here the property is not being reset around you, because
       there is nothing to reset it for. You arrive on Friday and you leave on
       Sunday, and in between the gate is closed behind one family.</p>
  </div>
</section>

<section>
  <div class="stakes flip">
    <div class="lede">
      <div class="eyebrow">The hours nobody schedules</div>
      <h2>Most of the weekend is not on the timeline.</h2>
      <p>A wedding timeline covers about eight hours. What couples describe to us
         afterwards is almost never in them: the friends still up at one in the
         morning, the half hour before anyone else is awake, the long breakfast on
         Sunday that nobody had to drive to.</p>
      <p>Those hours exist here because there is nowhere else anybody has to be.
         That is the whole of what the second night buys.</p>
      <a class="btn" href="/stay/">Where everyone sleeps</a>
    </div>
    <div class="cluster">
      <figure class="cl-1">{{img:w-night.webp|Two friends in a getting ready suite the night before, laughing}}</figure>
      <figure class="cl-2">{{img:w-morning.webp|The bride in a robe in the quiet of the morning}}</figure>
      <figure class="cl-3">{{img:w-after.webp|A table laid on the porch of a cottage the morning after}}</figure>
    </div>
  </div>
</section>

<section id="investment">
  <div class="lede">
    <div class="eyebrow">Investment</div>
    <h2>One figure, and a conversation.</h2>
    <p>There is one starting figure for an Estate Weekend, and you will have it in
       the first reply. There is no menu of options and no price list to download,
       because what actually fits depends on your date, your count and how you want
       the weekend to feel.</p>
    <p>Tell us those three things and what comes back is a recommendation, not a
       brochure.</p>
    <a class="btn btn-solid" href="/inquire/">Start there</a>
  </div>
  <div class="note">
    <p><b>Prototype note.</b> The published starting figure is one of the decisions still
       open. The framework recommends a single number with nothing beside it &mdash; the
       absence of everything else is what produces the inquiry.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The conservatory lit from within after dark"
       style="background-image:url('/assets/img/close-weddings.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">One weekend at a time</div>
    <h2>Most Saturdays are already spoken for.</h2>
    <p>The estate holds one wedding at a time, which means the calendar is shorter than it looks. Walking the property is how most couples decide, and it costs nothing but an afternoon.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["weddings/whats-included/index.html"] = dict(
    nav="Weddings", title="What's Included | %s" % SITE,
    desc="What comes with the estate, and what happens when the weather turns.",
    hero_img="included.webp", hero_alt="The conservatory at Magnolia House, glass on three sides",
    eyebrow="Celebrate &middot; What's included",
    h1="Fewer separate decisions.",
    standfirst="The questions a mother asks: what is included, where does everyone sleep, "
               "what happens if it rains, and who is responsible for what.",
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">The short version</div>
    <h2 class="rise-words"><span>The</span> <span>list</span> <span>of</span> <span>things</span> <span>you</span> <span>still</span> <span>have</span> <span>to</span> <span>arrange</span> <span>is</span> <span>the</span> <span>short</span> <span>one.</span></h2>
    <p>Most of what a wedding costs is not the wedding. It is the coordination
       of eleven separate companies who have never worked together, each with
       its own contract, its own arrival time and its own idea of where the
       power is.</p>
    <p class="close">Tables, chairs, linens, decor, catering, setup, cleanup,
       parking, security and coordination are already here and already know
       each other. What is left for you to arrange is the interesting part.</p>
  </div>
</section>

<section>
  <div class="grid">
    <article class="card">
      {{img:inc-decor.webp|A long table laid with white linen, black chargers and greenery|class="wipe"}}
      <h3>Already on the property</h3>
      <p>Tables, chairs, linens and an extensive decor inventory, included rather than
         rented &mdash; so fewer details become their own vendor, their own invoice and
         their own phone call.</p>
    </article>
    <article class="card">
      {{img:inc-rain.webp|The conservatory from the lawn, glass on three sides|class="wipe"}}
      <h3>It rained, and nothing changed</h3>
      <p>Glass, cover and the whole property to move into, including the conservatory at
         Magnolia House. No tent. No five o'clock panic. No flip fee.</p>
    </article>
    <article class="card">
      {{img:inc-team.webp|The dance floor full, late in the evening|class="wipe"}}
      <h3>Handled behind the scenes</h3>
      <p>Setup, cleanup, golf carts, parking, security and coordination, by people who have
         worked this property hundreds of times and know where the kitchen is.</p>
    </article>
    <article class="card">
      {{img:inc-food.webp|Copper mugs and a garnished cocktail on a wooden board|class="wipe"}}
      <h3>In-house catering</h3>
      <p>Food actually served here, by a kitchen that works this estate every weekend.</p>
    </article>
    <article class="card">
      {{img:inc-sleep.webp|The cottages of Overlook Village along the hillside|class="wipe"}}
      <h3>Where everyone sleeps</h3>
      <p>Thirty-four people stay on the estate. A hotel is six minutes away for everyone
         else, and the airport is thirty.</p>
    </article>
    <article class="card">
      {{img:inc-yours.webp|An invitation suite, a ring dish and a bottle of scent|class="wipe"}}
      <h3>Your own team, welcome</h3>
      <p>Bring your planner and your vendors. We would rather support your plan than
         replace it. <a href="/planners/">For planners</a>.</p>
    </article>
  </div>
</section>

<section>
  <div class="stakes flip">
    <div class="lede">
      <div class="eyebrow">The one everybody asks about</div>
      <h2>And if it rains?</h2>
      <p>Nothing is struck, nothing is tented and nothing costs extra. The
         conservatory at Magnolia House is glass on three sides and already
         part of the property, so the wet-weather plan is a room you would have
         been happy to use anyway.</p>
      <p>The decision gets made at a sensible hour by people who have made it
         before, and the answer is a different room rather than a different
         day.</p>
    </div>
    <figure class="frame">
      {{img:inc-glass.webp|The conservatory inside, chandeliers over the floor|class="par"}}
    </figure>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="Sparklers at the doors of Magnolia House at night"
       style="background-image:url('/assets/img/close-included.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Still counting</div>
    <h2>The rest of the answers take about an hour.</h2>
    <p>Bring the questions your mother has been asking. They are usually the sharpest ones, and they are easier to answer standing in the room.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["weddings/real-weddings/index.html"] = dict(
    nav="Weddings", title="Real Weddings | %s" % SITE,
    desc="Weddings that have happened on the estate.",
    hero_img="real-weddings.webp", hero_alt="A couple in the meadow at golden hour",
    eyebrow="Celebrate &middot; Real weddings",
    h1="Weddings that happened here.",
    standfirst="Each one credited to the couple, the planner, the photographer and the "
               "vendors who made it.",
    body="""
<section>
  <div class="lede">
    <h2>Gallery</h2>
    <p>Ceremonies in the meadow, the deck at six, the hall late. Every wedding here is
    credited to the couple, the planner and the photographer who made it.</p>
  </div>
  <div class="gallery">
    <figure>{{img:g-1.webp|The couple at the arch, the ridge behind them}}</figure>
    <figure>{{img:g-2.webp|A first look on the path, the valley beyond}}</figure>
    <figure>{{img:g-3.webp|The first dance under the drapery and lights}}</figure>
    <figure>{{img:g-4.webp|The couple on the drive, Lookout Mountain behind}}</figure>
    <figure>{{img:g-5.webp|The dance floor late, glow sticks up}}</figure>
    <figure>{{img:g-6.webp|The rehearsal table laid under the pergola}}</figure>
    <figure>{{img:g-7.webp|The wedding party walking down through the trees}}</figure>
    <figure>{{img:g-8.webp|The recessional back up the aisle}}</figure>
  </div>
  <div class="note">
    <p><b>Awaiting content.</b> These are estate frames, not credited real weddings. The
       page needs a first set of six to eight weddings with the couple&rsquo;s permission,
       the planner and vendor credits under each, and photography from the current season.
       Nothing from before the property changed.</p>
    <p>The credits are not a courtesy. A vendor who is named here has a reason to name
       the estate on her own site, and that referral runs both ways.</p>
  </div>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">What you are looking at</div>
    <h2 class="rise-words"><span>Every</span> <span>wedding</span> <span>on</span> <span>this</span> <span>page</span> <span>had</span> <span>the</span> <span>property</span> <span>to</span> <span>itself.</span></h2>
    <p>There is no frame on this page taken around another wedding. No corner
       cropped to hide somebody else&rsquo;s reception, no shot timed for the
       ten minutes the lawn was free, no guests waiting behind a rope while a
       different family finished.</p>
    <p class="close">It is a small thing to claim and a difficult one to fake,
       and it is visible in almost every photograph once you know to look.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The dance floor late in the evening, lit purple"
       style="background-image:url('/assets/img/close-real.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Yours next</div>
    <h2>Every one of these was somebody&rsquo;s ordinary Saturday.</h2>
    <p>Until it was not. Come and walk the property, and we will show you where each of these was standing.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["weddings/single-day/index.html"] = dict(
    nav="Weddings", title="Single-Day Celebrations | %s" % SITE,
    desc="A single-day celebration on the estate.",
    hero_img="single-day.webp", hero_alt="The meadow, quiet, with the ridge beyond",
    eyebrow="Celebrate &middot; Single day",
    h1="A day, rather than a weekend.",
    standfirst="Not every celebration wants two nights. The estate still closes around one "
               "couple for the day, and nothing is shared.",
    body="""
<section>
  <div class="split">
    <div class="split-text">
      <h2>What stays the same</h2>
      <p>One celebration on the property. The whole estate to move through. The same
         inclusions, the same weather alternatives, the same people running it.</p>
      <h2 style="margin-top:1.5rem">What is different</h2>
      <p>No lodging night, no rehearsal evening, and no breakfast the morning after
         &mdash; which is to say, none of the parts most couples tell us afterwards they
         did not expect to love.</p>
      <a class="btn" href="/weddings/">See the Estate Weekend</a>
    </div>
    <figure class="frame">
      {{img:sd-fire.webp|The fire pit lit at golden hour, florals on either side|class="par"}}
    </figure>
  </div>
  <div class="note">
    <p><b>Positioning note.</b> This is a real offering and should convert, but the framework
       is explicit that it must not appear in the brand essence, the hero, or the homepage
       story. The weekend is the differentiator.</p>
  </div>
</section>

<section class="band">
  {{img:band-quiet.webp|The meadow from above, the arch small in the middle of it|class="band-img"}}
  <p>Whatever else changes, the property is still yours alone for the day.</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">What does not change</div>
    <h2 class="rise-words"><span>One</span> <span>celebration</span> <span>on</span> <span>the</span> <span>property.</span> <span>That</span> <span>part</span> <span>never</span> <span>moves.</span></h2>
    <p>The single-day celebration is a shorter answer to the same question,
       not a lesser version of somebody else&rsquo;s. There is still one
       wedding on the property. There is still no second arch coming down at
       the far end of the field.</p>
    <p class="close">What you give up is the two nights, and most couples who
       have had them will tell you that is the part they would keep.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The ceremony set out and empty, under a heavy sky"
       style="background-image:url('/assets/img/close-single.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Either way</div>
    <h2>Come and see which one it wants to be.</h2>
    <p>Most couples arrive certain they want the day and leave having worked out what the weekend would cost. It is an easier conversation on the property than off it.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["stay/index.html"] = dict(
    nav="Stay", title="Stay | %s" % SITE,
    desc="Private mountainside lodging on a 74-acre estate near Chattanooga.",
    hero_img="stay.webp", hero_alt="A cottage in the woods at the edge of the property",
    eyebrow="Stay",
    h1="Stay Where the Story Continues",
    standfirst="The cottages are open when there is no wedding on the property. A creek, a "
               "waterfall, two and a half miles of trails, and the oldest mountain range on "
               "earth outside the door.",
    actions=[("Inquire about a stay", "/inquire/")],
    body="""
<section>
  <div class="lede">
    <h2>Come for a weekend. Come back for an anniversary.</h2>
    <p>Or come once, look around, and start imagining something larger. A guest who stays
       two nights has seen the whole estate &mdash; which is how a good many weddings here
       begin.</p>
  </div>
  <div class="grid">
    <article class="card">
      <figure class="frame">{{img:stay-village.webp|The cottages of Overlook Village along the hillside|class="wipe"}}</figure>
      <div class="eyebrow">Overlook Village</div>
      <h3>Four cottages along the hill</h3>
      <p>Phoenix, Bluebird, Goldfinch and Hummingbird &mdash; three that sleep four and
         one that sleeps six, each turned to face out rather than at the next, so
         nobody is looking into anybody else&rsquo;s morning.</p>
    </article>
    <article class="card">
      <figure class="frame">{{img:stay-inside.webp|A cottage bathroom in timber, twin basins under twin mirrors|class="wipe"}}</figure>
      <div class="eyebrow">The Lodge, and inside</div>
      <h3>Thirty-four beds in all</h3>
      <p>The Lodge takes the largest group, with the Willow Room for hair and
         makeup on the morning and the Mahogany Suite for whoever is still up at
         one. Timber, glass and quiet throughout &mdash; built to be lived in for two
         nights rather than checked into for one.</p>
    </article>
  </div>
  <div class="note">
    <p><b>What would make this page worth visiting twice.</b> How many each cottage
       sleeps, which has the bath under the window, which is nearest the creek. That is
       what somebody choosing between them actually wants, it is the only thing that
       would justify a page per cottage, and none of it exists yet on the client side.
       Until it does, a list of names is decoration.</p>
    <p><b>Deliberately not listed here:</b> Lost in the Woods. The framework folds it into
       the Estate Weekend as the emotional close, rather than offering it as a separate
       bookable stay.</p>
  </div>
</section>

<section class="band">
  {{img:band-return.webp|A couple close together, the estate soft behind them|class="band-img"}}
  <p>Come once for the wedding. Come back for the anniversary.</p>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">Come back</div>
    <h2>Return and anniversary stays.</h2>
    <p>First, fifth and tenth anniversaries for every couple married here. Vow renewals,
       proposal weekends, return stays for the wedding party, and off-season rates between
       Saturdays.</p>
  </div>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">Why a wedding estate has beds in it</div>
    <h2 class="rise-words"><span>Thirty-four</span> <span>beds</span> <span>are</span> <span>why</span> <span>the</span> <span>weekend</span> <span>works.</span></h2>
    <p>Thirty-four people sleeping on the property is not a convenience that
       was added afterwards. It is the reason the weekend works at all: the
       rehearsal can run late, the morning can start slowly, and nobody spends
       the best day of their life reading directions on a phone.</p>
    <p class="close">Between Saturdays the same cottages are simply a quiet
       place in the woods with a creek at the bottom of it.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A sparkler lit outside a cottage after dark"
       style="background-image:url('/assets/img/close-stay.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Stay first</div>
    <h2>Book two nights before you book a wedding.</h2>
    <p>A guest who has slept here has already seen the property at six in the morning and at eleven at night, which is more than any tour can show you.</p>
    <a class="btn" href="/inquire/">Inquire about a stay</a>
  </div>
</section>
""")

PAGES["the-estate/index.html"] = dict(
    nav="The Estate", title="The Estate | %s" % SITE,
    desc="Seventy-four acres beneath Lookout Mountain, as one property.",
    hero_img="estate.webp", hero_alt="The meadow opening beneath the ridge, the deck at its edge",
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    eyebrow="One estate",
    h1="One property, one map, one path.",
    standfirst="There are not four "
               "venues. There is one estate, and every celebration includes all of it.",
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">Read this first</div>
    <h2 class="rise-words"><span>There</span> <span>are</span> <span>not</span> <span>four</span> <span>venues.</span> <span>There</span> <span>is</span> <span>one</span> <span>estate.</span></h2>
    <p>Ask most estates which space you are getting and they will tell you. Here it
       is the wrong question. The
       places below are not alternatives to choose between; they are four
       points on one walk, and every celebration here includes all of them.</p>
    <p class="close">You arrive at the house, you marry in the meadow, you
       drink on the deck and you dance in the hall. Nobody drives between them.</p>
  </div>
</section>

<section class="walk">
  <div class="lede">
    <div class="eyebrow">The walk</div>
    <h2>Six places, and the ground between them.</h2>
    <p>The drawing is the estate&rsquo;s own survey &mdash; contours every sixteen feet, off the same LiDAR the county holds. Six places, and the walk
       between them, at the size it actually is.</p>
  </div>
  <div class="walk-grid">
    <figure class="walk-map">
      {{inline:plan.svg}}
      <figcaption>Contours every 16 ft. The whole weekend is
        <b>3,045 ft</b> of walking &mdash; 0.58 miles, spread over two days.</figcaption>
    </figure>
  <div class="note">
    <p><b>Survey note.</b> Elevation is USGS 3DEP one-metre LiDAR; place positions are read from aerial imagery and want confirming against a site plan.</p>
  </div>
    <div class="walk-steps">
    <div class="wstep ws-1">
      <div class="eyebrow"><span>The way in</span></div>
      <h3>Arrival</h3>
      <p>You turn off Pope Creek Road and the gate closes behind you. For the next two days nothing arrives that you did not invite, and nothing leaves until you do. This is the only drive anybody makes all weekend.</p>
    </div>
    <div class="wstep ws-2">
      <div class="eyebrow"><span>Where you arrive</span><span class="dist">175 ft from the gate</span></div>
      <h3><a class="place-link" href="/the-estate/magnolia-house/">Magnolia House</a></h3>
      <p>White columns and glass against the ridge, at the top of the drive. It is the first photograph almost every guest takes, through the windshield on the way up. The conservatory behind it is also the weather plan that costs nothing.</p>
      <a class="door frame" href="/the-estate/magnolia-house/" aria-label="Magnolia House: see the page">
        {{img:magnolia-house.webp|Magnolia House, white columns above the lawn|class="par"}}
      </a>
    </div>
    <div class="wstep ws-3">
      <div class="eyebrow"><span>Where you marry</span><span class="dist">860 ft from the front door</span></div>
      <h3><a class="place-link" href="/the-estate/the-valley/">The Valley</a></h3>
      <p>An open meadow held on three sides by ridgeline, with Lookout Mountain beyond. Sound stays in it and the wind drops in it. Nothing is visible from it that the estate does not own.</p>
      <a class="door frame" href="/the-estate/the-valley/" aria-label="The Valley: see the page">
        {{img:the-valley.webp|The processional crossing the meadow|class="par"}}
      </a>
    </div>
    <div class="wstep ws-4">
      <div class="eyebrow"><span>Where the light goes</span><span class="dist">1,030 ft &mdash; the longest walk of the weekend</span></div>
      <h3><a class="place-link" href="/the-estate/lookout-deck/">The Lookout Deck</a></h3>
      <p>A railed deck out over the valley, facing the mountain. It turns gold at six, tip to tip, and everyone stops talking. Guests walk here from the ceremony; there is no shuttle because there is nothing to shuttle across.</p>
      <a class="door frame" href="/the-estate/lookout-deck/" aria-label="The Lookout Deck: see the page">
        {{img:lookout-deck.webp|A couple dancing on the Lookout Deck, the ridge behind|class="par"}}
      </a>
    </div>
    <div class="wstep ws-5">
      <div class="eyebrow"><span>Where you dine and dance</span><span class="dist">650 ft from the deck</span></div>
      <h3><a class="place-link" href="/the-estate/davis-hall/">Davis Hall</a></h3>
      <p>Drapery, chandeliers, and the room where the dancing happens. It carries the largest receptions on the property, and nobody has to find their car to get to it.</p>
      <a class="door frame" href="/the-estate/davis-hall/" aria-label="Davis Hall: see the page">
        {{img:davis-hall.webp|Davis Hall under its drapery, lit for the first dance|class="par"}}
      </a>
    </div>
    <div class="wstep ws-6">
      <div class="eyebrow"><span>Where everyone sleeps</span><span class="dist">325 ft, and then bed</span></div>
      <h3><a class="place-link" href="/the-estate/overlook-village/">Overlook Village</a></h3>
      <p>Cottages along the hill, thirty-four beds, and the end of the evening about a minute from the end of the party. This is the leg that every other venue replaces with a line of taxis.</p>
      <a class="door frame" href="/the-estate/overlook-village/" aria-label="Overlook Village: see the page">
        {{img:stay-village.webp|The cottages of Overlook Village along the hillside|class="par"}}
      </a>
    </div>
    </div>
  </div>
</section>

<section class="band">
  {{img:band-ground.webp|The couple standing at the arch in the open meadow|class="band-img"}}
  <p>Six places on one map, and you never leave the property to reach any of them.</p>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The ground itself</div>
    <h2>And the same ground, from the side.</h2>
    <p>The plan above flattens a property that is anything but flat: from the low
       ground to the high ridge inside that frame is a 240-foot climb. This is the
       same survey built as a model and turned, so the valley can be looked at
       from any angle.</p>
    <a class="btn" href="/terrain/">Open the terrain model</a>
  </div>
  <div class="note">
    <p><b>Still in prototype.</b> Elevation is USGS 3DEP one-metre LiDAR through The National
       Map; the imagery over it is USGS NAIP, October 2023, at 0.57&thinsp;m per pixel. Both
       are public domain federal survey data. The terrain model still lives at its old
       address and is not styled to match this site.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A bride at the deck rail, looking out at the mountain"
       style="background-image:url('/assets/img/close-estate.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">The whole of it</div>
    <h2>Seventy-four acres does not photograph.</h2>
    <p>You can see the six places on this page. What you cannot see from a screen is how far apart they are, how quiet the meadow is, or how the deck turns at six.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["planners/index.html"] = dict(
    nav="Planners", title="For Planners | %s" % SITE,
    desc="Site logistics, load-in and how a weekend runs at The Valley Venues.",
    hero_img="planners.webp", hero_alt="The estate from the deck, looking down the valley",
    eyebrow="For planners",
    h1="Bring your vision. We know the estate.",
    standfirst="Planners send couples here repeatedly once they trust the operation. This "
               "page is written to your lens rather than the bride's.",
    actions=[("Register as a planner", "/planners/register/")],
    body="""
<section>
  <div class="stakes">
    <div class="lede">
      <div class="eyebrow">Working here</div>
      <h2>What you will want to know before you quote.</h2>
      <p>The questions a planner asks on a first site visit, answered in the order
         you would ask them rather than the order they suit us.</p>
      <p>Most of the decor is already on the property, which shortens your rentals
         list and your load-in both.</p>
    </div>
    <figure class="frame">
      {{img:vend-table.webp|Glassware and candles down the length of a laid table|class="par"}}
    </figure>
  </div>
</section>

<section>
  <div class="grid">
    <article class="card">
      <h3>Site logistics</h3>
      <p>Load-in access, vehicle routes on the property, power, kitchen access, and where
         the golf carts live.</p>
    </article>
    <article class="card">
      <h3>How the weekend runs</h3>
      <p>What the estate handles and what it expects you to handle, hour by hour, from
         Friday load-in to Sunday clear.</p>
    </article>
    <article class="card">
      <h3>Staff handoffs</h3>
      <p>Who you speak to, when, and who is on the property overnight.</p>
    </article>
    <article class="card">
      <h3>Weather alternatives</h3>
      <p>Every indoor and covered option with real capacities, and the call time for a
         decision.</p>
    </article>
    <article class="card">
      <h3>Parking and guest movement</h3>
      <p>Arrival flow, level walking routes, and transport between spaces.</p>
    </article>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The shape of it</div>
    <h2>How a weekend actually runs.</h2>
    <p>Times are indicative and are settled with you for your weekend, but the
       sequence is the same every weekend and it is the sequence that matters
       when you are building a timeline.</p>
  </div>
  <div class="steps">
    <div class="step"><span class="when">Fri</span>
      <div><b>Load-in from midday</b><p>Vehicle access to every space. Nothing
      is being cleared from the weekend before, because there was no weekend
      before &mdash; the property was reset on Monday.</p></div></div>
    <div class="step"><span class="when">Fri</span>
      <div><b>Rehearsal, then dinner on the property</b><p>The rehearsal happens
      where the ceremony will. Guests who are staying check in and do not leave
      again.</p></div></div>
    <div class="step"><span class="when">Sat</span>
      <div><b>Your call time is not the venue&rsquo;s call time</b><p>Getting-ready
      spaces are already occupied, so hair and makeup can start whenever you
      need them to rather than whenever the doors open.</p></div></div>
    <div class="step"><span class="when">Sat</span>
      <div><b>Weather decision, made early</b><p>The alternative is a room, not a
      tent, so the call can be made in the morning and does not need to be
      revisited at five.</p></div></div>
    <div class="step"><span class="when">Sat</span>
      <div><b>Ceremony to deck to hall, on foot</b><p>No shuttle, no staged
      release of guests, no second parking plan. Golf carts for anyone who needs
      one.</p></div></div>
    <div class="step"><span class="when">Sun</span>
      <div><b>Clear on Sunday, not at midnight</b><p>Nothing has to be off the
      property before breakfast, because nothing is arriving behind you.</p></div></div>
  </div>
  <div class="note">
    <p><b>To confirm.</b> Load-in times, vehicle routes, power and kitchen access,
       overnight staffing and the weather call time all need filling in from the
       operations team. It is the part planners read first.</p>
  </div>
</section>

<section class="band">
  {{img:pl-deck.webp|A group on the Lookout Deck with the mountain behind them|class="band-img"}}
  <p>One load-in. One site. One team who has done this here before.</p>
</section>

<section>
  <div class="note">
    <p><b>Prototype note.</b> This page carries its own capture, and that list is tagged and
       worked separately from bridal inquiries.</p>
  </div>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">How we work with you</div>
    <h2 class="rise-words"><span>We</span> <span>are</span> <span>an</span> <span>extension</span> <span>of</span> <span>your</span> <span>team.</span></h2>
    <p>Not a replacement for it. The estate has its own in-house crew and they are
       used to working alongside a planner rather than instead of one &mdash; your
       design, your timeline, your client relationship, and people who know where
       the power is and which door the kitchen is behind.</p>
    <p>One load-in. One site. One crew, on the property overnight. No shared loading
       bay, no other planner&rsquo;s truck in the way, no negotiation over who gets
       the ceremony lawn at four.</p>
    <p class="close">You are not competing for the venue&rsquo;s attention, because
       there is nobody else here to give it to.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A couple at the rail of the Lookout Deck, the ridge behind"
       style="background-image:url('/assets/img/close-planners.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Trade inquiries</div>
    <h2>Come and walk it without a couple.</h2>
    <p>Planner site visits are welcome on their own, and are a good deal more useful than a floor plan. Bring a timeline and we will tell you what it actually takes here.</p>
    <a class="btn" href="/planners/register/">Register as a planner</a>
  </div>
</section>
""")

PAGES["planners/register/index.html"] = dict(
    nav="Planners", title="Register as a Planner | %s" % SITE,
    desc="Register as a planner with The Valley Venues.",
    hero_img="pl-deck.webp",
    hero_alt="A group on the Lookout Deck with the mountain behind them",
    eyebrow="For planners &middot; Register",
    h1="Tell us who you are.",
    standfirst="Short on purpose. You do not have a date, a guest count or a "
               "budget to give us, and asking for them would only slow this "
               "down. The website and handle are for your listing on the "
               "approved planners page.",
    body="""
<section>
  <form class="form inquiry" id="inquiry-planner" novalidate
        data-inquiry-type="Planner" data-kind="planner">
    <div class="field-row">
      <div class="field">
        <label for="p_first_name">First name <b aria-hidden="true">*</b></label>
        <input id="p_first_name" name="first_name" type="text" autocomplete="given-name" required>
      </div>
      <div class="field">
        <label for="p_last_name">Last name</label>
        <input id="p_last_name" name="last_name" type="text" autocomplete="family-name">
      </div>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="p_email">Email <b aria-hidden="true">*</b></label>
        <input id="p_email" name="email" type="email" autocomplete="email" required>
      </div>
      <div class="field">
        <label for="p_phone">Phone</label>
        <input id="p_phone" name="phone" type="tel" autocomplete="tel"
              >
      </div>
    </div>

    <div class="field">
      <label for="p_planner_name">Your studio <b aria-hidden="true">*</b></label>
      <input id="p_planner_name" name="planner_name" type="text"
             autocomplete="organization" required>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="p_planner_website">Website</label>
        <input id="p_planner_website" name="planner_website" type="url"
               inputmode="url" autocomplete="url"
              >
      </div>
      <div class="field">
        <label for="p_planner_social">Instagram</label>
        <input id="p_planner_social" name="planner_social" type="text"
              >
      </div>
    </div>

    <div class="field">
      <label for="p_referral_source">How did you hear about the estate?</label>
      <select id="p_referral_source" name="referral_source">
        <option value="">&mdash;</option>
        <option>Instagram</option>
        <option>TikTok</option>
        <option>Google</option>
        <option>Planner referral</option>
        <option>Past couple</option>
        <option>Wedding site</option>
        <option>Other</option>
      </select>
    </div>

    <div class="hp" aria-hidden="true">
      <label for="p_website">Website</label>
      <input id="p_website" name="_hp" type="text" tabindex="-1" autocomplete="off">
    </div>

    <p class="form-error" id="inquiry-planner-error" role="alert" hidden></p>
    <button class="btn btn-solid" type="submit">Register</button>
    <p class="form-privacy">This goes to the planner list, not the bridal one.
       You will not get couples&rsquo; email.</p>
  </form>

  <div class="form-done" id="inquiry-planner-done" role="status" hidden>
    <div class="eyebrow">Registered</div>
    <h2>Welcome. Come and walk it.</h2>
    <p>A welcome note is on its way, and planner site visits are welcome on
       their own &mdash; without a couple, and a good deal more useful than a
       floor plan. Reply to that email with a date that suits you.</p>
  </div>

  <div class="note">
    <p><b>New keys, and the CRM has to be told.</b> Website and Instagram post as
       <code>planner_website</code> and <code>planner_social</code>. Per section 6 of the
       webhook spec, GoHighLevel built its field mapping from one sample payload and matches
       on key names &mdash; so after the custom fields exist, the sample request must be
       <b>re-fetched</b> in the workflow trigger. Skip that and both fields arrive and go
       nowhere, silently, exactly like a mistyped dropdown value.</p>
  </div>
</section>
""")


PAGES["about/index.html"] = dict(
    nav="About", title="About | %s" % SITE,
    desc="The family behind the estate, and the design thinking behind the experience.",
    hero_img="about.webp", hero_alt="Magnolia House, columns and glass against the ridge",
    eyebrow="About",
    h1="The Question Behind Every Room",
    standfirst="A family estate, and a design philosophy that starts somewhere unusual for a "
               "wedding venue: not with how a room looks, but with how a person will feel "
               "standing in it.",
    body="""
<section>
 <div class="stakes flip">
  <div class="lede">
    <div class="eyebrow">Kobi Cummings</div>
    <h2>Co-founder, certified wedding planner, experiential designer.</h2>
    <p>Kobi holds a Bachelor of Fine Arts in production design from the Savannah College of
       Art and Design, with a minor in themed entertainment, and worked at Disney Live
       Entertainment as an arts specialist on shows, parades, props and environments &mdash;
       all of them built around one question. <em>What should the guest feel in this
       moment?</em></p>
    <p>It is the same question she asks about the moment the doors open and everyone turns
       around. Whoever sits closest to the dance floor is in every photograph of your first
       dance. That should be someone you love.</p>
  </div>
  <div class="cluster wide">
    <figure class="cl-1">{{img:ab-toast.webp|The bride and her party raising a glass together indoors}}</figure>
    <figure class="cl-2">{{img:inc-decor.webp|A table laid with linen, chargers and greenery}}</figure>
    <figure class="cl-3">{{img:g-3.webp|The first dance under the drapery and lights}}</figure>
  </div>
 </div>
  <div class="note">
    <p><b>Approval required.</b> This wording follows Draft 2 of the brand framework and needs
       approving word for word before it appears publicly. Claims stay first person and
       factual, with no sole credit anywhere.</p>
    <p><b>Missing.</b> There is no photograph of Kobi in the 2,472-image library. An About
       page whose subject is a person needs one, and it is the single most useful frame the
       next shoot could produce.</p>
  </div>
</section>

<section class="band">
  {{img:band-family.webp|A couple walking together in the meadow|class="band-img"}}
  <p>What should the guest feel, standing in this moment?</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">The working method</div>
    <h2 class="rise-words"><span>A</span> <span>room</span> <span>is</span> <span>not</span> <span>a</span> <span>look.</span> <span>It</span> <span>is</span> <span>a</span> <span>feeling</span> <span>somebody</span> <span>has</span> <span>standing</span> <span>in</span> <span>it.</span></h2>
    <p>Themed entertainment design starts from the guest and works backwards.
       Not <em>what should this room look like</em> but <em>what should a person
       feel standing in it, at this hour, having just done the thing they came
       here to do.</em></p>
    <p class="close">It is why the seating chart matters more than the
       centerpieces, why the walk from the ceremony to the deck is a walk and
       not a shuttle, and why the last thing on the property is a cottage in the
       woods rather than a parking lot.</p>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The family</div>
    <h2>A family story, still.</h2>
    <p>Paul Cummings bought the property for another purpose entirely. Over time he and his
       daughter Kobi began restoring and reimagining it, and what emerged was not a
       collection of event spaces but a hospitality estate.</p>
    <p>The estate should grow without anyone becoming a room number. Couples are known here, by name.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A mother settling her daughter's veil before the ceremony"
       style="background-image:url('/assets/img/close-about.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Come and meet her</div>
    <h2>Kobi answers, and Kobi is there on the night.</h2>
    <p>Not a sales office. The people who answer the inquiry are the people who will be on the property at eleven at night on your Saturday.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["inquire/index.html"] = dict(
    nav=None, title="Speak with Our Team | %s" % SITE,
    desc="Tell us about the weekend you are imagining, and a person will write back.",
    hero_img="tour.webp",
    hero_alt="A couple turning together in the open meadow, the ridge beyond",
    eyebrow="Speak with our team",
    h1="Let&rsquo;s create one of the best days of your life.",
    standfirst="It begins here, with a conversation. Tell us a little about the two of "
               "you and the day you are imagining, and a person will write back.",
    body="""

<section>
  <form class="form inquiry" id="inquiry-couple" novalidate
        data-inquiry-type="Couple" data-kind="couple">
    <p class="form-intro">Everything except your name and email is optional.
       Tell us as much or as little as you like.</p>

    <div class="field-row">
      <div class="field">
        <label for="first_name">First name <b aria-hidden="true">*</b></label>
        <input id="first_name" name="first_name" type="text" autocomplete="given-name" required>
      </div>
      <div class="field">
        <label for="last_name">Last name</label>
        <input id="last_name" name="last_name" type="text" autocomplete="family-name">
      </div>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="email">Email <b aria-hidden="true">*</b></label>
        <input id="email" name="email" type="email" autocomplete="email" required>
      </div>
      <div class="field">
        <label for="phone">Phone</label>
        <input id="phone" name="phone" type="tel" autocomplete="tel"
              >
      </div>
    </div>

    <fieldset class="field-set" data-group="when">
      <legend>When</legend>
      <p class="hint">A date or a season &mdash; either is enough to start with.</p>
      <div class="field-row">
        <div class="field">
          <label for="event_date">Your date, if you have one</label>
          <input id="event_date" name="event_date" type="date">
        </div>
        <div class="field">
          <label for="season">Or the season you are considering</label>
          <select id="season" name="season">
            <option value="">&mdash;</option>
            <option>Spring</option>
            <option>Summer</option>
            <option>Fall</option>
            <option>Winter</option>
            <option>Not sure</option>
          </select>
        </div>
      </div>
      <div class="field">
        <label for="date_flexible">Is the date flexible?</label>
        <select id="date_flexible" name="date_flexible">
          <option value="">&mdash;</option>
          <option>Yes</option>
          <option>No</option>
        </select>
      </div>
    </fieldset>

    <div class="field-row">
      <div class="field">
        <label for="experience_type">A weekend, or a single day? <b aria-hidden="true">*</b></label>
        <select id="experience_type" name="experience_type" required>
          <option value="">&mdash;</option>
          <option>Estate Weekend</option>
          <option>Single Day</option>
          <option>Undecided</option>
        </select>
      </div>
      <div class="field">
        <label for="guest_count">Roughly how many people</label>
        <input id="guest_count" name="guest_count" type="number" min="0" max="1000"
               inputmode="numeric" placeholder="An estimate is fine">
      </div>
    </div>

    <div class="field">
      <label for="lodging_interest">Would you want people staying on the property?</label>
      <select id="lodging_interest" name="lodging_interest">
        <option value="">&mdash;</option>
        <option>Yes</option>
        <option>No</option>
      </select>
    </div>

    <div class="field">
      <label for="feeling">What do you want the weekend to feel like?</label>
      <textarea id="feeling" name="feeling" rows="4"
                placeholder="In your own words."></textarea>
    </div>

    <div class="field-row">
      <div class="field">
        <label for="working_with_planner">Are you working with a planner?</label>
        <select id="working_with_planner" name="working_with_planner">
          <option value="">&mdash;</option>
          <option>Yes</option>
          <option>No</option>
          <option>Looking for one</option>
        </select>
      </div>
      <div class="field" id="planner-name-field" hidden>
        <label for="planner_name">Their studio</label>
        <input id="planner_name" name="planner_name" type="text">
      </div>
    </div>

    <div class="field">
      <label for="referral_source">How did you hear about us?</label>
      <select id="referral_source" name="referral_source">
        <option value="">&mdash;</option>
        <option>Instagram</option>
        <option>TikTok</option>
        <option>Google</option>
        <option>Planner referral</option>
        <option>Past couple</option>
        <option>Wedding site</option>
        <option>Other</option>
      </select>
    </div>

    <div class="hp" aria-hidden="true">
      <label for="c_website">Website</label>
      <input id="c_website" name="_hp" type="text" tabindex="-1" autocomplete="off">
    </div>

    <p class="form-error" id="inquiry-couple-error" role="alert" hidden></p>
    <button class="btn btn-solid" type="submit">Let&rsquo;s begin</button>
    <p class="form-privacy">Only ever used to write back to you.</p>
  </form>

  <div class="form-done" id="inquiry-couple-done" role="status" hidden>
    <div class="eyebrow">Thank you</div>
    <h2>And so it begins.</h2>
    <p>A person will write back soon. If you would rather talk it through, say so
       and we will find a time. If you have not heard from us within a day or so,
       email <a href="mailto:Info@thevalleyvenues.com">Info@thevalleyvenues.com</a>.</p>
  </div>

  <div class="note">
    <p><b>Why this is not called Book a Tour.</b> The direction document measures the
       site on tours booked, and the framework says the tour is &ldquo;something a couple
       is fortunate to be offered.&rdquo; Both are served better by a conversation on the
       door than a tour on it: the audience is Atlanta, Nashville, Knoxville and, the
       document hopes, Chicago and New York, and a tour is a flight for most of them. The
       conversation is the intake; the tour is what the right couple is offered afterward.</p>
    <p><b>Prototype note.</b> The form posts straight to GoHighLevel from the browser.
       Note what it does not ask: your total
       budget. That question closes more doors than it filters, and guest count arrives
       naturally here anyway &mdash; after you have described what you want, rather than as
       the price of entry.</p>
    <p>What comes back should be a person, not a pamphlet: a short, specific reply in the
       brand voice, signed by Kobi.</p>
    <p>The two starred fields are starred for a reason beyond politeness. The CRM only
       starts Kobi&rsquo;s sequence for an inquiry that has an experience type <em>and</em>
       either a date or a season; anything less sits in the pipeline unworked. So the form
       insists on them rather than letting somebody skip both and never hear back.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="Magnolia House at the top of the drive, the ridge behind it"
       style="background-image:url('/assets/img/close-tour.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">When you are ready</div>
    <h2>Come and stand in it.</h2>
    <p>More than half of the couples who walk this property choose it. When it suits
       you, come and see it for yourself &mdash; fifteen minutes from downtown
       Chattanooga, and
       the visit is free.</p>
    <a class="btn" href="#main">Speak with our team</a>
  </div>
</section>
""")


PAGES["the-estate/magnolia-house/index.html"] = dict(
    nav="The Estate", title="Magnolia House | %s" % SITE,
    desc='Built in the 1890s, lost to a fire in 2025, and raised again with the original columns at the front and a glass conservatory behind.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='magnolia-house.webp',
    hero_alt='Magnolia House, white columns above the lawn, the ridge behind',
    eyebrow='The Estate &middot; Magnolia House &middot; Where it begins',
    h1='The house the estate is known by.',
    standfirst='Built in the 1890s, lost to a fire in 2025, and raised again with the original columns at the front and a glass conservatory behind. It is the first thing you see, and the reason most people come.',
    actions=[("Speak with our team", "/inquire/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">Where the estate begins</div>\n    <h2>Not a rebuild. A rebirth.</h2>\n    <p>Magnolia House is the building the estate is known by, and it is the first\n       thing every guest sees &mdash; a hundred and seventy-five feet from the gate, at the top\n       of the drive, white columns against the ridge. It was raised in the 1890s.\n       In May 2025 a fire took the interior, and the family chose to bring it back\n       rather than replace it.</p>\n    <p>The front is restored to its history as closely as the record allows. The\n       columns you marry in front of are the original columns, saved from the fire\n       and standing again. Window frames and a wooden mantle from the old house\n       are back in the new one. And behind the house, where there was nothing\n       before, there is a conservatory &mdash; glass on three sides, Lookout\n       Mountain on the fourth, light all day &mdash; which is also the answer to\n       what happens if it rains: nothing is tented, nothing is struck, and nothing\n       costs extra.</p>\n    <p>Everything else on the property is arranged around it. You arrive here.\n       You marry in the meadow below it. You come back to it for dinner under\n       glass, and you walk up to the cottages from its door.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Built</span>The 1890s. Reborn in 2026, on the original footprint.</li>\n    <li><span>Holds</span>The ceremony, the reception, cocktails, and the rehearsal dinner the night before.</li>\n    <li><span>The conservatory</span>Glass on three sides, the mountain on the fourth. The weather plan that costs nothing.</li>\n    <li><span>The columns</span>Original, saved from the fire, and still what you stand in front of.</li>\n    <li><span>Where it sits</span>A hundred and seventy-five feet from the gate. The first photograph most guests take.</li>\n    <li><span>Then</span>Eight hundred and sixty feet, on foot, to the meadow.</li>\n  </ul>\n\n  <div class="note">\n    <p><b>Working note.</b> The live site still carries the rebuild page &mdash;\n       &ldquo;Coming 2026&rdquo;, pre-opening FAQs, reduced rates during construction.\n       None of it was carried over. The two frames marked &ldquo;as drawn&rdquo; are\n       architectural renderings; the finished house has not been photographed for\n       the site yet, and that is the first shoot to book.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Magnolia House, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:mh-1.webp|The house from the drive, with the conservatory behind it, as drawn}}</figure>\n    <figure>{{img:mh-2.webp|The original columns}}</figure>\n    <figure>{{img:mh-3.webp|Under the columns, Lookout Mountain behind}}</figure>\n    <figure>{{img:mh-4.webp|A first look on the steps}}</figure>\n    <figure>{{img:mh-5.webp|The conservatory, glass on three sides, as drawn}}</figure>\n    <figure>{{img:mh-6.webp|On the steps}}</figure>\n    <figure>{{img:mh-7.webp|The porch}}</figure>\n    <figure>{{img:mh-8.webp|A table laid on the porch}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <span></span>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/the-valley/"><span>On the walk, next</span><b>The Valley</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The conservatory lit from within after dark"\n       style="background-image:url(\'/assets/img/close-weddings.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">After dark</div>\n    <h2>See it lit.</h2>\n    <p>The conservatory at night is the reason the house was rebuilt with glass.\n       Come and stand in it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/inquire/">Speak with our team</a>\n  </div>\n</section>\n')

PAGES["the-estate/the-valley/index.html"] = dict(
    nav="The Estate", title="The Valley | %s" % SITE,
    desc='An open meadow held on three sides by ridgeline, with Lookout Mountain beyond.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='the-valley.webp',
    hero_alt='The processional crossing the meadow toward the arch',
    eyebrow='The Estate &middot; The Valley &middot; Where you marry',
    h1='The meadow where it happens.',
    standfirst='An open meadow held on three sides by ridgeline, with Lookout Mountain beyond. Sound stays in it, the wind drops in it, and nothing is visible from it that the estate does not own.',
    actions=[("Speak with our team", "/inquire/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>Held on three sides, open on the fourth.</h2>\n    <p>The Valley is the flat, open ground through the middle of the property, and\n       the hills around it are why it works. They keep the sound in and the wind\n       out, and they hold the last half hour of light after it has left the grass.\n       The fourth side is the mountain.</p>\n    <p>This is where you marry. It is also where the rehearsal happens the night\n       before, where cocktails can be poured under the sky, and where dinner can\n       be laid if the evening is the kind that wants to stay outside. Whatever is\n       set here is set for one couple: there is no second ceremony on the\n       property, and nobody&rsquo;s arch comes down while yours goes up.</p>\n    <p>It is eight hundred and sixty feet from the front door of Magnolia\n       House, and everyone walks it.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>The ceremony. The rehearsal. Cocktails and dinner under the sky when the evening allows.</li>\n    <li><span>Faces</span>Lookout Mountain, across the open side.</li>\n    <li><span>Held by</span>Ridgeline on three sides. Sound stays in, wind stays out.</li>\n    <li><span>Seats</span>Up to three hundred, in the meadow, facing the mountain.</li>\n    <li><span>If it rains</span>The conservatory at Magnolia House. No tent, no flip fee, no five o&rsquo;clock decision.</li>\n    <li><span>Then</span>A thousand feet, on foot, up to the deck &mdash; the longest walk of the weekend.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>The Valley, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:tv-1.webp|The ceremony in the meadow, the ridge behind the congregation}}</figure>\n    <figure>{{img:tv-2.webp|At the arch, the ridge behind}}</figure>\n    <figure>{{img:tv-3.webp|Seated toward the mountain}}</figure>\n    <figure>{{img:tv-4.webp|The recessional, petals in the air}}</figure>\n    <figure>{{img:tv-5.webp|The meadow from above, the arch small in the middle of it}}</figure>\n    <figure>{{img:tv-6.webp|Walking the meadow}}</figure>\n    <figure>{{img:tv-7.webp|Through the tall grass toward the arch}}</figure>\n    <figure>{{img:tv-8.webp|The creek at the foot of the meadow}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/magnolia-house/"><span>Before this</span><b>Magnolia House</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/lookout-deck/"><span>On the walk, next</span><b>Lookout Deck</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The ceremony set out and empty, under a heavy sky"\n       style="background-image:url(\'/assets/img/close-single.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Set, and waiting</div>\n    <h2>Nobody else is standing here.</h2>\n    <p>The meadow is arranged once, for you, and put away afterward. Walk it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/inquire/">Speak with our team</a>\n  </div>\n</section>\n')

PAGES["the-estate/lookout-deck/index.html"] = dict(
    nav="The Estate", title="Lookout Deck | %s" % SITE,
    desc='A railed deck out over the valley, facing Lookout Mountain.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='lookout-deck.webp',
    hero_alt='A couple dancing on the Lookout Deck, the ridge behind them',
    eyebrow='The Estate &middot; Lookout Deck &middot; Where the light goes',
    h1='Where the mountain turns gold.',
    standfirst='A railed deck out over the valley, facing Lookout Mountain. At six the light goes across it tip to tip, and everyone stops talking.',
    actions=[("Speak with our team", "/inquire/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>The view no other estate in the region has.</h2>\n    <p>The deck is built out over the fall of the land, so the valley drops away\n       beneath the rail and the mountain fills everything beyond it. It is where\n       cocktails are poured after the ceremony &mdash; or where the ceremony itself is held, at the rail, with the mountain for a backdrop &mdash; where the first look tends to\n       happen in the morning, and where the wedding party ends up whenever nobody\n       has told them where to be.</p>\n    <p>Guests walk here from the meadow. It is a thousand feet,\n       the longest walk of the whole weekend, and it goes uphill toward the light\n       &mdash; which is the point. Nobody is shuttled, nobody is released in\n       groups, and nobody is looking for their keys.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>A ceremony at the rail, facing the mountain. Cocktail hour. The first look. Small dinners. Anything that wants the view.</li>\n    <li><span>Faces</span>Lookout Mountain and the evening light, across the whole width of the valley.</li>\n    <li><span>The hour</span>Gold at six, tip to tip, for about half an hour.</li>\n    <li><span>Sits</span>A thousand feet from the meadow. Six hundred and fifty from Davis Hall.</li>\n    <li><span>Then</span>Down to the hall for dinner, on foot, in the last of it.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Lookout Deck, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:ld-1.webp|The deck set for a ceremony, the mountain in autumn}}</figure>\n    <figure>{{img:ld-2.webp|At the arch on the deck}}</figure>\n    <figure>{{img:ld-3.webp|At the rail, in fog}}</figure>\n    <figure>{{img:ld-4.webp|A lounge at the rail, the mountain beyond}}</figure>\n    <figure>{{img:ld-5.webp|An arch at the rail, facing the ridge}}</figure>\n    <figure>{{img:ld-6.webp|The party, umbrellas up}}</figure>\n    <figure>{{img:ld-7.webp|At the rail}}</figure>\n    <figure>{{img:ld-8.webp|On the deck, the ridge behind}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/the-valley/"><span>Before this</span><b>The Valley</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/davis-hall/"><span>On the walk, next</span><b>Davis Hall</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A couple at the rail of the Lookout Deck, the ridge behind"\n       style="background-image:url(\'/assets/img/close-planners.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">At the rail</div>\n    <h2>Stand here at six.</h2>\n    <p>It does not photograph. That is why the tour exists. Come when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/inquire/">Speak with our team</a>\n  </div>\n</section>\n')

PAGES["the-estate/davis-hall/index.html"] = dict(
    nav="The Estate", title="Davis Hall | %s" % SITE,
    desc='Drapery, chandeliers, and the largest floor on the property.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='davis-hall.webp',
    hero_alt='Davis Hall under its drapery, lit for the first dance',
    eyebrow='The Estate &middot; Davis Hall &middot; Where you dine and dance',
    h1='The room where the dancing happens.',
    standfirst='Drapery, chandeliers, and the largest floor on the property. Dinner, the first dance, and everything after it &mdash; six hundred and fifty feet from the deck and a minute from bed.',
    actions=[("Speak with our team", "/inquire/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>Earned by the evening.</h2>\n    <p>Davis Hall is the room the weekend arrives at rather than the one it starts\n       in. Dinner is here. The first dance is here. The floor is the largest on the\n       estate and it carries the largest receptions the property holds, under\n       drapery and chandeliers, with the estate&rsquo;s own tables, chairs and\n       linens already in the room rather than on a truck.</p>\n    <p>It is six hundred and fifty feet from the deck, so the walk down happens in the last\n       of the light, and three hundred and twenty-five feet from the cottages, so the walk up\n       happens whenever you are ready and not when a shuttle is. Nobody leaves at\n       eleven because nobody has anywhere to drive to.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>Dinner. The first dance. The largest receptions on the property.</li>\n    <li><span>Dressed</span>Drapery and chandeliers, and the estate&rsquo;s own tables, chairs and linens.</li>\n    <li><span>Sits</span>Six hundred and fifty feet from the deck. Ninety-nine from the cottages.</li>\n    <li><span>After</span>Nobody drives. The cottages are up the hill and the night is yours.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Davis Hall, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:dh-1.webp|The room set, drapery and the checkerboard floor, in daylight}}</figure>\n    <figure>{{img:dh-2.webp|Laid for dinner}}</figure>\n    <figure>{{img:dh-3.webp|The head table under the drapery}}</figure>\n    <figure>{{img:dh-4.webp|At the sweetheart table}}</figure>\n    <figure>{{img:dh-5.webp|The first dance, the party watching}}</figure>\n    <figure>{{img:dh-6.webp|Later}}</figure>\n    <figure>{{img:dh-7.webp|A centerpiece}}</figure>\n    <figure>{{img:dh-8.webp|A table, laid}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/lookout-deck/"><span>Before this</span><b>Lookout Deck</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/overlook-village/"><span>On the walk, next</span><b>Overlook Village</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The dance floor late in the evening, lit purple"\n       style="background-image:url(\'/assets/img/close-real.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Late</div>\n    <h2>Nobody is leaving.</h2>\n    <p>The room is yours until you are done with it. Come and stand in it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/inquire/">Speak with our team</a>\n  </div>\n</section>\n')

PAGES["the-estate/overlook-village/index.html"] = dict(
    nav="The Estate", title="Overlook Village | %s" % SITE,
    desc='Four cottages along the hill, a lodge for the largest party, and one cottage in the woods for the two of you.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='stay-village.webp',
    hero_alt='The cottages of Overlook Village along the hillside',
    eyebrow='The Estate &middot; Overlook Village &middot; Where everyone sleeps',
    h1='Where everyone sleeps.',
    standfirst='Four cottages along the hill, a lodge for the largest party, and one cottage in the woods for the two of you. Thirty-four beds, a minute from the end of the evening.',
    actions=[("Speak with our team", "/inquire/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">The village</div>\n    <h2>Four cottages, each turned to face out.</h2>\n    <p>Phoenix, Bluebird, Goldfinch and Hummingbird sit along the hill above the\n       hall, each one turned toward the view rather than toward the next, so nobody\n       is looking into anybody else&rsquo;s morning. Three sleep four and one sleeps\n       six &mdash; a queen bed and a queen pull-out in each &mdash; with a kitchenette\n       inside and a shared outdoor kitchen between them: a grill, a pizza oven, and\n       a hammock for whoever is done.</p>\n    <p>Private hot tubs are coming. Between Saturdays the village is open as a\n       <a href="/stay/">stay</a> on its own terms.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Cottages</span>Four. Phoenix, Bluebird, Goldfinch, Hummingbird.</li>\n    <li><span>Sleeps</span>Eighteen across the village. Three cottages sleep four, one sleeps six.</li>\n    <li><span>Inside</span>A queen bed, a queen pull-out, a kitchenette with a stovetop, fridge, microwave and dishwasher.</li>\n    <li><span>Between them</span>An outdoor kitchen with a grill and a pizza oven. A hammock. Hot tubs on the way.</li>\n    <li><span>Sits</span>Three hundred and twenty-five feet up the hill from Davis Hall, on foot.</li>\n  </ul>\n\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">The Lodge</div>\n    <h2>For the largest party, and the morning.</h2>\n    <p>The Lodge takes the wedding party or the biggest family group, and it has two\n       rooms that matter on the day. The Willow Room is a private hair and makeup\n       studio, so the morning starts where you slept and not in a car. The Mahogany\n       Suite is a pool table, a card table and a seventy-inch screen, for whoever is\n       still up at one.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">And then</div>\n    <h2>Lost in the Woods.</h2>\n    <p>One cottage, tucked away at the far edge of the property, for the two of you.\n       A king bed. A full kitchen. A walk-in shower and a soaking tub. Outside, your\n       own kitchen and grill, a fire pit sunk into the ground, and a fountain you\n       will hear before you see. It is where the wedding party gathers the night\n       before, and where the two of you disappear to afterward &mdash; married,\n       alone, and thirty seconds from everyone you love.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Lost in the Woods</span>One cottage. A king bed, a full kitchen, a walk-in shower and a soaking tub.</li>\n    <li><span>Outside</span>Your own kitchen and grill, an in-ground fire pit, a fountain.</li>\n    <li><span>In all</span>Thirty-four beds on the estate. A hotel is six minutes away for everyone else.</li>\n  </ul>\n\n  <div class="note">\n    <p><b>Where the direction and the live site differ.</b> The live site sells Lost in\n       the Woods as a bookable honeymoon suite. The direction document folds it into the\n       Estate Weekend as the emotional close rather than offering it separately, and\n       this page follows the direction. Bachelorette weekends are also sold on the live\n       site; the framework retires the word &ldquo;package&rdquo; in guest copy, so if\n       they stay, they are a <em>stay</em>.</p>\n  </div>\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Overlook Village, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:ov-1.webp|Overlook Village from above, the mountain behind}}</figure>\n    <figure>{{img:ov-2.webp|The cottages at dusk}}</figure>\n    <figure>{{img:ov-3.webp|Along the hill}}</figure>\n    <figure>{{img:ov-4.webp|Every cottage faces out: a chair at the window over the valley}}</figure>\n    <figure>{{img:ov-5.webp|The Mahogany Suite in the Lodge}}</figure>\n    <figure>{{img:ov-6.webp|A vanity with twin mirrors, in the Lodge}}</figure>\n    <figure>{{img:ov-7.webp|A soaking tub under the lights}}</figure>\n    <figure>{{img:ov-8.webp|Outside the cottage in the woods}}</figure>\n  </div>\n  <p class="credit">Photography by Christin Sofka.</p>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/davis-hall/"><span>Before this</span><b>Davis Hall</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <span></span>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A sparkler lit outside a cottage after dark"\n       style="background-image:url(\'/assets/img/close-stay.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Goodnight, not goodbye</div>\n    <h2>The party is a minute from bed.</h2>\n    <p>Which is the whole idea. Come and see the cottages when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/inquire/">Speak with our team</a>\n  </div>\n</section>\n')

PAGES["the-difference/index.html"] = dict(
    nav="The Difference", title="The Difference | %s" % SITE,
    desc="Why one wedding at a time changes everything else: the whole estate, everything handled, and everyone knows your name.",
    hero_img="single-day.webp", hero_alt="The meadow, empty and waiting, with the ridge beyond",
    eyebrow="The Difference",
    h1="Yours, and only yours.",
    standfirst="For two days there is nobody on seventy-four acres you did not invite. "
               "Everything you need is already here, everything is handled, and everyone "
               "you meet will call you by your first name.",
    actions=[("Speak with our team", "/inquire/"),
             ("Walk the Estate", "/the-estate/")],
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">Read this first</div>
    <h2 class="rise-words"><span>Weddings</span> <span>are</span> <span>stressful.</span> <span>This</span> <span>one</span> <span>does</span> <span>not</span> <span>have</span> <span>to</span> <span>be.</span></h2>
    <p>Most of the stress of a wedding is not the wedding. It is eleven companies who have
       never met, four hotels, a room that opens at four because it was being reset until
       three, and a timeline somebody else wrote. None of that is on the property.</p>
    <p class="close">What is left is the day, and the two of you in it.</p>
  </div>
</section>

<section>
  <div class="split">
    {{img:band-estate.webp|The estate from above, two people alone in the meadow}}
    <div class="split-text">
      <div class="eyebrow">One at a time</div>
      <h2>The whole estate. One wedding. Ever.</h2>
      <p>Larger estates around here run two or three weddings on a Saturday. This one
         holds one, and holds it for the weekend. The gate closes on Friday behind one
         family and does not open for anyone else until you leave.</p>
      <p>So nothing on the property is timed around anyone but you. The ceremony happens
         when the light is best, not when the room is free. The rehearsal happens where the
         vows will. The music runs as late as your people do.</p>
      <a class="btn" href="/the-estate/">Walk the Estate</a>
    </div>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">Not here</div>
    <h2>The list of things you will not find.</h2>
    <ul class="nots">
      <li>A second wedding on the property</li>
      <li>A shuttle between the ceremony and the party</li>
      <li>A room that opens at four and closes at eleven</li>
      <li>A tent, or a fee to move indoors</li>
      <li>A vendor you have to find yourself</li>
      <li>A room number</li>
    </ul>
    <p class="close">Everything on that list is where the stress comes from. It is simply
       not here.</p>
  </div>
</section>

<section>
  <div class="split flip">
    {{img:wk-dawn.webp|A suite on the estate in the morning}}
    <div class="split-text">
      <div class="eyebrow">No travel, no rush</div>
      <h2>You arrive once.</h2>
      <p>You wake up where you are getting married. Hair can start at five, because the
         aisle is a short walk from the room you slept in. Guests walk from the ceremony to
         the deck to dinner; nobody drives between anything, and nobody starts looking for
         their keys at eleven.</p>
      <p>Your family is not at a hotel by the interstate. They are up the hill, and they
         come down for breakfast. Fifteen minutes from downtown Chattanooga, six from a
         hotel for anyone who needs one, thirty from the airport.</p>
      <a class="btn" href="/stay/">Where everyone sleeps</a>
    </div>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">Everything is thought of</div>
    <h2>Bring your people. The rest is here.</h2>
    <p>Tables, chairs, linens and thirty thousand dollars of decor are already on the
       property. The kitchen is ours. The crew that sets up, clears, drives the carts and
       parks the cars has done it here hundreds of times. And the person designing the day
       is trained to design how a moment feels.</p>
  </div>
  <div class="grid">
    <article class="card">
      {{img:inc-food.webp|Copper mugs and a garnished cocktail on a wooden board|class="wipe"}}
      <div class="eyebrow">The kitchen</div>
      <h3>Catering, from here.</h3>
      <p>Food actually cooked on the estate, by a kitchen that works it every weekend
         &mdash; from the rehearsal dinner to breakfast on Sunday.</p>
    </article>
    <article class="card">
      {{img:w-premium.webp|Bridesmaids beside tall floral arrangements at golden hour|class="wipe"}}
      <div class="eyebrow">The design</div>
      <h3>Built around you, by Kobi.</h3>
      <p>There is no standard floor plan. Yours is drawn with you by a designer trained at
         SCAD and Disney to think about what a guest feels, not only what a room looks
         like. <a href="/about/">Meet Kobi</a>.</p>
    </article>
    <article class="card">
      {{img:inc-glass.webp|The conservatory inside, chandeliers over the floor|class="wipe"}}
      <div class="eyebrow">The weather</div>
      <h3>It rained, and nothing changed.</h3>
      <p>Glass, cover and the whole property to move into. No tent, no five o&rsquo;clock
         panic, no flip fee. <a href="/weddings/whats-included/">Everything that is
         included</a>.</p>
    </article>
  </div>
</section>

<section class="band">
  {{img:band-family.webp|A couple walking together in the meadow|class="band-img"}}
  <p>Everyone here will call you by your first name.</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">Not a number</div>
    <h2 class="rise-words"><span>You</span> <span>are</span> <span>not</span> <span>a</span> <span>Saturday.</span> <span>You</span> <span>are</span> <span>a</span> <span>name.</span></h2>
    <p>This is a family estate, not a sales office. The people who answer your first
       message are the people who will be on the property at eleven at night on your
       Saturday. By the rehearsal they will know your mother&rsquo;s name too, and which
       cousin needs to be nowhere near the speakers.</p>
    <p class="close">The estate will grow. Nobody who marries here will ever be a room
       number.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A mother settling her daughter&rsquo;s veil before the ceremony"
       style="background-image:url('/assets/img/close-tour.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">When you are ready</div>
    <h2>Let&rsquo;s talk about yours.</h2>
    <p>Tell us a little about the two of you and the day you are imagining. A person writes back, by name, and the visit comes whenever it suits you.</p>
    <a class="btn" href="/inquire/">Speak with our team</a>
  </div>
</section>
""")

PAGES["404.html"] = dict(
    nav=None, title="Not found | %s" % SITE,
    desc="That page is not here.",
    hero_img="band-quiet.webp",
    hero_alt="The meadow from above, the ceremony arch small in the middle of it",
    eyebrow="404",
    h1="There is nothing at this address.",
    standfirst="Which is rather the point of the place, but not what you were "
               "looking for. Everything on the estate is one of these.",
    actions=[("Back to the beginning", "/"),
             ("Speak with our team", "/inquire/")],
    body="""
<section>
  <div class="lede">
    <h2>Where you might have been going</h2>
  </div>
  <ul class="named">
    <li><a href="/weddings/">Weddings</a> <span>The Estate Weekend</span></li>
    <li><a href="/weddings/whats-included/">What&rsquo;s included</a> <span>And what happens if it rains</span></li>
    <li><a href="/weddings/real-weddings/">Real weddings</a> <span>Weddings that happened here</span></li>
    <li><a href="/stay/">Stay</a> <span>Lodging on the estate</span></li>
    <li><a href="/the-estate/">The Estate</a> <span>Six places and the walk between them</span></li>
    <li><a href="/planners/">For planners</a> <span>How a weekend runs</span></li>
    <li><a href="/about/">About</a> <span>The family, and the question behind every room</span></li>
    <li><a href="/inquire/">Speak with our team</a> <span>Start with a conversation</span></li>
  </ul>
</section>
""")


# --------------------------------------------------------------------- write
# Every stylesheet and script link carries a short hash of the file it points
# at. GitHub Pages serves assets with a ten-minute cache; without this a fix
# to opening.css is invisible to anyone who looked at the site in the last ten
# minutes, and during launch week that is everyone who matters. The hash only
# changes when the file does, so unchanged assets stay cached.
import hashlib
ASSET_LINK = re.compile(r'((?:href|src)="/assets/[a-z0-9-]+\.(?:css|js))"')
_digest = {}
def version_assets(html):
    def stamp(m):
        rel = m.group(1).split('"')[1]
        if rel not in _digest:
            with open(os.path.join(ROOT, rel.lstrip("/")), "rb") as f:
                _digest[rel] = hashlib.md5(f.read()).hexdigest()[:8]
        return '%s?v=%s"' % (m.group(1), _digest[rel])
    return ASSET_LINK.sub(stamp, html)

for path, page in PAGES.items():
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    html = version_assets(shell(page, path))
    open(dest, "w", encoding="utf-8").write(html)
    print("%-44s %5d bytes" % (path, len(html)))

print("\n%d pages" % len(PAGES))
