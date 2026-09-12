"""
The map lab: ten treatments of the estate map, side by side.

    python _tools/map_lab.py

These are for looking at and choosing between, not for shipping. They live at
/map-lab/, nothing links to them, and every one of them carries noindex.

The brief was Disney, which needs reading carefully, because the brand document
rules out the obvious version of it: no princess graphics, no fantasy fonts, no
overly literal fairy tale. What it does not rule out -- what it asks for -- is
the craft underneath a Disney park map. Those maps are hand-drawn, warm, lit
like a stage, and they make you want to walk into them. That is the target:
atmosphere rather than costume, which is the brand document's own phrase.

Every variation hovers to a real photograph of the real place. That was the
part of the brief with the least room for interpretation and it is the part
that does the selling.

Each entry below is name, blurb, optional svg options, css and js. Adding an
eleventh is a dict, not a file.
"""
import os
import shutil

from estate_map import build, PLACES
from map_lab_variations import VARIATIONS

INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Map Lab &mdash; The Valley Venues</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Libre+Franklin:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/map-lab/lab.css">
<style>
.wrap{max-width:74rem;margin:0 auto;padding:clamp(2rem,6vw,4rem) clamp(1.1rem,4vw,3rem) 5rem}
.lead{max-width:46rem;margin-bottom:clamp(2rem,5vw,3rem)}
.lead h1{font-family:var(--display);font-weight:400;font-size:clamp(2.1rem,5vw,3.4rem);
  margin:0 0 .7rem;line-height:1.04}
.lead p{margin:0 0 .8rem;opacity:.82}
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr))}
.lab-card{display:block;text-decoration:none;color:var(--deep);background:var(--cream);
  border:1px solid var(--olive);padding:1.2rem 1.3rem 1.4rem;
  transition:transform .3s cubic-bezier(.16,.8,.24,1),box-shadow .3s}
.lab-card:hover{transform:translateY(-3px);box-shadow:0 14px 32px rgba(52,55,47,.17)}
.lab-card h2{font-family:var(--display);font-weight:400;font-size:1.55rem;
  margin:.1rem 0 .45rem;line-height:1.1}
.lab-card p{margin:0;font-size:.88rem;opacity:.78;line-height:1.5}
</style></head>
<body class="lab"><div class="wrap">
<div class="lead">
<h1>Ten maps</h1>
<p>Ten treatments of the same estate, for choosing between rather than for
shipping. Every one of them hovers to a real photograph of the real place.</p>
<p>Nothing on the site links here and every page carries noindex. The map
currently live on <b>/the-estate/</b> is closest to&nbsp;01.</p>
</div>
<div class="grid">%s</div>
</div></body></html>"""

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "map-lab")

# Three real frames per place, so a hover can show the property rather than a
# diagram of it.
PHOTOS = {
    "magnolia": ["mh-2", "mh-3", "mh-6"],
    "valley":   ["tv-2", "tv-3", "tv-7"],
    "hall":     ["dh-2", "dh-3", "dh-5"],
    "deck":     ["ld-2", "ld-4", "ld-7"],
    "village":  ["ov-2", "ov-4", "ov-8"],
    "woods":    ["close-woods", "sd-fire", "stay-inside"],
}
BLURB = {
    "magnolia": "Columns, glass, and the first photograph every guest takes.",
    "valley":   "The meadow, held on three sides, open to the mountain.",
    "hall":     "Dinner, the first dance, and the largest floor on the estate.",
    "deck":     "Fifteen thousand square feet out over the valley.",
    "village":  "Four cottages along the hill, each turned to face out.",
    "woods":    "One cabin at the far edge, for the two of you.",
}

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>%(n)s &middot; %(name)s &mdash; Map Lab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=Libre+Franklin:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/map-lab/lab.css">
<style>%(css)s</style>
</head>
<body class="lab">
<header class="lab-head">
  <a class="lab-back" href="/map-lab/">&larr; All ten</a>
  <div>
    <span class="lab-n">%(n)s</span>
    <h1>%(name)s</h1>
    <p>%(blurb)s</p>
  </div>
  <nav class="lab-jump">%(jump)s</nav>
</header>
<main class="lab-stage %(stage)s">
%(body)s
</main>
<script>%(js)s</script>
</body>
</html>
"""

