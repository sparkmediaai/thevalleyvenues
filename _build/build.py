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
    ("Weddings", "/weddings/"),
    ("Stay", "/stay/"),
    ("The Estate", "/the-estate/"),
    ("Planners", "/planners/"),
    ("About", "/about/"),
]
CTA = ("Book a Tour", "/book-a-tour/")

FOOTER = [
    ("Celebrate", [
        ("The Estate Weekend", "/weddings/"),
        ("What's Included", "/weddings/whats-included/"),
        ("Real Weddings", "/weddings/real-weddings/"),
        ("Single-Day Celebrations", "/weddings/single-day/"),
    ]),
    ("Stay", [
        ("Lodging on the Estate", "/stay/"),
        ("The Estate", "/the-estate/"),
    ]),
    ("Trade", [
        ("For Planners", "/planners/"),
        ("Preferred Vendors", "/planners/vendors/"),
        ("Register as a Planner", "/planners/register/"),
    ]),
    ("The Valley Venues", [
        ("About &amp; Kobi", "/about/"),
        ("Book a Tour", "/book-a-tour/"),
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
        '        <div>\n          <h4>%s</h4>\n          <ul>%s</ul>\n        </div>'
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
<meta name="theme-color" content="#23291F">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%(site)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
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
<link rel="stylesheet" href="%(root)sassets/forms.css">
%(head)s<script>window.FORM_ENDPOINT=%(endpoint)s;if(/[?&]notes\b/.test(location.search))document.documentElement.classList.add("notes")</script>
</head>
<body>

<a class="skip" href="#main">Skip to content</a>

<header class="site-head">
  <div class="inner">
    <a class="wordmark" href="%(root)s">%(site)s</a>
    <nav class="site-nav" aria-label="Primary">
      <ul>
%(nav)s
      </ul>
    </nav>
    <a class="btn btn-solid" href="%(cta_href)s">%(cta_text)s</a>
  </div>
</header>

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
  <div class="inner">
%(foot)s
    <div>
      <h4>Visit</h4>
      <address class="addr">
        1860 Pope Creek Rd<br>Wildwood, Georgia<br>
        Fifteen minutes from Chattanooga
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
        "head": page.get("head", ""), "foot_js": page.get("foot_js", ""),
    }


# ---------------------------------------------------------------- the pages
PAGES = {}

PAGES["index.html"] = dict(
    nav=None, title="%s | %s" % (SITE, TAGLINE), desc=TAGLINE,
    head='<link rel="stylesheet" href="/assets/home.css">\n'
         '<link rel="preload" as="image" href="/assets/img/hero-1.webp"\n'
         '      imagesrcset="/assets/img/hero-1-sm.webp 1100w, /assets/img/hero-1.webp 2200w"\n'
         '      imagesizes="100vw">\n',
    foot_js='<script src="/assets/home.js" defer></script>',
    hero_html='  <div class="hero-stage">\n    <figure class="slide is-on" data-moment="The arrival"><img src="/assets/img/hero-1.webp" srcset="/assets/img/hero-1-sm.webp 1100w, /assets/img/hero-1.webp 2200w" sizes="100vw" alt="Magnolia House, white columns above the lawn" width="2200" height="1100" fetchpriority="high" decoding="async"></figure>\n    <figure class="slide" data-moment="The morning"><img data-src="/assets/img/hero-2.webp" data-srcset="/assets/img/hero-2-sm.webp 1100w, /assets/img/hero-2.webp 2200w" sizes="100vw" alt="A groom having his bow tie straightened, both of them laughing" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="The meadow, set"><img data-src="/assets/img/hero-3.webp" data-srcset="/assets/img/hero-3-sm.webp 1100w, /assets/img/hero-3.webp 2200w" sizes="100vw" alt="The ceremony aisle set out, the ridge behind it" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="Golden hour"><img data-src="/assets/img/hero-4.webp" data-srcset="/assets/img/hero-4-sm.webp 1100w, /assets/img/hero-4.webp 2200w" sizes="100vw" alt="A couple in the meadow as the light goes" width="2200" height="1100" decoding="async"></figure>\n    <figure class="slide" data-moment="After dark"><img data-src="/assets/img/hero-5.webp" data-srcset="/assets/img/hero-5-sm.webp 1100w, /assets/img/hero-5.webp 2200w" sizes="100vw" alt="The conservatory at Magnolia House, lit for dinner" width="2200" height="1100" decoding="async"></figure>\n    <div class="hero-marks">\n      <button type="button" class="hero-step" data-step="-1" aria-label="Previous moment"><svg viewBox="0 0 12 20" aria-hidden="true" focusable="false"><path d="M9 1 2 10 9 19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>\n      <p class="hero-hour"><span>The arrival</span></p>\n      <div class="hero-dots" role="group" aria-label="Choose a moment">\n        <button type="button" aria-current="true"><span class="skip">The arrival</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">The morning</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">The meadow, set</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">Golden hour</span><i></i></button>\n        <button type="button" aria-current="false"><span class="skip">After dark</span><i></i></button>\n      </div>\n      <button type="button" class="hero-step" data-step="1" aria-label="Next moment"><svg viewBox="0 0 12 20" aria-hidden="true" focusable="false"><path d="M3 1 10 10 3 19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>\n    </div>\n  </div>\n',
    eyebrow="Wildwood, Georgia &middot; Fifteen minutes from Chattanooga",
    h1="One Private Mountain Estate. All for You.",
    standfirst="Seventy-four private acres beneath Lookout Mountain, fifteen minutes from "
               "Chattanooga. One wedding at a time, ever. For your two days the gate closes "
               "behind one family, and every field, every porch and every bed is yours.",
    actions=[("Book a Tour", "/book-a-tour/"),
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
    <a class="btn" href="/the-estate/">See the whole property</a>
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
      <span class="wk-when">Friday</span>
      <b>You arrive once</b>
      <p>Through the gate, and for the next two days this is simply where you are. The
         rehearsal happens where the vows will, and nobody goes back to a hotel.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-dawn.webp" alt="A suite on the estate in the morning" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Saturday, early</span>
      <b>Sunrise comes with the room</b>
      <p>Light comes up over Lookout Mountain and fills the room you are already standing
         in. Hair can start at five. There is no commute in a wedding dress.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-gold.webp" alt="A couple dancing on the deck as the light goes" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Saturday, six</span>
      <b>The mountain turns gold</b>
      <p>Guests walk from the ceremony to the overlook. Nobody drives, nobody follows
         directions, and nobody starts looking for their keys at eleven.</p>
    </li>
    <li class="wk reveal">
      <figure><img src="/assets/img/wk-sun.webp" alt="The cottages on the hill at dusk" width="1200" height="900" loading="lazy" decoding="async"></figure>
      <span class="wk-when">Sunday</span>
      <b>Goodnight instead of goodbye</b>
      <p>Two nights means three mornings, and the last thing you do together is breakfast
         rather than a car park.</p>
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
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
    actions=[("Book a Tour", "/book-a-tour/"),
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

<section id="investment">
  <div class="lede">
    <div class="eyebrow">Investment</div>
    <h2>One figure, and a conversation.</h2>
    <p>Estate Weekends begin at <b>[starting figure &mdash; to be confirmed]</b>. There is no
       package grid and no price list to download, because what actually fits depends on your
       date, your count and how you want the weekend to feel.</p>
    <p>Tell us those three things and what comes back is a recommendation, not a brochure.</p>
    <a class="btn btn-solid" href="/book-a-tour/">Start there</a>
  </div>
  <div class="note">
    <p><b>Prototype note.</b> The published starting figure is one of the decisions still
       open. The framework recommends a single number with nothing beside it &mdash; the
       absence of everything else is what produces the enquiry.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="The conservatory lit from within after dark"
       style="background-image:url('/assets/img/close-weddings.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">One weekend at a time</div>
    <h2>Most Saturdays are already spoken for.</h2>
    <p>The estate holds one wedding at a time, which means the calendar is shorter than it looks. Walking the property is how most couples decide, and it costs nothing but an afternoon.</p>
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
               "vendors who made it &mdash; which is also how a vendor list earns its referrals.",
    body="""
<section>
  <div class="lede">
    <h2>Gallery</h2>
    <p>Eight frames from the estate&rsquo;s existing photography, standing in for the
       structure of the real thing: a wall you scroll rather than a lightbox you open,
       and every wedding credited underneath it.</p>
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
    <p>The credits are not a courtesy. A vendor who is named here has a reason to name the
       estate on her own site, which is the whole mechanism of the
       <a href="/planners/vendors/">preferred vendor list</a>.</p>
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
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
       not a cheaper version of somebody else&rsquo;s. There is still one
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
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
    actions=[("Enquire about a stay", "/book-a-tour/")],
    body="""
<section>
  <div class="lede">
    <h2>Come for a weekend. Come back for an anniversary.</h2>
    <p>Or come once, look around, and start imagining something larger. A guest who stays
       two nights has seen the whole estate &mdash; which is how a good many weddings here
       begin.</p>
  </div>
  <div class="names" aria-hidden="true">
    <div class="names-track"><span>Phoenix</span><span>Bluebird</span><span>Goldfinch</span><span>Hummingbird</span><span>Willow</span><span>Mahogany</span><span>Overlook Village</span><span>The Lodge</span><span>Phoenix</span><span>Bluebird</span><span>Goldfinch</span><span>Hummingbird</span><span>Willow</span><span>Mahogany</span><span>Overlook Village</span><span>The Lodge</span></div>
  </div>
  <ul class="named">
    <li>Phoenix <span>Cottage</span></li>
    <li>Bluebird <span>Cottage</span></li>
    <li>Goldfinch <span>Cottage</span></li>
    <li>Hummingbird <span>Cottage</span></li>
    <li>Willow <span>Cottage</span></li>
    <li>Mahogany <span>Cottage</span></li>
    <li>Overlook Village <span>Cottages on the hill</span></li>
    <li>The Lodge <span>The larger house</span></li>
  </ul>
  <div class="grid">
    <article class="card">
      {{img:stay-village.webp|The cottages of Overlook Village along the hillside|class="wipe"}}
      <div class="eyebrow">Overlook Village</div>
      <p>A row of cottages along the hill, each one facing out rather than at the next.</p>
    </article>
    <article class="card">
      {{img:stay-inside.webp|A cottage bathroom in timber, twin basins under twin mirrors|class="wipe"}}
      <div class="eyebrow">Inside</div>
      <p>Timber, glass and quiet. Built to be lived in for two nights, not checked into.</p>
    </article>
  </div>
  <div class="note">
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
    <div class="eyebrow">Why an events estate has beds in it</div>
    <h2 class="rise-words"><span>Nobody</span> <span>drives</span> <span>home.</span> <span>That</span> <span>is</span> <span>the</span> <span>whole</span> <span>idea.</span></h2>
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
    <a class="btn" href="/book-a-tour/">Enquire about a stay</a>
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
    standfirst="This page replaces a dropdown that listed four venues. There are not four "
               "venues. There is one estate, and every celebration includes all of it.",
    body="""
<section>
  <div class="statement">
    <div class="eyebrow">Read this first</div>
    <h2 class="rise-words"><span>There</span> <span>are</span> <span>not</span> <span>four</span> <span>venues.</span> <span>There</span> <span>is</span> <span>one</span> <span>estate.</span></h2>
    <p>The old site listed four venues in a dropdown, which is how a guest
       learns to ask which one they are getting. It is the wrong question. The
       four places below are not alternatives to choose between; they are four
       points on one walk, and every celebration here includes all of them.</p>
    <p class="close">You arrive at the house, you marry in the meadow, you
       drink on the deck and you dance in the hall. Nobody drives between them.</p>
  </div>
</section>

<section class="walk">
  <div class="lede">
    <div class="eyebrow">The walk</div>
    <h2>Six places, and the ground between them.</h2>
    <p>The drawing is the estate&rsquo;s own survey &mdash; contours every five
       metres, off the same LiDAR the county holds. Six places, and the walk
       between them, at the size it actually is.</p>
  </div>
  <div class="walk-grid">
    <figure class="walk-map">
      {{inline:plan.svg}}
      <figcaption>Contours at 5&thinsp;m. The whole weekend is
        <b>928&thinsp;m</b> of walking &mdash; 0.58 miles, spread over two days.
        Elevation is USGS 3DEP one-metre LiDAR; place positions are read from
        aerial imagery and want confirming against a site plan.</figcaption>
    </figure>
    <div class="walk-steps">
    <div class="wstep ws-1">
      <div class="eyebrow"><span>Friday</span></div>
      <h3>Arrival</h3>
      <p>You turn off Pope Creek Road and the gate closes behind you. For the next two days nothing arrives that you did not invite, and nothing leaves until you do. This is the only drive anybody makes all weekend.</p>
    </div>
    <div class="wstep ws-2">
      <div class="eyebrow"><span>Friday</span><span class="dist">53 m from the gate</span></div>
      <h3>Magnolia House</h3>
      <p>White columns and glass against the ridge, at the top of the drive. It is the first photograph almost every guest takes, through the windshield on the way up. The conservatory behind it is also the weather plan that costs nothing.</p>
      <figure class="frame">
        {{img:magnolia-house.webp|Magnolia House, white columns above the lawn|class="par"}}
      </figure>
    </div>
    <div class="wstep ws-3">
      <div class="eyebrow"><span>Saturday, four</span><span class="dist">263 m from the front door</span></div>
      <h3>The Valley</h3>
      <p>An open meadow held on three sides by ridgeline, with Lookout Mountain beyond. Sound stays in it and the wind drops in it. Nothing is visible from it that the estate does not own.</p>
      <figure class="frame">
        {{img:the-valley.webp|The processional crossing the meadow|class="par"}}
      </figure>
    </div>
    <div class="wstep ws-4">
      <div class="eyebrow"><span>Saturday, six</span><span class="dist">313 m &mdash; the longest walk of the weekend</span></div>
      <h3>The Lookout Deck</h3>
      <p>A railed deck out over the valley, facing the mountain. It turns gold at six, tip to tip, and everyone stops talking. Guests walk here from the ceremony; there is no shuttle because there is nothing to shuttle across.</p>
      <figure class="frame">
        {{img:lookout-deck.webp|A couple dancing on the Lookout Deck, the ridge behind|class="par"}}
      </figure>
    </div>
    <div class="wstep ws-5">
      <div class="eyebrow"><span>Saturday, eight</span><span class="dist">200 m from the deck</span></div>
      <h3>Davis Hall</h3>
      <p>Drapery, chandeliers, and the room where the dancing happens. It carries the largest receptions on the property, and nobody has to find their car to get to it.</p>
      <figure class="frame">
        {{img:davis-hall.webp|Davis Hall under its drapery, lit for the first dance|class="par"}}
      </figure>
    </div>
    <div class="wstep ws-6">
      <div class="eyebrow"><span>Saturday, late</span><span class="dist">99 m, and then bed</span></div>
      <h3>Overlook Village</h3>
      <p>Cottages along the hill, thirty-four beds, and the end of the evening about a minute from the end of the party. This is the leg that every other venue replaces with a taxi rank.</p>
      <figure class="frame">
        {{img:stay-village.webp|The cottages of Overlook Village along the hillside|class="par"}}
      </figure>
    </div>
    </div>
  </div>
</section>

<section class="band">
  {{img:band-ground.webp|The couple standing at the arch in the open meadow|class="band-img"}}
  <p>Four places on one map, and you never leave the property to reach any of them.</p>
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
    <p>You can see the four places on this page. What you cannot see from a screen is how far apart they are, how quiet the meadow is, or how the deck turns at six.</p>
    <a class="btn" href="/book-a-tour/">Book a tour</a>
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
    actions=[("Register as a planner", "/planners/register/"),
             ("Preferred vendors", "/planners/vendors/")],
    body="""
<section>
  <div class="grid">
    <article class="card">
      <h3>Site logistics</h3>
      <p>Load-in access, vehicle routes on the property, power, kitchen access, and where
         the golf carts live. <em>Detail to be confirmed with the operations team.</em></p>
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
    <article class="card">
      <h3>We would rather support your plan</h3>
      <p>Than replace it. The estate has an in-house team, and it is used to working
         alongside a planner rather than instead of one.</p>
    </article>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The shape of it</div>
    <h2>How a weekend actually runs.</h2>
    <p>Times are indicative and get confirmed with the operations team, but the
       sequence is the same every weekend and it is the sequence that matters
       when you are building a timeline.</p>
  </div>
  <div class="steps">
    <div class="step"><span class="when">Fri</span>
      <div><b>Load-in from midday</b><p>Vehicle access to all four spaces. Nothing
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
       worked separately from bridal enquiries.</p>
  </div>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">The part that matters to you</div>
    <h2 class="rise-words"><span>A</span> <span>weekend</span> <span>here</span> <span>has</span> <span>one</span> <span>moving</span> <span>part,</span> <span>and</span> <span>it</span> <span>is</span> <span>yours.</span></h2>
    <p>One load-in. One site. One team, on the property overnight, who have run
       this weekend before and know which door the kitchen is behind. No shared
       loading bay, no other planner&rsquo;s truck in the way, no negotiation
       over who gets the ceremony lawn at four.</p>
    <p class="close">You are not competing for the venue&rsquo;s attention,
       because there is nobody else to give it to.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A couple at the rail of the Lookout Deck, the ridge behind"
       style="background-image:url('/assets/img/close-planners.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Trade enquiries</div>
    <h2>Come and walk it without a couple.</h2>
    <p>Planner site visits are welcome on their own, and are a good deal more useful than a floor plan. Bring a timeline and we will tell you what it actually takes here.</p>
    <a class="btn" href="/planners/register/">Register as a planner</a>
  </div>
</section>
""")

PAGES["planners/vendors/index.html"] = dict(
    nav="Planners", title="Preferred Vendors | %s" % SITE,
    desc="Planners and vendors who know the estate.",
    hero_img="vendors.webp", hero_alt="An invitation suite and two rings",
    eyebrow="For planners &middot; Preferred vendors",
    h1="The people who know this property.",
    standfirst="Most couples reach this site before they have hired a planner. This list "
               "puts one in front of a couple who has already chosen the estate.",
    body="""
<section>
  <div class="lede">
    <h2>Planners</h2>
    <p>Each entry carries a name, a studio, a website and a social handle.</p>
  </div>
  <ul class="named">
    <li>Planner name <span>Studio &middot; website &middot; social</span></li>
    <li>Planner name <span>Studio &middot; website &middot; social</span></li>
    <li>Planner name <span>Studio &middot; website &middot; social</span></li>
  </ul>
  <div class="split flip" style="margin-top:3rem">
    <div class="split-text">
      <h2>Vendors</h2>
      <p>Photography, florals, music, hair and makeup, rentals, officiants.</p>
      <p>Rentals is the shortest list, because the tables, the chairs, the linens and a
         good deal of the decor are already on the property.</p>
    </div>
    <figure class="frame">
      {{img:vend-table.webp|Glassware and candles down the length of a laid table|class="par par-mid"}}
    </figure>
  </div>
  <ul class="named">
    <li>Vendor name <span>Category &middot; website &middot; social</span></li>
    <li>Vendor name <span>Category &middot; website &middot; social</span></li>
    <li>Vendor name <span>Category &middot; website &middot; social</span></li>
  </ul>
  <div class="note">
    <p><b>Why this page exists.</b> Being listed here gives a planner cause to name the estate
       on her own site and in her guides. The referral runs both directions, and the estate
       holds the list.</p>
  </div>
</section>

<section>
  <div class="statement">
    <div class="eyebrow">How this list is meant to work</div>
    <h2 class="rise-words"><span>A</span> <span>referral</span> <span>is</span> <span>worth</span> <span>more</span> <span>than</span> <span>an</span> <span>advertisement.</span></h2>
    <p>Most couples find a venue before they find a planner. By the time
       somebody is reading this page they have already decided where the wedding
       is, which makes it the least competitive introduction a planner will get
       all year.</p>
    <p class="close">In return, the estate gets named on a dozen other sites by
       people with no reason to flatter it. That is the entire mechanism, and it
       only works if the list stays short and honest.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="Candles and low light on a dressed table"
       style="background-image:url('/assets/img/close-vendors.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">For vendors</div>
    <h2>Worked here before?</h2>
    <p>If you have run a wedding on this property and it went well, tell us. The list is built from people the team has actually stood beside at one in the morning.</p>
    <a class="btn" href="/book-a-tour/">Get in touch</a>
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
               placeholder="(423) 555&#8209;0147">
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
               placeholder="okaforevents.com">
      </div>
      <div class="field">
        <label for="p_planner_social">Instagram</label>
        <input id="p_planner_social" name="planner_social" type="text"
               placeholder="@okaforevents">
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
       centrepieces, why the walk from the ceremony to the deck is a walk and
       not a shuttle, and why the last thing on the property is a cottage in the
       woods rather than a car park.</p>
  </div>
</section>

<section>
  <div class="lede">
    <div class="eyebrow">The family</div>
    <h2>A family story, still.</h2>
    <p>Paul Cummings bought the property for another purpose entirely. Over time he and his
       daughter Kobi began restoring and reimagining it, and what emerged was not a
       collection of event spaces but a hospitality estate.</p>
    <p>The estate should grow without anyone becoming a room number. Clients are known here.</p>
  </div>
</section>

<section class="closing">
  <div class="closing-img" role="img" aria-label="A mother settling her daughter's veil before the ceremony"
       style="background-image:url('/assets/img/close-about.webp')"></div>
  <div class="closing-body">
    <div class="eyebrow">Come and meet them</div>
    <h2>You will be dealing with the family.</h2>
    <p>Not a sales office. The people who answer the enquiry are the people who will be on the property at eleven at night on your Saturday.</p>
    <a class="btn" href="/book-a-tour/">Book a tour</a>
  </div>
</section>
""")

PAGES["book-a-tour/index.html"] = dict(
    nav=None, title="Book a Tour | %s" % SITE,
    desc="Reserve a tour of the estate.",
    hero_img="tour.webp",
    hero_alt="A couple turning together in the open meadow, the ridge beyond",
    eyebrow="Book a tour",
    h1="Come and stand in it.",
    standfirst="More than half of the couples who walk this property book it. Tell us a "
               "little about the weekend you are imagining and we will tell you what "
               "actually fits.",
    body="""

<section>
  <form class="form inquiry" id="inquiry-couple" novalidate
        data-inquiry-type="Couple" data-kind="couple">
    <p class="form-intro">Everything except your name and email is optional,
       but the more you tell us the more useful the reply is.</p>

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
               placeholder="(423) 555&#8209;0147">
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
    <button class="btn btn-solid" type="submit">Request a tour</button>
    <p class="form-privacy">We will only use this to answer you. No list, no
       drip, nothing sold.</p>
  </form>

  <div class="form-done" id="inquiry-couple-done" role="status" hidden>
    <div class="eyebrow">Thank you</div>
    <h2>That is with Kobi.</h2>
    <p>You will get a reply from a person, naming the two or three
       configurations that actually fit what you described. If it has not
       arrived within a day or so, email
       <a href="mailto:Info@thevalleyvenues.com">Info@thevalleyvenues.com</a>
       and we will find out why.</p>
  </div>

  <div class="lede" style="margin-top:3rem">
    <div class="eyebrow">What happens next</div>
    <h2>Three things, in this order.</h2>
  </div>
  <div class="steps">
    <div class="step"><span class="when">One</span>
      <div><b>A reply from a person</b><p>Naming the two or three configurations
      that actually fit what you described, with figures. Not a brochure and not
      a price list.</p></div></div>
    <div class="step"><span class="when">Two</span>
      <div><b>An afternoon on the property</b><p>An hour and a half, on foot,
      including the parts most tours skip. Bring whoever is going to ask the
      hard questions.</p></div></div>
    <div class="step"><span class="when">Three</span>
      <div><b>A date held while you think</b><p>Nothing on this property is
      shared, which means a date either is yours or it is not. We will tell you
      plainly which ones are still open.</p></div></div>
  </div>

  <div class="note">
    <p><b>Prototype note.</b> The form posts to a Cloudflare worker, which holds the
       GoHighLevel webhook URL as a secret and forwards the inquiry. Until that worker is
       deployed the form validates and then tells the visitor to email instead. Note what it
       does not ask: your total
       budget. That question closes more doors than it filters, and guest count arrives
       naturally here anyway &mdash; after you have described what you want, rather than as
       the price of entry.</p>
    <p>What should come back is a recommendation naming the two or three configurations that
       fit, priced, in the brand voice, and signed by Kobi &mdash; within minutes rather than
       a pamphlet within seconds.</p>
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
    <div class="eyebrow">The drive up</div>
    <h2>More than half of the couples who walk it book it.</h2>
    <p>That is not a sales line, it is a description of what the property does to people. It is fifteen minutes from Chattanooga and the tour is free.</p>
    <a class="btn" href="#main">Request a tour</a>
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
             ("Book a Tour", "/book-a-tour/")],
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
    <li><a href="/book-a-tour/">Book a tour</a> <span>Come and stand in it</span></li>
  </ul>
</section>
""")


# --------------------------------------------------------------------- write
for path, page in PAGES.items():
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    html = shell(page, path)
    open(dest, "w", encoding="utf-8").write(html)
    print("%-44s %5d bytes" % (path, len(html)))

print("\n%d pages" % len(PAGES))
