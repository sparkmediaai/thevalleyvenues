"""
Build the prototype site.

Eleven pages share one header, one footer and one stylesheet. Writing them by
hand would mean changing the navigation in eleven places the first time it
moves, and it will move — the structure is a proposal, not a decision. So the
pages are data and the shell is code.

Run:  python _build/build.py
"""
import json, os, re, struct
from datetime import datetime, timezone

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

# The address the site is actually for. While BASE is anything else this is a
# staging copy of a real business's website, sitting on a public host with its
# real prices and its real phone number on it, and it asks search engines to
# stay away. Point BASE at the line below and that request disappears on its
# own -- which is the point, because "remember to take the noindex off" is not
# a plan, it is a thing somebody forgets on launch day.
PRODUCTION = "https://thevalleyvenues.com/"

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
    ("Gallery", "/gallery/"),
    ("About", "/about/"),
]
CTA = ("Download the Wedding Pamphlet", "/pricing/")

FOOTER = [
    ("Celebrate", [
        ("Pricing &amp; the pamphlet", "/pricing/"),
        ("The Difference", "/the-difference/"),
        ("The Estate Weekend", "/weddings/"),
        ("What's Included", "/weddings/whats-included/"),
        ("The Gallery", "/gallery/"),
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
        ("The Lodge", "/the-estate/the-lodge/"),
        ("Lost in the Woods", "/the-estate/lost-in-the-woods/"),
    ]),
    ("The Valley Venues", [
        ("About &amp; Kobi", "/about/"),
        ("Speak with our team", "/inquire/"),
        ("Pricing", "/pricing/"),
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
%(robots)s<link rel="icon" href="%(root)sassets/favicon.svg" type="image/svg+xml">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Libre+Franklin:wght@400;500;600&family=Libre+Caslon+Display&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Jost:wght@400;500&display=swap">
<link rel="stylesheet" href="%(root)sassets/site.css">
<link rel="stylesheet" href="%(root)sassets/motion.css">
<link rel="stylesheet" href="%(root)sassets/opening.css">
<link rel="stylesheet" href="%(root)sassets/forms.css">
%(head)s<link rel="stylesheet" href="%(root)sassets/spa.css">
<link rel="stylesheet" href="%(root)sassets/olive.css">
<script>document.documentElement.classList.add("js");if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches){document.documentElement.classList.add("io");setTimeout(function(){if(!window.__reveal)document.documentElement.classList.remove("io")},3000)}window.FORM_ENDPOINT=%(endpoint)s;if(/[?&]notes\b/.test(location.search))document.documentElement.classList.add("notes")</script>
</head>
<body data-page="%(page_id)s">

<a class="skip" href="#main">Skip to content</a>

<header class="site-head">
  <div class="inner">
    <a class="wordmark" href="%(root)s"><img src="%(root)sassets/logo-mark.webp" alt="" width="240" height="240" decoding="async"><span>%(site)s</span></a>
    <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="site-nav"><span class="nav-bars" aria-hidden="true"><i></i><i></i></span><span class="nav-word">Menu</span></button>
    <nav class="site-nav" id="site-nav" aria-label="Primary">
      <ul>
%(nav)s
      </ul>
    </nav>
    <a class="btn btn-solid" href="%(cta_href)s">%(cta_text)s</a>
  </div>
</header>
%(banner)s
<header class="hero %(hero_class)s">
%(hero)s%(hero_body)s</header>

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
%(cta_bar)s%(foot_js)s
<script src="%(root)sassets/nav.js" defer></script>
<script src="%(root)sassets/vendor/gsap.min.js" defer></script>
<script src="%(root)sassets/vendor/ScrollTrigger.min.js" defer></script>
<script src="%(root)sassets/motion-og.js" defer></script>
<script src="%(root)sassets/reveal.js" defer></script>
<script src="%(root)sassets/opening.js" defer></script>
<script src="%(root)sassets/forms.js" defer></script>
</body>
</html>
""" % {
        "title": page["title"], "desc": page["desc"], "root": depth_root,
        "url": url, "base": BASE,
        "endpoint": json_str(FORM_ENDPOINT),
        "robots": "" if BASE == PRODUCTION else
                  '<meta name="robots" content="noindex,nofollow">' + chr(10),
        "site": SITE, "nav": nav, "cta_href": CTA[1], "cta_text": CTA[0],
        # On a phone the pamphlet button lives in a bar at the foot of the
        # screen instead of the header. Not on the page the button leads to.
        "cta_bar": "" if path.startswith("pricing/") else
                   '<div class="cta-bar"><a class="btn btn-solid" href="%s">%s</a></div>\n' % (CTA[1], CTA[0]),
        "hero": hero, "eyebrow": page["eyebrow"], "h1": page["h1"],
        "standfirst": page["standfirst"], "actions": actions,
        # A page can leave the words out of its hero when its body opens with
        # its own heading (that heading is then the page's h1).
        "hero_body": "" if page.get("hero_text") is False else
                     '  <div class="hero-body">\n    <div class="eyebrow">%s</div>\n    <h1>%s</h1>\n'
                     '    <p>%s</p>%s\n  </div>\n' % (page["eyebrow"], page["h1"], page["standfirst"], actions),
        "body": expand(page["body"]), "foot": foot,
        "hero_class": hero_class,
        "page_id": (path.replace("/index.html", "").replace(".html", "").replace("/", "-")
                    if path != "index.html" else "home"),
        "banner": page.get("banner", OPENING),
        "head": page.get("head", ""), "foot_js": page.get("foot_js", ""),
    }


# ---------------------------------------------------------------- the pages
PAGES = {}

# --------------------------------------------------------------- Instagram
# The estate's own posts, pulled on a schedule by _tools/instagram.py and
# served from this repo like any other photograph -- no embed script, no
# third-party cookies, and the frames are cut to the site's own square.
#
# A feed that has gone quiet reads worse than no feed at all, so the section
# hides itself if the newest post is older than STALE_DAYS or if there are
# fewer than three to show. Before the account is connected there is no file
# at all, and the page is simply shorter.
STALE_DAYS = 75


def instagram_section():
    path = os.path.join(ROOT, "assets", "instagram.json")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        feed = json.load(f)
    posts = feed.get("posts", [])[:8]
    if len(posts) < 3:
        return ""
    newest = max((p.get("timestamp", "") for p in posts), default="")
    try:
        when = datetime.strptime(newest[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return ""
    age = (datetime.now(timezone.utc) - when).days
    if age > STALE_DAYS:
        print("  instagram: newest post is %d days old, section hidden" % age)
        return ""

    frames = []
    for p in posts:
        label = p.get("caption") or "A post from the estate"
        frames.append(
            '    <a class="ig-frame%s" href="%s" target="_blank" rel="noopener">\n'
            '      <img src="/assets/img/ig/%s" alt="%s" width="900" height="900" loading="lazy" decoding="async">\n'
            '      <span class="ig-cap">%s</span>\n'
            '    </a>' % (" ig-video" if p.get("video") else "", p.get("permalink", ""),
                          p["img"], esc(label), esc(label)))
    return ('\n<section class="social">\n'
            '  <div class="lede">\n'
            '    <div class="eyebrow">Lately</div>\n'
            '    <h2>The last few weeks, as they happened.</h2>\n'
            '    <p>Posted by the estate, straight from the property.</p>\n'
            '  </div>\n'
            '  <div class="ig-grid">\n%s\n  </div>\n'
            '  <a class="ig-follow" href="%s" target="_blank" rel="noopener">@%s on Instagram</a>\n'
            '</section>\n' % ("\n".join(frames), feed.get("profile", ""), feed.get("handle", "")))


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


PAGES["index.html"] = dict(
    nav=None, title="%s | %s" % (SITE, TAGLINE), desc=TAGLINE,
    head='<link rel="stylesheet" href="/assets/home.css">\n'
         '<link rel="stylesheet" href="/assets/social.css">\n'
         '<link rel="preload" as="image" href="/assets/video/hero-poster.webp"\n'
         '      imagesrcset="/assets/video/hero-poster-sm.webp 720w, /assets/video/hero-poster.webp 1600w"\n'
         '      imagesizes="100vw">\n',
    foot_js='<script src="/assets/home.js" defer></script>',
    hero_html=(
        '  <div class="hero-stage">\n'
        # The poster is a real image with its own srcset, so a phone fetches the
        # small one and the page has something to paint before the video arrives.
        '    <img class="hero-poster" src="/assets/video/hero-poster.webp" '
        'srcset="/assets/video/hero-poster-sm.webp 720w, /assets/video/hero-poster.webp 1600w" sizes="100vw" '
        'alt="The meadow set for a ceremony, white chairs and the arch, seen from the air" '
        'width="1600" height="776" fetchpriority="high" decoding="async">\n'
        # No autoplay attribute: home.js starts it, so reduced motion and no-JS
        # both keep the still. Sources are chosen by width in the script too.
        '    <video class="hero-video" muted loop playsinline preload="none" aria-hidden="true" '
        'data-sm="/assets/video/hero-sm.mp4" data-webm="/assets/video/hero.webm" '
        'data-mp4="/assets/video/hero.mp4"></video>\n'
        '    <button type="button" class="hero-pause" aria-pressed="false" hidden>'
        '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
        '<path class="i-pause" d="M5 3v10M11 3v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<path class="i-play" d="M5 3l8 5-8 5z" fill="currentColor"/></svg>'
        '<span>Pause film</span></button>\n'
        '  </div>\n'),
    eyebrow="Wildwood, Georgia &middot; Fifteen minutes from downtown Chattanooga",
    h1="All yours, uninterrupted.",
    standfirst="A private world beneath Lookout Mountain, unfolding across seventy-four "
               "secluded acres fifteen minutes from downtown Chattanooga. Every space on it "
               "is yours, and only yours, for as long as your celebration lasts.",
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("Walk the Estate", "/the-estate/")],
    body="""
<section>
 <div class="stakes">
  <div class="lede reveal">
    <div class="eyebrow">Why any of this matters</div>
    <h2>One of the most beautiful days of your life.</h2>
    <p>It is also one of the rare moments when nearly everyone you love gathers in one
       place. Parents and grandparents. Childhood friends and college roommates. Brothers
       and sisters. People who scattered across the country and have not shared a room in
       years.</p>
    <p>A gathering this precious deserves more than a handful of scheduled hours. It
       deserves room to breathe, to linger over long conversations, to laugh late into the
       evening and wake together to the mountain. Every corner of this estate exists for
       that one purpose.</p>
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
    <p>Many of the region&rsquo;s larger estates welcome two or three weddings in a
       single day, each couple sharing the grounds with another. Yours is given
       something rarer: an entire estate devoted to one celebration. Every flower,
       every toast, every whispered promise unfolds for you alone, against the
       mountain, shared only with the people you hold dearest.</p>
    <ul class="nots">
      <li>Yours is the only wedding on the property</li>
      <li>Every space prepared around your vision</li>
      <li>Every conversation private, every moment savored</li>
      <li>Every field, every porch, every bed</li>
    </ul>
    <p class="close">For as long as your celebration lasts, the only people on
       seventy&#8209;four acres are the ones you invited.</p>
    <a class="btn" href="/the-difference/">Why that changes everything</a>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The weekend</div>
    <h2>More than a wedding day.</h2>
    <p>When a celebration deserves more than a single day, the whole weekend becomes
       yours: shared meals, quiet mornings and golden evenings beneath the mountain, with
       everyone you love close at hand from the first welcome to the last embrace.</p>
  </div>
  <ol class="weekend">
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-arrive.webp" alt="Magnolia House from the foot of its front steps" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">The arrival</span>
      <b>You arrive once</b>
      <p>Through the gate, and for the next two days this is simply where you are.
         Familiar faces arrive one hug at a time, until the people you love most are
         around one long table, laughing like they were never apart.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-morning.webp" alt="A bride smiling into the mirror of the getting ready suite" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Getting ready</span>
      <b>There is no commute in a wedding dress</b>
      <p>You wake to light spilling over Lookout Mountain, coffee already warm and your
         closest friends drifting in. Hair can start at five, and your gown waits in the
         next room, steps from where you will say I do.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-golden.webp" alt="A couple laughing in an embrace on the Lookout Deck in the evening light" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Golden hour</span>
      <b>The mountain turns gold</b>
      <p>As evening settles over the valley, the ridge begins to glow. Guests come up
         from the ceremony, glasses rise, conversations soften, and the light pours
         across the mountain for about half an hour.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-after.webp" alt="A couple walking hand in hand across the misty meadow the next morning" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">The farewell</span>
      <b>Goodnight instead of goodbye</b>
      <p>When the last song ends, everyone you love strolls up the hill to bed. Two
         nights means three mornings, and the last of them is a long breakfast together
         rather than a parking lot.</p>
    </li>
  </ol>
</section>

<section>
  <div class="lede reveal">
    <div class="eyebrow">Everyone stays</div>
    <h2>Nobody drives home.</h2>
    <p>Cottages, suites and a lodge for the whole wedding party are tucked across the
       estate, each with a name rather than a number, with beds for thirty-four of your
       nearest. Instead of a late drive to a hotel by the interstate, your family strolls
       up the hill, and by morning they drift back down for breakfast with the mountain
       glowing beyond the porch.</p>
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

%(instagram)s
<section class="closing">
  <div class="closing-img" role="img" aria-label="A cottage in the woods, lit at night"
       style="background-image:url('/assets/img/close-woods.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">And then</div>
    <h2>Where your forever begins.</h2>
    <p>At the far edge of the estate, where the trees close in, a private cottage waits.
       The night before, it gathers your wedding party around the fire. The night after,
       it belongs to the two of you alone &mdash; a soaking tub, a fountain under the
       stars, and thirty seconds between you and everyone you love.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""" % dict(instagram=instagram_section()))


# ------------------------------------------------------ gallery photographs
# Photographs from the gallery, by id, with a srcset over its two web sizes.
# The web files are 1600px on the long edge, and 640px for the small one.
_GALLERY = {}


def gpic(pid, alt, cls="", sizes="(max-width:760px) 100vw, 50vw", eager=False, style=""):
    if not _GALLERY:
        with open(os.path.join(ROOT, "assets", "gallery.json"), encoding="utf-8") as f:
            for g in json.load(f):
                _GALLERY[g["id"]] = g
    g = _GALLERY[pid]
    k = 1600.0 / max(g["w"], g["h"])
    w, h = round(g["w"] * min(k, 1)), round(g["h"] * min(k, 1))
    sm = 640.0 / max(g["w"], g["h"])
    return ('<img src="/assets/gallery/%(id)s.webp" srcset="/assets/gallery/%(id)s-sm.webp %(sw)dw, '
            '/assets/gallery/%(id)s.webp %(w)dw" sizes="%(sizes)s" alt="%(alt)s" width="%(w)d" height="%(h)d"'
            '%(cls)s%(style)s loading="%(load)s" decoding="async">' % dict(
                id=pid, sw=round(g["w"] * min(sm, 1)), w=w, h=h, sizes=sizes, alt=alt,
                cls=' class="%s"' % cls if cls else "", style=' style="%s"' % style if style else "",
                load="eager" if eager else "lazy"))


def words(text):
    """Each word in its own span, for the line that fills as it is read."""
    return " ".join("<span>%s</span>" % w for w in text.split())


# No photograph of Magnolia House from before the May 2025 fire: it does not
# look like that any more. Every gallery photograph predates the fire.
# The Weddings page is the chosen direction (the wedding lab's 11): the estate
# film at full screen with the headline on a parchment band across its foot,
# then Olive Grove's large blocks. Short on purpose -- most visitors arrive from
# Instagram on a phone.
WAYS = [
    ("Single Day Celebration", "One day",
     "The whole estate devoted to your wedding day, from the first flower placed to the final farewell.",
     "/weddings/single-day/", "aybee-dominy-3700", "A bride and groom walking back up the aisle in the meadow"),
    ("The Estate Weekend", "Two nights",
     "The celebration begins the evening before, with your rehearsal dinner set and waiting, and two nights on the estate.",
     "/stay/", "copy-of-dsc05971-arw-1", "A couple at a picnic breakfast laid in the meadow"),
    ("All-Inclusive Estate Experience", "Everything handled",
     "One team brings it all together &mdash; design, coordination, catering, the bar and the music &mdash; with Kobi&rsquo;s own hand in the design.",
     "/weddings/whats-included/", "copy-of-the-valley-venues-kristen-thomison-photo-63",
     "A reception table dressed in blue and white"),
]

PAGES["weddings/index.html"] = dict(
    nav="Weddings", title="Weddings | %s" % SITE,
    desc="The Estate Weekend at The Valley Venues: one wedding, the whole property, for a day or a weekend.",
    head='<link rel="stylesheet" href="/assets/weddings.css">\n',
    hero_text=False,
    hero_html=(
        '  <div class="fh">\n'
        '    <figure class="fh-media">\n'
        '      <img src="/assets/video/hero-poster.webp" alt="" aria-hidden="true" fetchpriority="high">\n'
        '      <video autoplay muted loop playsinline preload="auto" poster="/assets/video/hero-poster.webp" aria-hidden="true">\n'
        '        <source media="(max-width:760px)" src="/assets/video/hero-sm.mp4" type="video/mp4">\n'
        '        <source src="/assets/video/hero.webm" type="video/webm">\n'
        '        <source src="/assets/video/hero.mp4" type="video/mp4">\n'
        '      </video>\n'
        '    </figure>\n'
        '    <div class="fh-band">\n'
        '      <div class="eyebrow">Weddings at The Valley Venues</div>\n'
        '      <h1>Where your love takes center stage.</h1>\n'
        '      <p>One celebration at a time, across seventy-four private acres beneath Lookout '
        'Mountain. For a single day or an entire weekend, the whole estate is devoted to the two '
        'of you and everyone you love.</p>\n'
        '      <a class="btn btn-solid" href="/pricing/">Download the Wedding Pamphlet</a>\n'
        '    </div>\n'
        '    <button type="button" class="fh-pause" aria-pressed="false">Pause film</button>\n'
        '  </div>\n'),
    eyebrow="Weddings", h1="Where your love takes center stage.", standfirst="",
    foot_js='<script>(function(){var v=document.querySelector(".fh video"),b=document.querySelector(".fh-pause");'
            'if(!v||!b)return;b.addEventListener("click",function(){if(v.paused){v.play();b.textContent="Pause film";'
            'b.setAttribute("aria-pressed","false");}else{v.pause();b.textContent="Play film";'
            'b.setAttribute("aria-pressed","true");}});})();</script>',
    body="""
<p class="og-line">The vows take moments. The memories last a lifetime.</p>

<section class="og-ways" aria-label="Three ways to celebrate">
%(ways)s
</section>

<section class="og-claim">
  <h2>Your wedding, the only one here.</h2>
  <p>One wedding on the property at a time, always. Every view, every path and every candlelit
     room is devoted to your celebration, shared only with the people you hold dearest. No
     second ceremony on the lawn, no reset between parties, nobody else&rsquo;s guests.</p>
</section>

<section class="og-book">
  <figure>%(aerial)s</figure>
  <div>
    <h2>Your dream, down to the last detail.</h2>
    <p>Every investment, every inclusion and every space, gathered in one guide. It comes to
       your email and your phone in about a minute.</p>
    <a class="btn btn-solid" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""" % dict(
        ways="\n".join(
            '  <article class="og-way">%s<div><div class="eyebrow">%s</div><h3>%s</h3><p>%s</p>'
            '<a href="%s">Discover</a></div></article>' % (
                gpic(img, alt, sizes="(max-width:820px) 100vw, 33vw"), kind, name, text, href)
            for name, kind, text, href, img, alt in WAYS),
        aerial=gpic("dji-0673", "The estate from the air, the meadow and the ridge in autumn",
                    sizes="(max-width:820px) 100vw, 50vw")),
)


PAGES["weddings/whats-included/index.html"] = dict(
    nav="Weddings", title="What's Included | %s" % SITE,
    desc="What comes with the estate, and what happens when the weather turns.",
    hero_img="included.webp", hero_alt="The conservatory at Magnolia House, glass on three sides",
    eyebrow="Celebrate &middot; What's included",
    h1="Everything your celebration deserves.",
    standfirst="Every question you and your family will ask: what comes with the estate, "
               "where your loved ones sleep, the plan for any sky, and who is responsible "
               "for what.",
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">The heart of it</div>
    <h2 class="rise-words"><span>The</span> <span>stage</span> <span>is</span> <span>set.</span> <span>The</span> <span>story</span> <span>is</span> <span>yours.</span></h2>
    <p>Most of what a wedding costs is not the wedding. It is the coordination
       of eleven separate companies who have never worked together, each with
       its own contract, its own arrival time and its own idea of where the
       power is.</p>
    <p class="close">Here the threads are already woven together: tables and
       linens waiting, decor from the estate&rsquo;s own collection, and the
       catering, setup, parking and coordination moving as one. Your part is
       the good part &mdash; the colors, the flowers, the music, and exactly
       how it should all feel.</p>
  </div>
</section>

<section>
  <div class="grid">
    <article class="card">
      {{img:inc-decor.webp|A long table laid with white linen, black chargers and greenery|class="wipe"}}
      <h3>Waiting to be styled</h3>
      <p>An extensive decor collection, with tables, chairs and linens, included rather
         than rented &mdash; so fewer details become their own vendor, their own invoice
         and their own phone call.</p>
    </article>
    <article class="card">
      {{img:inc-rain.webp|The conservatory from the lawn, glass on three sides|class="wipe"}}
      <h3>Rain or shine, still magic</h3>
      <p>Soaring glass, graceful cover and the whole estate to gather within, including the
         conservatory at Magnolia House. No tent. No five o'clock panic. No flip fee.</p>
    </article>
    <article class="card">
      {{img:inc-team.webp|The dance floor full, late in the evening|class="wipe"}}
      <h3>Every detail, quietly cared for</h3>
      <p>While you celebrate, the team tends to setup, cleanup, the golf carts, parking,
         security and coordination &mdash; people who have worked this property hundreds of
         times and know where the kitchen is.</p>
    </article>
    <article class="card">
      {{img:inc-food.webp|Copper mugs and a garnished cocktail on a wooden board|class="wipe"}}
      <h3>In-house catering</h3>
      <p>From the welcome bites to the final toast, menus are made to your taste and cooked
         here, by a kitchen that works this estate every weekend.</p>
    </article>
    <article class="card">
      {{img:inc-sleep.webp|The cottages of Overlook Village along the hillside|class="wipe"}}
      <h3>Everyone you love, close by</h3>
      <p>Beds for thirty-four across the cottages, the suites and the Lodge. A hotel is six
         minutes away for everyone else, and the airport is thirty.</p>
    </article>
    <article class="card">
      {{img:inc-yours.webp|An invitation suite, a ring dish and a bottle of scent|class="wipe"}}
      <h3>Every partner, one dream</h3>
      <p>Bring your planner and your vendors; our team will work alongside them. We would
         rather support your plan than replace it.</p>
    </article>
  </div>
</section>

<section>
  <div class="stakes flip">
    <div class="lede">
      <div class="eyebrow">For any sky</div>
      <h2>And if it rains?</h2>
      <p>Your celebration moves to the conservatory at Magnolia House, where the
         light comes in from three sides and the chandeliers hang over the
         floor. It is already part of the estate, so nothing is struck, nothing
         is tented and nothing costs extra &mdash; the wet-weather plan is a
         room you would have been happy to use anyway.</p>
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
    <div class="eyebrow">Your visit awaits</div>
    <h2>Some answers are meant to be felt.</h2>
    <p>Photographs show you the estate; a visit lets you feel it. Bring the questions your mother has been asking &mdash; they are usually the sharpest ones, and they are easier to answer standing in the room.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["weddings/real-weddings/index.html"] = dict(
    nav="Weddings", title="Real Weddings | %s" % SITE,
    desc="Weddings that have happened on the estate.",
    hero_img="rw-1.webp",
    hero_alt="Caitlin and Gupinder at the altar in the meadow, the wedding party either side",
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
    <figure>{{img:rw-2.webp|Caitlin and Gupinder marry in the meadow in autumn, the congregation seated toward the ridge}}</figure>
    <figure>{{img:rw-3.webp|Caitlin and Gupinder at the altar, the wedding party either side of them}}</figure>
    <figure>{{img:g-1.webp|The couple at the arch, the ridge behind them}}</figure>
    <figure>{{img:g-2.webp|A first look on the path, the valley beyond}}</figure>
    <figure>{{img:g-3.webp|The first dance under the drapery and lights}}</figure>
    <figure>{{img:g-4.webp|The couple on the drive, Lookout Mountain behind}}</figure>
    <figure>{{img:g-5.webp|The dance floor late, glow sticks up}}</figure>
    <figure>{{img:g-6.webp|The rehearsal table laid under the pergola}}</figure>
    <figure>{{img:g-7.webp|The wedding party walking down through the trees}}</figure>
    <figure>{{img:g-8.webp|The recessional back up the aisle}}</figure>
  </div>
  <p class="credit">Caitlin and Gupinder, in the meadow in autumn.</p>
  <div class="note">
    <p><b>Credits wanted.</b> The two autumn frames at the top are Caitlin and Gupinder&rsquo;s
       wedding on this estate. Still missing are their photographer and planner, which this
       page promises to name. The rest are estate frames, not credited weddings. The
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
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["weddings/single-day/index.html"] = dict(
    nav="Weddings", title="Single-Day Celebrations | %s" % SITE,
    desc="A single-day celebration on the estate.",
    hero_img="single-day.webp", hero_alt="The meadow, quiet, with the ridge beyond",
    eyebrow="Celebrate &middot; Single day",
    h1="One perfect day, entirely yours.",
    standfirst="Some love stories are told in a single day. From the morning light to the "
               "final farewell, the whole estate turns toward one couple.",
    body="""
<section>
  <div class="split">
    <div class="split-text">
      <h2>Everything you love, still yours</h2>
      <p>The estate is still held for one couple, with every space open to your
         celebration, every inclusion in place, shelter ready for any weather and the same
         people running it.</p>
      <h2 style="margin-top:1.5rem">Every moment, gathered into one day</h2>
      <p>Your celebration gathers into a single day, from the first look to the last dance.
         What the weekend adds is the rehearsal evening, two nights of lodging on the
         property, and a long breakfast together the morning after &mdash; which is to say,
         the parts most couples tell us afterwards they did not expect to love.</p>
      <a class="btn" href="/weddings/">See the Estate Weekend</a>
    </div>
    <figure class="frame">
      {{img:sd-fire.webp|The fire pit lit at golden hour, florals on either side|class="par"}}
    </figure>
  </div>
</section>

<section class="band">
  {{img:band-quiet.webp|The meadow from above, the arch small in the middle of it|class="band-img"}}
  <p>One day, one couple, and the whole estate devoted to you.</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">Always yours</div>
    <h2 class="rise-words"><span>A</span> <span>day</span> <span>as</span> <span>complete</span> <span>as</span> <span>your</span> <span>love.</span></h2>
    <p>Whether your celebration lasts a day or a weekend, the promise is the
       same: one wedding, one couple, the whole estate. There is still no
       second arch coming down at the far end of the field, and your day is
       given the same devotion as every celebration held here.</p>
    <p class="close">What you give up is the two nights, and most couples who
       have had them will tell you that is the part they would keep.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The ceremony set out and empty, under a heavy sky"
       style="background-image:url('/assets/img/close-single.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Choose your story</div>
    <h2>Find your fairy tale here.</h2>
    <p>Download the wedding pamphlet, compare the single day with the Estate Weekend, and see the investment for each. The moment you walk the estate, you will know which one is yours.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["the-estate/the-lodge/index.html"] = dict(
    nav="The Estate", title="The Lodge | %s" % SITE,
    desc="The wedding party's own building: two getting-ready suites, a kitchen built for a crowd, and fourteen beds.",
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='the-lodge.webp',
    hero_alt='The Mahogany Suite in the Lodge, the pool table under antler chandeliers',
    eyebrow='The Estate &middot; The Lodge &middot; Where the party stays',
    h1='The morning happens here.',
    standfirst='Two suites, a kitchen built for a crowd, and fourteen beds. The wedding party gets a building of its own, a walk from the hall.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">The morning</div>\n    <h2>Two suites, and nobody drives to a salon.</h2>\n    <p>The Willow Room is a private hair and makeup studio inside the building\n       everyone slept in: three stations, mirrors and lights along the wall, and\n       a sofa for whoever is next. The morning of a wedding is the part that\n       runs late when it is spread across a town, and here it is not spread at\n       all &mdash; the party wakes up, eats, and sits down in the next room.</p>\n    <p>The Mahogany Suite is the same building at the other end of the day: a\n       pool table, a card table and a seventy-inch screen, for the people who\n       are not finished at midnight and should not have to be quiet.</p>\n  </div>\n  <ul class="facts">\n    <li><span>The Willow Room</span>A private hair and makeup studio, for the morning of.</li>\n    <li><span>The Mahogany Suite</span>A pool table, a card table and a seventy-inch screen.</li>\n  </ul>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">The kitchen</div>\n    <h2>Built for a crowd, not for a couple.</h2>\n    <p>Two refrigerators, a double oven and an island long enough to work\n       around. It is the reason a party of fourteen can eat here without\n       anything being catered: supper the night before, breakfast together, and the\n       hour on the wedding morning when everyone wants coffee at once. Nothing on the\n       day itself happens in this building &mdash; the Lodge is where the party gets\n       ready and sleeps, and the celebration is down the hill.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">The beds</div>\n    <h2>Fourteen, under one roof.</h2>\n    <p>A primary suite with a king bed and its own bathroom, three more\n       bedrooms, and four full bathrooms &mdash; so the wedding party or the\n       largest family group stays together instead of being split between\n       cottages and a hotel in town. Outside there is a wraparound porch, a fire\n       pit, and the valley in front of it. Guests of the Lodge have the pool to\n       themselves.</p>\n    <p>Between Saturdays the Lodge is open as a <a href="/stay/">stay</a> on its\n       own terms, and it pairs with the <a href="/the-estate/overlook-village/">cottages</a>\n       when the group is larger than fourteen.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Sleeps</span>Fourteen. A primary suite with a king bed and ensuite, and three more bedrooms.</li>\n    <li><span>Bathrooms</span>Four, full.</li>\n    <li><span>The kitchen</span>Two refrigerators, a double oven, and an island to work around.</li>\n    <li><span>Outside</span>A wraparound porch, a fire pit, and the pool, which is the Lodge&rsquo;s alone.</li>\n    <li><span>Sits</span>On the drive between Overlook Village and Davis Hall, a walk from both.</li>\n  </ul>\n\n  <div class="note">\n    <p><b>Working note.</b> Everything above is the estate&rsquo;s own detail from the\n       live lodging page. The one gap is a photograph of the Lodge from outside:\n       every frame we hold is of the rooms, so the page leads with them.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>The Lodge, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:lg-1.webp|The Willow Room: three stations, mirrors and lights along the wall}}</figure>\n    <figure>{{img:lg-10.webp|The kitchen: a double oven, and an island to work around}}</figure>\n    <figure>{{img:lg-2.webp|The Mahogany Suite, the pool table under antler chandeliers}}</figure>\n    <figure>{{img:lg-11.webp|The dining room, laid for the whole party}}</figure>\n    <figure>{{img:lg-3.webp|The primary suite, a king bed under a carved headboard}}</figure>\n    <figure>{{img:lg-4.webp|A bedroom with two beds, green panelling and a wrought-iron headboard}}</figure>\n    <figure>{{img:lg-5.webp|Another bedroom, the window over the valley}}</figure>\n    <figure>{{img:lg-6.webp|A bathroom: twin mirrors, white tile and a walk-in shower}}</figure>\n    <figure>{{img:lg-12.webp|A double walk-in shower}}</figure>\n    <figure>{{img:lg-8.webp|A bathroom under lemon paper, green tile below}}</figure>\n    <figure>{{img:lg-9.webp|The pool, with the mountain behind it}}</figure>\n  </div>\n  <p class="credit">Photography by Alyssa Rachelle.</p>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/overlook-village/"><span>Before this</span><b>Overlook Village</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/lost-in-the-woods/"><span>On the walk, next</span><b>Lost in the Woods</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A sparkler lit outside a cottage after dark"\n       style="background-image:url(\'/assets/img/close-stay.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">The morning, and the small hours</div>\n    <h2>Everyone under one roof.</h2>\n    <p>Which is how the morning stays calm and the night runs late. Come and see it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-estate/lost-in-the-woods/index.html"] = dict(
    nav="The Estate", title="Lost in the Woods | %s" % SITE,
    desc="One cabin at the far edge of the property, with a fire pit and a terrace of its own — and room for fifty.",
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='lw-1.webp',
    hero_alt='The terrace at Lost in the Woods at dusk, strung with lights',
    eyebrow='The Estate &middot; Lost in the Woods &middot; Its own small venue',
    h1='Lost in the Woods.',
    standfirst='One cabin at the far edge of the property, with a fire pit and a terrace of its own — and room for fifty. Small enough for the two of you, and enough of a place for fifty.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>A cabin at the far edge, and a place in its own right.</h2>\n    <p>Lost in the Woods sits away from everything else on the property, down the\n       drive past the meadow, where the trees close in. Inside: a king bed, a full\n       kitchen with a pull-out couch, and a walk-in shower and soaking tub under\n       the timber. Outside is the part people do not expect &mdash; an outdoor\n       kitchen and grill of its own, a fire pit sunk into the stone, a fountain\n       you hear before you see it, and a terrace strung with lights over the\n       valley.</p>\n    <p>That makes it more than a bed. It is where the wedding party gathers the\n       night before, and it holds a micro-wedding or an event of its own &mdash; up to\n       fifty guests, at the fire pit with the ridge behind them. It is also where the\n       two of you disappear to afterward &mdash;\n       married, alone, and thirty seconds from everyone you love.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Inside</span>A king bed, a full kitchen with a pull-out couch, a walk-in shower and a soaking tub.</li>\n    <li><span>Outside</span>Its own outdoor kitchen and grill, an in-ground fire pit, a fountain, and a terrace over the valley.</li>\n    <li><span>Holds</span>Up to fifty, for a micro-wedding or an event. The night before. The two of you afterward.</li>\n    <li><span>Sits</span>At the far edge of the property, off the west drive, on its own.</li>\n    <li><span>In all</span>Thirty-four beds on the estate, across the village, the Lodge and this.</li>\n  </ul>\n\n  </section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Lost in the Woods, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:lw-1.webp|The terrace at dusk, strung with lights above the rocks}}</figure>\n    <figure>{{img:lw-3.webp|The fire pit, and the valley beyond it}}</figure>\n    <figure>{{img:lw-2.webp|Inside: the living room under timber}}</figure>\n    <figure>{{img:lw-4.webp|The soaking tub, lights in the window behind it}}</figure>\n    <figure>{{img:lw-5.webp|A hammock on the grass, the ridge across the valley}}</figure>\n    <figure>{{img:lw-6.webp|The bedroom, the king bed under the boards}}</figure>\n    <figure>{{img:lw-7.webp|The kitchen, full-sized}}</figure>\n    <figure>{{img:lw-8.webp|The table on the deck, laid for a few}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/the-lodge/"><span>Before this</span><b>The Lodge</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <span></span>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A sparkler lit outside the cottage in the woods, after dark"\n       style="background-image:url(\'/assets/img/close-woods.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Afterward</div>\n    <h2>Thirty seconds away, and nobody can find you.</h2>\n    <p>Which is the point of putting it at the far edge. Come and see it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["stay/index.html"] = dict(
    nav="Stay", title="Stay | %s" % SITE,
    desc="Private mountainside lodging on a 74-acre estate near Chattanooga.",
    hero_img="stay.webp", hero_alt="A cottage in the woods at the edge of the property",
    eyebrow="Stay",
    h1="Stay Where the Story Continues",
    standfirst="The cottages are open when there is no wedding on the property. A creek, a "
               "waterfall, two and a half miles of trails, and the oldest mountain range on "
               "earth outside the door.",
    actions=[("Download the Wedding Pamphlet", "/pricing/")],
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
      <p>The Lodge takes the largest group, with the Willow Suite for hair and
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
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["the-estate/index.html"] = dict(
    nav="The Estate", title="The Estate | %s" % SITE,
    desc="Seventy-four acres beneath Lookout Mountain, as one property.",
    # The hero is the map itself. The page's argument is that the estate is one
    # place, and the drawing makes it before a word is read.
    hero_html='  <figure class="park-stage park-hero">\n'
              '    <div class="park-scroll">%s</div>\n'
              '    <button type="button" class="park-again" hidden>Play it again</button>\n'
              '  </figure>\n' % open(os.path.join(ROOT, "assets", "park-map.svg"), encoding="utf-8").read().strip(),
    head='<link rel="stylesheet" href="/assets/plan.css">\n'
         '<link rel="stylesheet" href="/assets/estate-park.css">\n',
    foot_js='<script src="/assets/estate-park.js" defer></script>',
    eyebrow="One estate &middot; Seventy-four acres",
    h1="One estate, and every space in it yours.",
    standfirst="Your celebration takes in the whole of it, from the sunlit meadow to the "
               "historic white house and the deck that turns gold at dusk. Hover a place "
               "on the map to see it, or touch it to wander there.",
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">An enchanted world</div>
    <h2 class="rise-words"><span>Connected</span> <span>by</span> <span>design,</span> <span>devoted</span> <span>to</span> <span>you.</span></h2>
    <p>Ask most estates which space you are getting and they will tell you. Here it is the
       wrong question. Magnolia House opens into its own grounds, Davis Hall opens onto the
       Lookout Deck with The Valley below, and every one of them is yours for the
       celebration.</p>
    <p class="close">Where you marry, where you dine and how the day unfolds is up to the two
       of you. Nobody else is on the property while you decide.</p>
  </div>
</section>

<section class="walk">
  <div class="lede">
    <div class="eyebrow">Places to fall in love</div>
    <h2>A world within the estate.</h2>
    <p>Each one is on the map above. Choose a place to wander in.</p>
  </div>
  <ul class="spots">
    <li class="spot">
      <a class="spot-link" href="/the-estate/magnolia-house/">
        <span class="spot-photo">{{img:magnolia-house.webp|Magnolia House, a couple on its front steps}}</span>
        <span class="spot-text">
          <span class="eyebrow">The historic house</span>
          <span class="spot-name">Magnolia House</span>
          <span class="spot-line">A historic white house framed by the mountain, with a glass conservatory behind it.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/the-valley/">
        <span class="spot-photo">{{img:the-valley.webp|The processional crossing the meadow}}</span>
        <span class="spot-text">
          <span class="eyebrow">The open meadow</span>
          <span class="spot-name">The Valley</span>
          <span class="spot-line">A sweeping meadow cradled by the ridgeline, with Lookout Mountain rising beyond.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/lookout-deck/">
        <span class="spot-photo">{{img:lookout-deck.webp|A couple dancing on the Lookout Deck, the ridge behind}}</span>
        <span class="spot-text">
          <span class="eyebrow">Davis Hall's wrap-around deck</span>
          <span class="spot-name">The Lookout Deck</span>
          <span class="spot-line">Wrapped around Davis Hall, where the valley falls away below and the ridge glows at dusk.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/davis-hall/">
        <span class="spot-photo">{{img:davis-hall.webp|Davis Hall under its drapery, lit for the first dance}}</span>
        <span class="spot-text">
          <span class="eyebrow">The grand hall</span>
          <span class="spot-name">Davis Hall</span>
          <span class="spot-line">Drapery and chandelier light, and the largest floor on the property.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/overlook-village/">
        <span class="spot-photo">{{img:stay-village.webp|The cottages of Overlook Village along the hillside}}</span>
        <span class="spot-text">
          <span class="eyebrow">The cottages on the hill</span>
          <span class="spot-name">Overlook Village</span>
          <span class="spot-line">Cottages along the hillside, where your loved ones rest just up the hill.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/the-lodge/">
        <span class="spot-photo">{{img:lg-1.webp|The Willow Room in the Lodge, three stations along the wall}}</span>
        <span class="spot-text">
          <span class="eyebrow">For your wedding party</span>
          <span class="spot-name">The Lodge</span>
          <span class="spot-line">Getting-ready suites, a kitchen for a crowd, and fourteen beds under one roof.</span>
        </span>
      </a>
    </li>
    <li class="spot">
      <a class="spot-link" href="/the-estate/lost-in-the-woods/">
        <span class="spot-photo">{{img:lw-3.webp|The fire pit at Lost in the Woods, the valley beyond it}}</span>
        <span class="spot-text">
          <span class="eyebrow">At the far edge</span>
          <span class="spot-name">Lost in the Woods</span>
          <span class="spot-line">Hidden at the edge of the woods: a cottage by the fire, made for two, with room for fifty.</span>
        </span>
      </a>
    </li>
  </ul>
</section>

<section class="band">
  {{img:band-ground.webp|The couple standing at the arch in the open meadow|class="band-img"}}
  <p>From the meadow to the mountain, all within reach.</p>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The lay of the land</div>
    <h2>See the estate from every angle.</h2>
    <p>The estate climbs two hundred and forty feet from the low ground to the
       ridge, which is why the views here feel endless. This is the same survey
       built as a model and turned, so the valley can be looked at from any
       side.</p>
    <a class="btn" href="/terrain/">Open the terrain model</a>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A bride at the deck rail, looking out at the mountain"
       style="background-image:url('/assets/img/close-estate.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Walk the estate</div>
    <h2>A beauty best discovered in person.</h2>
    <p>In person the estate reveals itself slowly: the quiet of the meadow, the walk between one moment and the next, and the deck turning gold at six. Download the wedding pamphlet and start planning your visit.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["about/index.html"] = dict(
    nav="About", title="About | %s" % SITE,
    desc="The family behind the estate, and the design thinking behind the experience.",
    # No hero photograph: this page is about a person, and her portrait is the
    # first picture on it.
    head='<link rel="stylesheet" href="/assets/about.css">\n',
    eyebrow="About",
    h1="A family devoted to your moment.",
    standfirst="Driven by a passion for extraordinary moments, the family behind The Valley "
               "Venues designs every celebration around one question: how you and the people "
               "you love will feel.",
    body="""
<section>
 <div class="kobi">
  <figure class="kobi-photo">
    {{img:kobi.webp|Kobi Cummings, smiling, lighting candles on a reception table}}
    <figcaption>Kobi Cummings</figcaption>
  </figure>
  <div class="lede">
    <div class="eyebrow">Kobi Cummings</div>
    <h2>Be our guest.</h2>
    <p>Every celebration here begins with a dream, and yours is placed in the hands of
       someone who has spent her career making them real. Kobi Cummings, co-founder of The
       Valley Venues and a certified wedding planner, holds a Bachelor of Fine Arts in
       production design from the Savannah College of Art and Design, with a minor in
       themed entertainment.</p>
    <p>That took her to Disney Live Entertainment as an arts specialist, designing props
       for live shows and parades in front of Cinderella Castle &mdash; work built around
       one question. <em>What should the guest feel in this moment?</em> The same question
       is now asked of this estate: of the moment the doors open and everyone turns around,
       and of whoever sits closest to the dance floor, who will be in every photograph of
       your first dance and should be someone you love.</p>
    <p class="kobi-quote">&ldquo;We are committed to ensuring that every memory created at
       The Valley Venues becomes a timeless and unforgettable fairy tale experience for all
       who visit.&rdquo;<span>Kobi Cummings</span></p>
  </div>
 </div>
</section>

<section class="band">
  <img class="band-img" src="/assets/gallery/copy-of-the-valley-venues-kristen-thomison-photo-225.webp"
       alt="A couple forehead to forehead on the Lookout Deck, guests seated behind them, the ridge beyond"
       width="1600" height="1067" loading="lazy" decoding="async">
  <p>Once upon a time begins the moment you arrive.</p>
</section>

<section>
 <div class="room">
  <figure class="room-photo">
    <img src="/assets/gallery/aybee-000084160025.webp"
         alt="A bride fastening an earring in a gilded mirror in the getting ready suite"
         width="1024" height="1545" loading="lazy" decoding="async">
  </figure>
  <div class="statement">
    <div class="eyebrow">The working method</div>
    <h2 class="rise-words"><span>Designed</span> <span>like</span> <span>a</span> <span>story,</span> <span>one</span> <span>scene</span> <span>at</span> <span>a</span> <span>time.</span></h2>
    <p>Themed entertainment design starts from the guest and works backwards.
       Not <em>what should this room look like</em> but <em>what should a person
       feel standing in it, at this hour, having just done the thing they came
       here to do.</em> So Kobi listens to the dream you have carried for years,
       then builds it moment by moment: the flowers, the music, the candlelight,
       and the way one space opens into the next.</p>
    <p class="close">It is why the seating chart matters more than the
       centerpieces, why the walk from the ceremony to the deck is a walk and
       not a shuttle, and why the last thing on the property is a cottage in the
       woods rather than a parking lot.</p>
  </div>
 </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">Rooted in love</div>
    <h2>Hospitality woven into our story.</h2>
    <p>Paul Cummings bought the property for another purpose entirely. Over time he and his
       daughter Kobi began restoring and reimagining it, and what emerged was not a
       collection of event spaces but a hospitality estate.</p>
    <p>Hospitality here is personal, warm and unhurried. The estate should grow without
       anyone becoming a room number: every couple is embraced as one of our own, long
       before the first toast and long after the last dance.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A mother settling her daughter's veil before the ceremony"
       style="background-image:url('/assets/img/close-about.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Your invitation</div>
    <h2>Let the magic begin.</h2>
    <p>Not a sales office: the people who answer the inquiry are the people who will be on the property at eleven at night on your Saturday. Tell us about the two of you, and Kobi and her team will start shaping a celebration as unforgettable as your love.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
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
        <label for="last_name">Last name <b aria-hidden="true">*</b></label>
        <input id="last_name" name="last_name" type="text" autocomplete="family-name" required>
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
      <label for="c_company">Company</label>
      <input id="c_company" name="company" type="text" tabindex="-1" autocomplete="off">
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
    <div class="eyebrow">Your next chapter</div>
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
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">Where the estate begins</div>\n    <h2>Not a rebuild. A rebirth.</h2>\n    <p>Magnolia House is the building the estate is known by, and it is the first\n       thing every guest sees &mdash; a hundred and seventy-five feet from the gate, at the top\n       of the drive, white columns against the ridge. It was raised in the 1890s.\n       In May 2025 a fire took the interior, and the family chose to bring it back\n       rather than replace it.</p>\n    <p>The front is restored to its history as closely as the record allows. The\n       columns you marry in front of are the original columns, saved from the fire\n       and standing again. Window frames and a wooden mantle from the old house\n       are back in the new one. And behind the house, where there was nothing\n       before, there is a conservatory &mdash; glass on three sides, Lookout\n       Mountain on the fourth, light all day &mdash; which is also the answer to\n       what happens if it rains: nothing is tented, nothing is struck, and nothing\n       costs extra.</p>\n    <p>Everything else on the property is arranged around it. You arrive here.\n       You marry in the meadow below it. You come back to it for dinner under\n       glass, and you walk up to the cottages from its door.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Built</span>The 1890s. Reborn in 2026, on the original footprint.</li>\n    <li><span>Holds</span>The ceremony, the reception, cocktails, and the rehearsal dinner the night before.</li>\n    <li><span>The conservatory</span>Glass on three sides, the mountain on the fourth. The weather plan that costs nothing.</li>\n    <li><span>The columns</span>Original, saved from the fire, and still what you stand in front of.</li>\n    <li><span>Where it sits</span>A hundred and seventy-five feet from the gate. The first photograph most guests take.</li>\n    <li><span>Then</span>Eight hundred and sixty feet, on foot, to the meadow.</li>\n  </ul>\n\n  <div class="note">\n    <p><b>Working note.</b> The live site still carries the rebuild page &mdash;\n       &ldquo;Coming 2026&rdquo;, pre-opening FAQs, reduced rates during construction.\n       None of it was carried over. The two frames marked &ldquo;as drawn&rdquo; are\n       architectural renderings; the finished house has not been photographed for\n       the site yet, and that is the first shoot to book.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Magnolia House, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:magnolia-house.webp|The house from the lawn, a couple on its front steps}}</figure>\n    <figure>{{img:inc-rain.webp|The conservatory from the lawn, glass on three sides}}</figure>\n    <figure>{{img:inc-glass.webp|The conservatory inside, chandeliers over the floor}}</figure>\n    <figure>{{img:mh-1.webp|The house from the drive, with the conservatory behind it, as drawn}}</figure>\n    <figure>{{img:close-weddings.webp|The conservatory lit from within after dark}}</figure>\n    <figure>{{img:mh-5.webp|The conservatory, glass on three sides, as drawn}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <span></span>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/the-valley/"><span>On the walk, next</span><b>The Valley</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The conservatory lit from within after dark"\n       style="background-image:url(\'/assets/img/close-weddings.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">After dark</div>\n    <h2>See it lit.</h2>\n    <p>The conservatory at night is the reason the house was rebuilt with glass.\n       Come and stand in it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-estate/the-valley/index.html"] = dict(
    nav="The Estate", title="The Valley | %s" % SITE,
    desc='An open meadow held on three sides by ridgeline, with Lookout Mountain beyond.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='the-valley.webp',
    hero_alt='The processional crossing the meadow toward the arch',
    eyebrow='The Estate &middot; The Valley &middot; Where you marry',
    h1='The meadow where it happens.',
    standfirst='An open meadow held on three sides by ridgeline, with Lookout Mountain beyond. Sound stays in it, the wind drops in it, and nothing is visible from it that the estate does not own.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>Held on three sides, open on the fourth.</h2>\n    <p>The Valley is the flat, open ground through the middle of the property, and\n       the hills around it are why it works. They keep the sound in and the wind\n       out, and they hold the last half hour of light after it has left the grass.\n       The fourth side is the mountain.</p>\n    <p>This is where you marry. It is also where the rehearsal happens the night\n       before, where cocktails can be poured under the sky, and where dinner can\n       be laid if the evening is the kind that wants to stay outside. Whatever is\n       set here is set for one couple: there is no second ceremony on the\n       property, and nobody&rsquo;s arch comes down while yours goes up.</p>\n    <p>It is eight hundred and sixty feet from the front door of Magnolia\n       House, and everyone walks it.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>The ceremony. The rehearsal. Cocktails and dinner under the sky when the evening allows.</li>\n    <li><span>Faces</span>Lookout Mountain, across the open side.</li>\n    <li><span>Held by</span>Ridgeline on three sides. Sound stays in, wind stays out.</li>\n    <li><span>Seats</span>Up to two hundred and fifty, in the meadow, facing the mountain.</li>\n    <li><span>If it rains</span>The conservatory at Magnolia House. No tent, no flip fee, no five o&rsquo;clock decision.</li>\n    <li><span>Then</span>A thousand feet, on foot, up to the deck &mdash; the longest walk of the weekend.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>The Valley, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:tv-1.webp|The ceremony in the meadow, the ridge behind the congregation}}</figure>\n    <figure>{{img:rw-3.webp|Caitlin and Gupinder at the altar in autumn, the wedding party either side}}</figure>\n    <figure>{{img:tv-2.webp|At the arch, the ridge behind}}</figure>\n    <figure>{{img:tv-3.webp|Seated toward the mountain}}</figure>\n    <figure>{{img:tv-4.webp|The recessional, petals in the air}}</figure>\n    <figure>{{img:tv-5.webp|The meadow from above, the arch small in the middle of it}}</figure>\n    <figure>{{img:tv-6.webp|Walking the meadow}}</figure>\n    <figure>{{img:tv-7.webp|Through the tall grass toward the arch}}</figure>\n    <figure>{{img:tv-8.webp|The creek at the foot of the meadow}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/magnolia-house/"><span>Before this</span><b>Magnolia House</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/lookout-deck/"><span>On the walk, next</span><b>Lookout Deck</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The ceremony set out and empty, under a heavy sky"\n       style="background-image:url(\'/assets/img/close-single.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Set, and waiting</div>\n    <h2>Nobody else is standing here.</h2>\n    <p>The meadow is arranged once, for you, and put away afterward. Walk it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-estate/lookout-deck/index.html"] = dict(
    nav="The Estate", title="Lookout Deck | %s" % SITE,
    desc='A railed deck out over the valley, facing Lookout Mountain.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='lookout-deck.webp',
    hero_alt='A couple dancing on the Lookout Deck, the ridge behind them',
    eyebrow='The Estate &middot; Lookout Deck &middot; Where the light goes',
    h1='Where the mountain turns gold.',
    standfirst='A railed deck out over the valley, facing Lookout Mountain. At six the light goes across it tip to tip, and everyone stops talking.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>The view no other estate in the region has.</h2>\n    <p>The deck is built out over the fall of the land, so the valley drops away\n       beneath the rail and the mountain fills everything beyond it. It is where\n       cocktails are poured after the ceremony &mdash; or where the ceremony itself is held, at the rail, with the mountain for a backdrop &mdash; where the first look tends to\n       happen in the morning, and where the wedding party ends up whenever nobody\n       has told them where to be.</p>\n    <p>Guests walk here from the meadow. It is a thousand feet,\n       the longest walk of the whole weekend, and it goes uphill toward the light\n       &mdash; which is the point. Nobody is shuttled, nobody is released in\n       groups, and nobody is looking for their keys.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>A ceremony at the rail, facing the mountain. Cocktail hour. The first look. Small dinners. Anything that wants the view.</li>\n    <li><span>Faces</span>Lookout Mountain and the evening light, across the whole width of the valley.</li>\n    <li><span>The hour</span>Gold at six, tip to tip, for about half an hour.</li>\n    <li><span>Seats</span>Up to a hundred and fifty for a ceremony, on fifteen thousand square feet of deck.</li>\n    <li><span>Sits</span>A thousand feet from the meadow. Six hundred and fifty from Davis Hall.</li>\n    <li><span>Then</span>Down to the hall for dinner, on foot, in the last of it.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Lookout Deck, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:ld-1.webp|The deck set for a ceremony, the mountain in autumn}}</figure>\n    <figure>{{img:ld-2.webp|At the arch on the deck}}</figure>\n    <figure>{{img:ld-3.webp|At the rail, in fog}}</figure>\n    <figure>{{img:ld-4.webp|A lounge at the rail, the mountain beyond}}</figure>\n    <figure>{{img:ld-5.webp|An arch at the rail, facing the ridge}}</figure>\n    <figure>{{img:ld-6.webp|The party, umbrellas up}}</figure>\n    <figure>{{img:ld-7.webp|At the rail}}</figure>\n    <figure>{{img:ld-8.webp|On the deck, the ridge behind}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/the-valley/"><span>Before this</span><b>The Valley</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/davis-hall/"><span>On the walk, next</span><b>Davis Hall</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A couple at the rail of the Lookout Deck, the ridge behind"\n       style="background-image:url(\'/assets/img/close-planners.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">At the rail</div>\n    <h2>Stand here at six.</h2>\n    <p>It does not photograph. That is why the tour exists. Come when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-estate/davis-hall/index.html"] = dict(
    nav="The Estate", title="Davis Hall | %s" % SITE,
    desc='Drapery, chandeliers, and the largest floor on the property.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='davis-hall.webp',
    hero_alt='Davis Hall under its drapery, lit for the first dance',
    eyebrow='The Estate &middot; Davis Hall &middot; Where you dine and dance',
    h1='The room where the dancing happens.',
    standfirst='Drapery, chandeliers, and the largest floor on the property. Dinner, the first dance, and everything after it &mdash; six hundred and fifty feet from the deck and a minute from bed.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">What it is</div>\n    <h2>Earned by the evening.</h2>\n    <p>Davis Hall is the room the weekend arrives at rather than the one it starts\n       in. Dinner is here. The first dance is here. The floor is the largest on the\n       estate and it carries the largest receptions the property holds, under\n       drapery and chandeliers, with the estate&rsquo;s own tables, chairs and\n       linens already in the room rather than on a truck.</p>\n    <p>It is six hundred and fifty feet from the deck, so the walk down happens in the last\n       of the light, and three hundred and twenty-five feet from the cottages, so the walk up\n       happens whenever you are ready and not when a shuttle is. Nobody leaves at\n       eleven because nobody has anywhere to drive to.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Holds</span>Dinner. The first dance. The largest receptions on the property.</li>\n    <li><span>Dressed</span>Drapery and chandeliers, and the estate&rsquo;s own tables, chairs and linens.</li>\n    <li><span>Seats</span>Up to two hundred and fifty.</li>\n    <li><span>Sits</span>Six hundred and fifty feet from the deck. Ninety-nine from the cottages.</li>\n    <li><span>After</span>Nobody drives. The cottages are up the hill and the night is yours.</li>\n  </ul>\n\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Davis Hall, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:dh-1.webp|The room set, drapery and the checkerboard floor, in daylight}}</figure>\n    <figure>{{img:dh-2.webp|Laid for dinner}}</figure>\n    <figure>{{img:dh-3.webp|The head table under the drapery}}</figure>\n    <figure>{{img:dh-4.webp|At the sweetheart table}}</figure>\n    <figure>{{img:dh-5.webp|The first dance, the party watching}}</figure>\n    <figure>{{img:dh-6.webp|Later}}</figure>\n    <figure>{{img:dh-7.webp|A centerpiece}}</figure>\n    <figure>{{img:dh-8.webp|A table, laid}}</figure>\n  </div>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/lookout-deck/"><span>Before this</span><b>Lookout Deck</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/overlook-village/"><span>On the walk, next</span><b>Overlook Village</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="The dance floor late in the evening, lit purple"\n       style="background-image:url(\'/assets/img/close-real.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Late</div>\n    <h2>Nobody is leaving.</h2>\n    <p>The room is yours until you are done with it. Come and stand in it when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-estate/overlook-village/index.html"] = dict(
    nav="The Estate", title="Overlook Village | %s" % SITE,
    desc='Four cottages along the hill, a lodge for the largest party, and one cottage in the woods for the two of you.',
    head='<link rel="stylesheet" href="/assets/plan.css">\n',
    hero_img='stay-village.webp',
    hero_alt='The cottages of Overlook Village along the hillside',
    eyebrow='The Estate &middot; Overlook Village &middot; Where everyone sleeps',
    h1='Where everyone sleeps.',
    standfirst='Four cottages along the hill, a lodge for the largest party, and one cottage in the woods for the two of you. Thirty-four beds, a minute from the end of the evening.',
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("The whole estate", "/the-estate/")],
    body='\n<section>\n  <div class="lede">\n    <div class="eyebrow">The village</div>\n    <h2>Four cottages, each turned to face out.</h2>\n    <p>Phoenix, Bluebird, Goldfinch and Hummingbird sit along the hill above the\n       hall, each one turned toward the view rather than toward the next, so nobody\n       is looking into anybody else&rsquo;s morning. Three sleep four and one sleeps\n       six &mdash; a queen bed and a queen pull-out in each &mdash; with a kitchenette\n       inside and a shared outdoor kitchen between them: a grill, a pizza oven, and\n       a hammock for whoever is done.</p>\n    <p>Private hot tubs are coming. Between Saturdays the village is open as a\n       <a href="/stay/">stay</a> on its own terms.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Cottages</span>Four. Phoenix, Bluebird, Goldfinch, Hummingbird.</li>\n    <li><span>Sleeps</span>Eighteen across the village. Three cottages sleep four, one sleeps six.</li>\n    <li><span>Inside</span>A queen bed, a queen pull-out, a kitchenette with a stovetop, fridge, microwave and dishwasher.</li>\n    <li><span>Between them</span>An outdoor kitchen with a grill and a pizza oven. A hammock. Hot tubs on the way.</li>\n    <li><span>Sits</span>Three hundred and twenty-five feet up the hill from Davis Hall, on foot.</li>\n  </ul>\n\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">The Lodge</div>\n    <h2>For the largest party, and the morning.</h2>\n    <p>Along the same drive, below the cottages, the Lodge takes the wedding party\n       or the biggest family group. The Willow Suite is a private hair and makeup\n       studio, so the morning starts where you slept and not in a car, and the\n       Mahogany Suite is for whoever is still up at one.\n       <a href="/the-estate/the-lodge/">See the Lodge</a>.</p>\n  </div>\n</section>\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">And then</div>\n    <h2><a href="/the-estate/lost-in-the-woods/">Lost in the Woods</a>.</h2>\n    <p>One cottage, tucked away at the far edge of the property, for the two of you.\n       A king bed. A full kitchen. A walk-in shower and a soaking tub. Outside, your\n       own kitchen and grill, a fire pit sunk into the ground, and a fountain you\n       will hear before you see. It is where the wedding party gathers the night\n       before, and where the two of you disappear to afterward &mdash; married,\n       alone, and thirty seconds from everyone you love.</p>\n  </div>\n  <ul class="facts">\n    <li><span>Lost in the Woods</span>One cottage. A king bed, a full kitchen, a walk-in shower and a soaking tub.</li>\n    <li><span>Outside</span>Your own kitchen and grill, an in-ground fire pit, a fountain.</li>\n    <li><span>In all</span>Thirty-four beds on the estate. A hotel is six minutes away for everyone else.</li>\n  </ul>\n\n  <div class="note">\n    <p><b>Where the direction and the live site differ.</b> The live site sells Lost in\n       the Woods as a bookable honeymoon suite. The direction document folds it into the\n       Estate Weekend as the emotional close rather than offering it separately, and\n       this page follows the direction. Bachelorette weekends are also sold on the live\n       site; the framework retires the word &ldquo;package&rdquo; in guest copy, so if\n       they stay, they are a <em>stay</em>.</p>\n  </div>\n</section>\n\n\n<section>\n  <div class="lede">\n    <div class="eyebrow">Seen</div>\n    <h2>Overlook Village, as it is.</h2>\n  </div>\n  <div class="gallery">\n    <figure>{{img:ov-1.webp|Overlook Village from above, the mountain behind}}</figure>\n    <figure>{{img:ov-2.webp|The cottages at dusk}}</figure>\n    <figure>{{img:ov-3.webp|Along the hill}}</figure>\n    <figure>{{img:ov-4.webp|Every cottage faces out: a chair at the window over the valley}}</figure>\n    <figure>{{img:ov-5.webp|The Mahogany Suite in the Lodge}}</figure>\n    <figure>{{img:ov-6.webp|A vanity with twin mirrors, in the Lodge}}</figure>\n    <figure>{{img:ov-7.webp|A soaking tub under the lights}}</figure>\n    <figure>{{img:ov-8.webp|Outside the cottage in the woods}}</figure>\n  </div>\n  <p class="credit">Photography by Christin Sofka.</p>\n</section>\n\n<nav class="onward" aria-label="Around the estate">\n    <a href="/the-estate/davis-hall/"><span>Before this</span><b>Davis Hall</b></a>\n    <a class="up" href="/the-estate/">The whole estate</a>\n    <a class="next" href="/the-estate/the-lodge/"><span>On the walk, next</span><b>The Lodge</b></a>\n</nav>\n\n<section class="closing">\n  <div class="closing-img" role="img" aria-label="A sparkler lit outside a cottage after dark"\n       style="background-image:url(\'/assets/img/close-stay.webp\')"></div>\n  <div class="closing-body">\n    <div class="eyebrow">Goodnight, not goodbye</div>\n    <h2>The party is a minute from bed.</h2>\n    <p>Which is the whole idea. Come and see the cottages when it suits you, or start with a conversation.</p>\n    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>\n  </div>\n</section>\n')

PAGES["the-difference/index.html"] = dict(
    nav="The Difference", title="The Difference | %s" % SITE,
    desc="Why one wedding at a time changes everything else: the whole estate, everything handled, and everyone knows your name.",
    hero_img="difference.webp",
    hero_alt="A couple on the Lookout Deck in the last of the light, the bride laughing",
    eyebrow="The Difference",
    h1="The whole estate, devoted to you.",
    standfirst="Seventy-four acres beneath Lookout Mountain, shared only with the people "
               "you invited. Everything you need is already here, every detail is handled, "
               "and everyone you meet will greet you by your first name.",
    actions=[("Download the Wedding Pamphlet", "/pricing/"),
             ("Walk the Estate", "/the-estate/")],
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">Peace of mind</div>
    <h2 class="rise-words"><span>Your</span> <span>wedding</span> <span>will</span> <span>feel</span> <span>like</span> <span>magic.</span></h2>
    <p>Everything your celebration needs already lives on this estate. Tables, linens and
       a decor library, ready to be styled to your vision. Rooms that are yours from the
       moment you arrive, and a timeline you write rather than inherit. One team, on one
       property, with a single purpose.</p>
    <p class="close">What is left is the celebration itself, and the two of you at the
       center of it.</p>
  </div>
</section>

<section>
  <div class="split">
    {{img:band-estate.webp|The estate from above, two people alone in the meadow}}
    <div class="split-text">
      <div class="eyebrow">One at a time</div>
      <h2>One estate. One celebration. Yours.</h2>
      <p>Larger estates around here run two or three weddings on a Saturday. This one
         holds one, and holds it for the weekend. The gate closes on Friday behind one
         family and does not open for anyone else until you leave.</p>
      <p>So every hour moves to your rhythm. The ceremony happens when the light is best,
         not when the room is free. The rehearsal happens where the vows will. Toasts
         last as long as the stories do, and the music runs as late as your people do.</p>
      <a class="btn" href="/the-estate/">Walk the Estate</a>
    </div>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">All included</div>
    <h2>A world made ready for two.</h2>
    <ul class="nots">
      <li>Every space on the estate, from the mountain views to the open meadow</li>
      <li>Linens, arches, backdrops and thirty thousand dollars of decor, styled to your vision</li>
      <li>Floor plans drawn around your celebration rather than around the room</li>
      <li>Shelter for any sky: glass, cover, and no fee to move indoors</li>
      <li>The estate&rsquo;s own kitchen, and the crew who set every scene</li>
      <li>Getting-ready suites, and golf carts for anyone who would rather ride than walk</li>
    </ul>
    <p class="close">And what you will not find: a second wedding, a shuttle, a room that
       closes at eleven, a tent fee, or a room number.</p>
  </div>
</section>

<section>
  <div class="split flip">
    {{img:wk-dawn.webp|A suite on the estate in the morning}}
    <div class="split-text">
      <div class="eyebrow">Steps from I do</div>
      <h2>Arrive once, then simply be.</h2>
      <p>The morning of your wedding begins a short walk from your vows. Hair can start at
         five, your friends gather close, and your gown waits in the next room. Guests
         drift from the ceremony to the deck to dinner on foot, or by golf cart if they
         would rather ride, and nobody starts looking for their keys at eleven.</p>
      <p>Your family is not at a hotel by the interstate. They are up the hill, and they
         come down for breakfast. Fifteen minutes from downtown Chattanooga, six from a
         hotel for anyone who needs one, thirty from the airport.</p>
      <a class="btn" href="/stay/">Where everyone sleeps</a>
    </div>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The art of the moment</div>
    <h2>Bring your people. The rest is here.</h2>
    <p>A wedding here is designed the way a story is told, scene by scene: the moment
       guests first step onto the grounds, the hush before the vows, the swell of laughter
       as glasses rise. Each one is imagined for how it will feel, then built around your
       vision &mdash; with thirty thousand dollars of decor already on the property, the
       estate&rsquo;s own kitchen, and a crew who have set this place hundreds of
       times.</p>
  </div>
  <div class="grid">
    <article class="card">
      {{img:inc-food.webp|Copper mugs and a garnished cocktail on a wooden board|class="wipe"}}
      <div class="eyebrow">The kitchen</div>
      <h3>Flavors made for the occasion.</h3>
      <p>Food actually cooked on the estate, by a kitchen that works it every weekend
         &mdash; from the rehearsal dinner to breakfast on Sunday, each course to your
         taste.</p>
    </article>
    <article class="card">
      {{img:w-premium.webp|Bridesmaids beside tall floral arrangements at golden hour|class="wipe"}}
      <div class="eyebrow">The design</div>
      <h3>Your vision, brought to life by Kobi.</h3>
      <p>There is no standard floor plan. Yours is drawn with you by a designer trained at
         SCAD and Disney to think about what a guest feels, not only what a room looks
         like. <a href="/about/">Meet Kobi</a>.</p>
    </article>
    <article class="card">
      {{img:inc-glass.webp|The conservatory inside, chandeliers over the floor|class="wipe"}}
      <div class="eyebrow">The weather</div>
      <h3>Beautiful in any weather.</h3>
      <p>Soaring glass, graceful cover, and the whole property to move into. No tent, no
         five o&rsquo;clock panic, no flip fee. <a href="/weddings/whats-included/">Everything
         that is included</a>.</p>
    </article>
  </div>
</section>

<section class="band">
  {{img:band-family.webp|A couple walking together in the meadow|class="band-img"}}
  <p>Everyone here will call you by your first name.</p>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">A family estate</div>
    <h2 class="rise-words"><span>The</span> <span>little</span> <span>things,</span> <span>remembered.</span></h2>
    <p>Every couple here is welcomed like family, and this is a family estate rather than
       a sales office. The people who answer your first message are the people who will be
       on the property at eleven at night on your Saturday. By the rehearsal they will know
       your mother&rsquo;s name, your favorite song, and which cousin needs to be nowhere
       near the speakers.</p>
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
    <p>It begins with a few words about the two of you. Tell us about the day you are
       imagining and a person writes back, by name, with the visit whenever it suits you.
       With one celebration at a time, the date you choose belongs to you alone.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""")

PAGES["pricing/index.html"] = dict(
    nav=None, title="Pricing | %s" % SITE,
    desc="The wedding pamphlet: every space on the estate, what comes with it, and "
         "what each experience costs. Sent to you by text and email.",
    hero_img="band-ground.webp",
    hero_alt="The arch standing alone in the open meadow, the ridge beyond it",
    eyebrow="Pricing",
    h1="Your celebration, in your hands.",
    standfirst="Every space on the estate, all that comes with it and each way to celebrate, "
               "in one guide, with the investment for every experience. Tell us where to send "
               "it and it is with you in a minute.",
    foot_js='<script src="https://link.msgsndr.com/js/form_embed.js"></script>',
    body="""
<section>
  <div class="split">
    <div class="split-text">
      <div class="eyebrow">What awaits you</div>
      <h2>The whole thing, not a teaser.</h2>
      <p>Every space on the estate and the moments it holds. The getting-ready suites.
         Every cottage, suite and lodge, and how many each one sleeps. What is included
         before you have hired anybody &mdash; tables, chairs, linens, the decor library,
         and the team who set it all up. The catering and bar menus. And the investment
         for every way to celebrate: a single day, the estate weekend, the all-inclusive
         experience, and micro weddings.</p>
      <p>It goes to your email and your phone, so it is still there when you are
         standing in a kitchen explaining it to somebody else.</p>
    </div>
    {{img:inc-glass.webp|The conservatory at Magnolia House from inside, chandeliers over the floor}}
  </div>
</section>

<section>
  <!-- The estate's own GoHighLevel form ("Pricing Pamphlet Capture Form"),
       embedded exactly as their current site embeds it, so every submission
       lands in their existing sub-account and fires the pamphlet workflow they
       already run (email, text, follow-up). It carries its own SMS consent
       checkbox and Cloudflare Turnstile check. Its fields and look are edited
       in GHL's form builder, not here. -->
  <div class="ghl-form">
    <p class="ghl-note">The pamphlet comes by text as well as email, which is why we ask for both.</p>
    <iframe src="https://api.leadconnectorhq.com/widget/form/MmcguxzmKTkCde4XaLrd"
            style="width:100%;height:100%;border:none;border-radius:0"
            id="inline-MmcguxzmKTkCde4XaLrd"
            data-layout="{'id':'INLINE'}"
            data-trigger-type="alwaysShow" data-trigger-value=""
            data-activation-type="alwaysActivated" data-activation-value=""
            data-deactivation-type="neverDeactivate" data-deactivation-value=""
            data-form-name="Pricing Pamphlet Capture Form"
            data-height="635"
            data-layout-iframe-id="inline-MmcguxzmKTkCde4XaLrd"
            data-form-id="MmcguxzmKTkCde4XaLrd"
            title="Pricing Pamphlet Capture Form"></iframe>
    <noscript><p class="ghl-note">If the form does not appear,
      <a href="https://api.leadconnectorhq.com/widget/form/MmcguxzmKTkCde4XaLrd">open it here</a>
      or email <a href="mailto:Info@thevalleyvenues.com">Info@thevalleyvenues.com</a>.</p></noscript>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A couple at the rail of the Lookout Deck, the ridge behind"
       style="background-image:url('/assets/img/close-planners.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">While you wait for it</div>
    <h2>Have a look around.</h2>
    <p>Six places on seventy-four acres, and the walk between them. It is the part of the pamphlet that reads better at full size.</p>
    <a class="btn" href="/the-estate/">Walk the estate</a>
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
             ("Download the Wedding Pamphlet", "/pricing/")],
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
    <li><a href="/about/">About</a> <span>The family, and the question behind every room</span></li>
    <li><a href="/inquire/">Speak with our team</a> <span>Start with a conversation</span></li>
  </ul>
</section>
""")


# ------------------------------------------------------------------ the gallery
# The photographs from the estate's current gallery, brought across by
# _tools/gallery_scrape.py with their photographers' credits and a place tag
# each. The wall is written into the page, so it is all there without
# JavaScript; gallery.js adds the filters' counts, the viewer and deep links.
GALLERY_PLACES = [
    ("valley", "The Valley"), ("magnolia", "Magnolia House"), ("deck", "Lookout Deck"),
    ("grounds", "The Grounds"), ("ready", "Getting Ready"), ("details", "The Details"),
    ("evening", "After Dark"),
]


def gallery_body():
    with open(os.path.join(ROOT, "assets", "gallery.json"), encoding="utf-8") as f:
        # Magnolia House was lost to fire in May 2025 and every photograph here
        # was taken before it, so none of the house is shown until new ones come.
        # The July 2024 Sara Kristen shoot was a Magnolia House session, so its
        # night frames at the brick gate go too.
        photos = [p for p in json.load(f) if "magnolia" not in p["tags"]
                  and not p["id"].startswith("sarah-kristen-photo-2024")]
    names = dict(GALLERY_PLACES)
    counts = {}
    for p in photos:
        for t in p["tags"]:
            counts[t] = counts.get(t, 0) + 1
    credits = []
    for p in photos:
        if p["credit"] and p["credit"] not in credits:
            credits.append(p["credit"])

    chips = ['<button type="button" class="gx-chip" data-place="" aria-pressed="true">'
             'All <span>%d</span></button>' % len(photos)]
    for key, label in GALLERY_PLACES:
        if counts.get(key):
            chips.append('<button type="button" class="gx-chip" data-place="%s" aria-pressed="false">'
                         '%s <span>%d</span></button>' % (key, label, counts[key]))
    options = "".join('<option value="%s">%s</option>' % (html_attr(c), c) for c in credits)

    tiles = []
    for i, p in enumerate(photos):
        where = " and ".join(names[t] for t in p["tags"])
        alt = "A wedding at The Valley Venues, %s" % where if p["tags"] != ["details"] else \
              "Wedding details at The Valley Venues"
        tiles.append(
            '    <a class="gx-item" href="/assets/gallery/%(id)s.webp" data-id="%(id)s" '
            'data-tags="%(tags)s" data-credit="%(credit)s" '
            'style="--r:%(r).4f;--tone:%(tone)s">'
            '<img src="/assets/gallery/%(id)s-sm.webp" alt="%(alt)s, photographed by %(credit)s" '
            'width="%(tw)d" height="%(th)d" loading="%(loading)s" decoding="async">'
            '<span class="gx-credit">%(credit)s</span></a>' % dict(
                id=p["id"], tags=" ".join(p["tags"]), credit=html_attr(p["credit"]),
                r=p["w"] / float(p["h"]), tone=p["tone"], alt=html_attr(alt),
                tw=640 if p["w"] >= p["h"] else round(640 * p["w"] / float(p["h"])),
                th=640 if p["h"] >= p["w"] else round(640 * p["h"] / float(p["w"])),
                loading="eager" if i < 8 else "lazy"))

    return """
<section class="gx-intro">
  <div class="lede">
    <div class="eyebrow">%(n)d photographs &middot; %(pn)d photographers</div>
    <h1>The estate, as the people who photograph it see it.</h1>
    <p>Every frame here was taken at a real wedding on this property, by a working
       wedding photographer. Choose a place to see only that part of the estate, or a
       photographer to see one eye across a whole day. Every photograph opens full size.</p>
  </div>
</section>

<section class="gx-section">
  <div class="gx-bar" role="group" aria-label="Filter the gallery">
    <div class="gx-chips">%(chips)s</div>
    <label class="gx-by"><span>Photographer</span>
      <select class="gx-select"><option value="">Everyone</option>%(options)s</select>
    </label>
  </div>
  <p class="gx-count" aria-live="polite"><span>%(n)d</span> photographs</p>
  <div class="gx">
%(tiles)s
  </div>
</section>

<section class="gx-credits">
  <div class="lede">
    <div class="eyebrow">Photographed by</div>
    <ul class="gx-names">%(names)s</ul>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The conservatory at Magnolia House from the lawn, glass on three sides"
       style="background-image:url('/assets/img/inc-rain.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">The pamphlet</div>
    <h2>Every place in these photographs, and what it holds.</h2>
    <p>The Wedding Pamphlet has the spaces, the lodging, what is included and the figures.
       It comes to your email and your phone.</p>
    <a class="btn" href="/pricing/">Download the Wedding Pamphlet</a>
  </div>
</section>
""" % dict(n=len(photos), pn=len(credits), chips="".join(chips), options=options,
           tiles="\n".join(tiles),
           names="".join('<li><button type="button" data-credit="%s">%s</button></li>' % (html_attr(c), c)
                         for c in credits))


def html_attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


PAGES["gallery/index.html"] = dict(
    nav="Gallery", title="Gallery | %s" % SITE,
    desc="Weddings at The Valley Venues, photographed by thirteen wedding photographers.",
    hero_img="included.webp",
    hero_alt="The conservatory at Magnolia House lit for a reception, a couple dancing under the chandeliers",
    hero_text=False,
    eyebrow="The Gallery",
    h1="Photographs sell this place better than we can.",
    standfirst="Magnolia House, the meadow, the deck and the grounds, at real weddings, "
               "each photograph credited to the person who took it.",
    head='<link rel="stylesheet" href="/assets/gallery.css">\n',
    foot_js='<script src="/assets/gallery.js" defer></script>',
    body=gallery_body(),
)


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