LAB_CSS = """
/* Shared chrome for every variation. The map itself is styled per page. */
:root{
  --ivory:#F5F1EA; --cream:#FFF0DA; --olive:#9A9F83; --clay:#B38A64;
  --blue:#679AA7; --sage:#AABEB3; --deep:#34372F;
  --sans:"Libre Franklin",system-ui,-apple-system,"Segoe UI",sans-serif;
  --display:"Cormorant Garamond",Georgia,serif;
}
*{box-sizing:border-box}
html,body{margin:0}
body.lab{background:var(--ivory);color:var(--deep);font:400 16px/1.6 var(--sans)}

.lab-head{
  display:flex;align-items:flex-start;gap:clamp(1rem,3vw,2.5rem);flex-wrap:wrap;
  padding:clamp(1.1rem,3vw,2rem) clamp(1.1rem,4vw,3rem);
  border-bottom:1px solid var(--olive);
}
.lab-back{
  font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600;
  color:var(--deep);text-decoration:none;padding-top:.55rem;white-space:nowrap;
}
.lab-back:hover{text-decoration:underline}
.lab-n{
  font-size:.7rem;letter-spacing:.2em;font-weight:600;color:var(--clay);
  display:block;margin-bottom:.15rem;
}
.lab-head h1{font-family:var(--display);font-weight:400;font-size:clamp(1.5rem,3.4vw,2.2rem);margin:0;line-height:1.1}
.lab-head p{margin:.3rem 0 0;color:var(--deep);opacity:.72;max-width:46rem;font-size:.94rem}
.lab-jump{margin-left:auto;display:flex;gap:.3rem;flex-wrap:wrap;padding-top:.4rem}
.lab-jump a{
  font:600 .7rem/1 var(--sans);letter-spacing:.06em;color:var(--deep);
  text-decoration:none;border:1px solid var(--olive);padding:.38rem .5rem;border-radius:2px;
}
.lab-jump a:hover{background:var(--cream)}
.lab-jump a[aria-current]{background:var(--deep);color:var(--cream);border-color:var(--deep)}

.lab-stage{position:relative;overflow:hidden}
.estate-map{display:block;width:100%;height:auto}

/* The map's own type, shared. */
.map-label{
  font-family:var(--sans);font-size:19px;font-weight:600;letter-spacing:.09em;
  text-transform:uppercase;fill:var(--deep);
  paint-order:stroke fill;stroke:var(--cream);stroke-width:5px;stroke-linejoin:round;
}
.map-sign{
  font-family:var(--sans);font-size:13px;font-weight:500;letter-spacing:.05em;
  fill:var(--deep);opacity:.7;
  paint-order:stroke fill;stroke:var(--cream);stroke-width:4px;stroke-linejoin:round;
}
.map-halo{fill:var(--olive);opacity:0;transition:opacity .3s ease}
.map-place{cursor:pointer}

/* The photograph that a hover reveals. Shared by most of the ten. */
.peek{
  position:absolute;z-index:40;pointer-events:none;width:clamp(200px,22vw,320px);
  opacity:0;transform:translate(-50%,-108%) scale(.96);
  transition:opacity .32s ease,transform .32s cubic-bezier(.16,.8,.24,1);
}
.peek.on{opacity:1;transform:translate(-50%,-104%) scale(1)}
.peek figure{margin:0;background:var(--cream);padding:.5rem .5rem .1rem;
  box-shadow:0 18px 40px rgba(52,55,47,.28);border-radius:2px}
.peek img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}
.peek figcaption{padding:.5rem .15rem .55rem}
.peek b{display:block;font-family:var(--display);font-weight:400;font-size:1.15rem;line-height:1.15}
.peek span{display:block;font-size:.78rem;opacity:.75;margin-top:.15rem}

@media (prefers-reduced-motion:reduce){
  *{animation-duration:.001ms !important;transition-duration:.001ms !important}
}
"""

# The hover-to-photograph behaviour, shared by the variations that use it.
PEEK_JS = """
function peekInit(opts){
  opts = opts || {};
  var stage = document.querySelector('.lab-stage');
  var svg = stage.querySelector('svg');
  var peek = document.createElement('div');
  peek.className = 'peek';
  peek.innerHTML = '<figure><img alt=""><figcaption><b></b><span></span></figcaption></figure>';
  stage.appendChild(peek);
  var img = peek.querySelector('img'), ttl = peek.querySelector('b'), sub = peek.querySelector('span');
  var shots = window.LAB_PHOTOS, timer = null, at = 0, cur = null;

  function place(el){
    // Anchor to the building, not the pointer, so it never jitters.
    var b = el.getBBox ? el.getBBox() : null;
    var r = el.getBoundingClientRect(), s = stage.getBoundingClientRect();
    peek.style.left = (r.left - s.left + r.width / 2) + 'px';
    peek.style.top  = (r.top  - s.top) + 'px';
  }
  function show(el){
    var key = el.getAttribute('data-place');
    if (!shots[key]) return;
    cur = key; at = 0;
    img.src = '/assets/img/' + shots[key].photos[0] + '.webp';
    img.alt = shots[key].title;
    ttl.textContent = shots[key].title;
    sub.textContent = shots[key].blurb;
    place(el); peek.classList.add('on');
    clearInterval(timer);
    // The place has eight frames; three of them is enough to say "there is
    // more of this" without turning the map into a slideshow.
    timer = setInterval(function(){
      at = (at + 1) % shots[cur].photos.length;
      img.src = '/assets/img/' + shots[cur].photos[at] + '.webp';
    }, 1500);
  }
  function hide(){ peek.classList.remove('on'); clearInterval(timer); cur = null; }

  svg.querySelectorAll('.map-place').forEach(function(el){
    el.addEventListener('mouseenter', function(){ show(el); });
    el.addEventListener('focus', function(){ show(el); });
    el.addEventListener('mouseleave', hide);
    el.addEventListener('blur', hide);
  });
  stage.addEventListener('mouseleave', hide);
  if (opts.after) opts.after(svg, stage);
}
"""


def photos_json():
    rows = []
    for key in PLACES:
        rows.append('"%s":{"title":%s,"blurb":%s,"photos":[%s]}' % (
            key, '"%s"' % PLACES[key]["label"], '"%s"' % BLURB[key],
            ",".join('"%s"' % n for n in PHOTOS[key])))
    return "window.LAB_PHOTOS={%s};" % ",".join(rows)


def extras(v, svg):
    """The couple of variations that need controls under the drawing."""
    if v.get("dusk"):
        night, _ = build(**dict(v.get("opts", {}), **v["dusk"]))
        return ('<div class="hours"><div class="layer day">%s</div>'
                '<div class="layer dusk">%s</div></div>'
                '<div class="dial"><label for="t">Hour</label>'
                '<input id="t" type="range" min="0" max="100" step="0.5" value="38">'
                '<output id="tv">1:56 pm</output></div>' % (svg, night))
    if v["slug"] == "03":
        return (svg + '<div class="rail"><button id="play">Pause</button>'
                '<span class="now" id="now">&mdash;</span>'
                '<input id="bar" type="range" min="0" max="100" step="0.1" value="0"></div>')
    if v["slug"] == "07":
        keys = [("spring", "Spring"), ("summer", "Summer"),
                ("autumn", "Autumn"), ("winter", "Winter")]
        return (svg + '<div class="seasons">%s</div>' % "".join(
            '<button data-s="%s" aria-pressed="false">%s</button>' % k for k in keys))
    if v["slug"] == "08":
        # Three panels, each showing a third of the same drawing. It has to be
        # three copies: a panel cannot show a slice of an element it does not
        # contain, and the creases have to fall between real edges.
        # The fir symbol's id has to differ per copy. Three elements answering
        # to #vv-fir is invalid, and every <use> in panels two and three would
        # quietly resolve against panel one's.
        panels = "".join(
            '<div class="panel">%s</div>' % svg.replace("vv-fir", "vv-fir-%d" % i)
            for i in range(3))
        return ('<button class="again">Fold it again</button>'
                '<div class="fold">%s</div>' % panels)
    if v["slug"] == "09":
        return (svg + '<button class="hold">Stop the tour</button>'
                '<div class="card"><img alt=""><b></b><span></span></div>')
    return svg


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    with open(os.path.join(OUT, "lab.css"), "w", encoding="utf-8") as f:
        f.write(LAB_CSS.strip() + "\n")

    jump = "".join('<a href="/map-lab/%s/">%s</a>' % (v["slug"], v["slug"])
                   for v in VARIATIONS)

    for v in VARIATIONS:
        svg, _ = build(**v.get("opts", {}))
        body = extras(v, svg)
        if v.get("wrap"):
            body = v["wrap"][0] + body + v["wrap"][1]
        mine = jump.replace('<a href="/map-lab/%s/"' % v["slug"],
                            '<a href="/map-lab/%s/" aria-current="page"' % v["slug"])
        html = SHELL % dict(
            n=v["slug"], name=v["name"], blurb=v["blurb"], jump=mine,
            css=v["css"].strip(), body=body, stage="stage-" + v["slug"],
            js=photos_json() + PEEK_JS + v["js"].strip())
        d = os.path.join(OUT, v["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("  /map-lab/%s/  %-18s %5.0f KB" % (v["slug"], v["name"], len(html) / 1024.0))

    cards = "".join(
        '<a class="lab-card" href="/map-lab/%s/"><span class="lab-n">%s</span>'
        '<h2>%s</h2><p>%s</p></a>' % (v["slug"], v["slug"], v["name"], v["blurb"])
        for v in VARIATIONS)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX % cards)
    print("  /map-lab/         index of %d" % len(VARIATIONS))


if __name__ == "__main__":
    main()
