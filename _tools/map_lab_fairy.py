"""Variations 16-25: the park map as a fairy tale.

11 was the pick. The note on it was "the more Disney the better, very similar to
a fairy tale", with 11 kept exactly as it is. So all ten of these start from 11's
drawing with the storybook layer switched on (pennants on every roof, twinkles,
bluebirds, butterflies over the meadow, a sparkle when you reach for a place) and
each one tells the arrival differently.

Nothing leaves the palette. Sparkles, fireworks, clouds and ribbons are all drawn
in the seven colours plus white, with the same soft ink outline as the map.
Every intro runs only when the stage carries .go, so the resting state is the
finished map, and none of them plays for a visitor who has asked for less motion.
"""
import math

from map_lab_park import BASE_CSS, POP_CSS
from park_map import CREAM, OLIVE, CLAY, BLUE, SAGE, DEEP, WHITE, STAR

# ------------------------------------------------------------------ shared art
FAIRY_CSS = BASE_CSS + """
.park-map .pennant{transform-box:fill-box;transform-origin:0 50%;
  animation:wave 3.4s ease-in-out infinite alternate;animation-delay:calc(var(--fd) * -1)}
@keyframes wave{from{transform:skewY(-5deg) scaleX(.92)}to{transform:skewY(4deg) scaleX(1.02)}}
.park-map .tw{transform-box:fill-box;transform-origin:50% 50%;
  animation:twinkle 5.5s ease-in-out infinite;animation-delay:calc(var(--tw) * -1)}
@keyframes twinkle{0%,100%{transform:scale(.2) rotate(0deg);opacity:.15}50%{transform:scale(1) rotate(90deg);opacity:1}}
.park-map .birds{animation:fly 52s linear infinite}
@keyframes fly{0%{transform:translate(-520px,40px)}25%{transform:translate(160px,-10px)}
  50%{transform:translate(860px,30px)}75%{transform:translate(1500px,-20px)}100%{transform:translate(2280px,10px)}}
.park-map .wing{transform-box:fill-box;transform-origin:50% 100%;animation:flap .7s ease-in-out infinite alternate}
.park-map .wf{animation-delay:-.35s}
@keyframes flap{from{transform:scaleY(1)}to{transform:scaleY(.1)}}
.park-map .bf{animation:flutter 24s ease-in-out infinite}
.park-map .bfly:nth-of-type(2n) .bf{animation-duration:30s;animation-direction:reverse}
@keyframes flutter{0%,100%{transform:translate(0,0)}25%{transform:translate(40px,-30px)}
  50%{transform:translate(-10px,-56px)}75%{transform:translate(-44px,-16px)}}
.park-map .bw{transform-box:fill-box;transform-origin:100% 50%;animation:bwing .6s ease-in-out infinite alternate}
.park-map .bw2{transform-origin:0 50%}
@keyframes bwing{to{transform:scaleX(.45)}}

/* sparkles thrown by the page */
.spk{transform-box:fill-box;transform-origin:50% 50%;animation:spk 1s cubic-bezier(.2,.7,.3,1) forwards}
@keyframes spk{0%{transform:translate(0,0) scale(0) rotate(0deg)}
  25%{transform:translate(calc(var(--dx) * .35),calc(var(--dy) * .35)) scale(var(--s)) rotate(40deg)}
  100%{transform:translate(var(--dx),var(--dy)) scale(0) rotate(170deg)}}
.map-place.hit .b{transform-origin:50% 100%;animation:bounce .8s cubic-bezier(.3,1.2,.5,1)}
.map-place.hit .ban{transform-origin:50% 50%;animation:jig .7s cubic-bezier(.3,1.6,.5,1)}
@keyframes bounce{0%{transform:scale(.1,0)}55%{transform:scale(.94,1.12)}78%{transform:scale(1.04,.96)}100%{transform:none}}
@keyframes jig{0%{transform:scale(.4,.4)}100%{transform:none}}
@keyframes unfurl{from{transform:scaleX(0)}}
@keyframes fade{from{opacity:0}}
@keyframes draw{from{stroke-dashoffset:1}}
@keyframes pop{from{transform:scale(0)}}
"""

HELPERS = """
var NS='http://www.w3.org/2000/svg';
var st=document.querySelector('.lab-stage');
var map=st.querySelector('svg.park-map');
var hooks=[],timers=[],cleanups=[];
var STAR='%(star)s';
var INKS=['#FFFFFF','#FFF0DA','#B38A64','#679AA7','#AABEB3'];
var fx=null;
function layer(){if(!fx||!fx.isConnected){fx=document.createElementNS(NS,'g');fx.setAttribute('class','fx');map.appendChild(fx);}return fx;}
function mk(tag,attrs,parent){var e=document.createElementNS(NS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);(parent||layer()).appendChild(e);return e;}
function spark(x,y,o,parent){o=o||{};var s=o.s||(.4+Math.random()*.7),life=o.life||(900+Math.random()*700);
  var g=mk('g',{transform:'translate('+x.toFixed(1)+' '+y.toFixed(1)+')'},parent);
  var p=mk('path',{d:STAR,fill:o.fill||INKS[Math.random()*INKS.length|0],stroke:'#34372F','stroke-width':1.3,'class':'spk'},g);
  var dx=o.dx!=null?o.dx:(Math.random()-.5)*60,dy=o.dy!=null?o.dy:20+Math.random()*50;
  p.style.setProperty('--s',s);p.style.setProperty('--dx',dx+'px');p.style.setProperty('--dy',dy+'px');
  p.style.animationDuration=life+'ms';setTimeout(function(){g.remove();},life+50);return g;}
function burst(x,y,n,r,parent){for(var i=0;i<n;i++){var a=i/n*Math.PI*2+Math.random()*.3,d=(r||70)*(.6+Math.random()*.5);
  spark(x,y,{dx:Math.cos(a)*d,dy:Math.sin(a)*d,s:.5+Math.random()*.6,life:1000},parent);}}
function later(fn,ms){timers.push(setTimeout(fn,ms));}
function clearAll(){timers.forEach(clearTimeout);timers=[];cleanups.forEach(function(f){f();});cleanups=[];
  if(fx){fx.remove();fx=null;}map.querySelectorAll('.map-place.hit').forEach(function(a){a.classList.remove('hit');});}
function where(key){var h=map.querySelector('.map-'+key+' .map-halo');return {x:+h.getAttribute('cx'),y:+h.getAttribute('cy')};}
function hit(key,n){var a=map.querySelector('.map-'+key);if(!a)return;a.classList.remove('hit');void a.getBBox();
  a.classList.add('hit');var p=where(key);burst(p.x,p.y-50,n||14,100);}
var KEYS=['magnolia','valley','hall','deck','village','woods'];
""" % dict(star=STAR)

TAIL = """
peekInit();
// reach for a place and it throws a little sparkle
var lastHover={};
map.querySelectorAll('.map-place').forEach(function(a){
  a.addEventListener('mouseenter',function(){var k=a.getAttribute('data-place'),now=Date.now();
    if(!MOTION_OK||now-(lastHover[k]||0)<700)return;lastHover[k]=now;var p=where(k);burst(p.x,p.y-60,10,80);});
});
function play(){clearAll();st.classList.remove('go');void st.offsetWidth;st.classList.add('go');
  hooks.forEach(function(h){h();});}
if(MOTION_OK) play();
document.querySelector('.again').addEventListener('click',play);
"""


def flourish(cls="orn"):
    return ('<svg class="%s" viewBox="0 0 240 30" aria-hidden="true"><path d="M 8 15 C 48 15 70 2 100 12 '
            'C 110 16 114 21 120 15 C 126 21 130 16 140 12 C 170 2 192 15 232 15" fill="none" '
            'stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
            '<path d="M 120 5 L 125 15 L 120 25 L 115 15 Z" fill="currentColor"/>'
            '<circle cx="8" cy="15" r="2.4" fill="currentColor"/><circle cx="232" cy="15" r="2.4" fill="currentColor"/>'
            '</svg>' % cls)


def cloud_bank():
    """A wall of storybook cloud, its puffy edge down the right-hand side."""
    rows = []
    blobs = []
    # Drawn about the size it is shown, so the puffs stay puffs. The billowing
    # edge sits inside the drawing so its outline shows.
    edge = [(800 + (i % 2) * 70, -30 + i * 88, 74 + (i % 3) * 16) for i in range(11)]
    inner = [(640 + (i % 3) * 40, 10 + i * 96, 104) for i in range(9)]
    big = [(200, 100, 260), (340, 420, 280), (180, 720, 260), (520, 180, 200), (520, 640, 210)]
    blobs = big + inner + edge
    rows.append('<svg viewBox="0 0 1000 800" preserveAspectRatio="xMaxYMid slice">')
    for x, y, r in blobs:
        rows.append('<circle cx="%d" cy="%d" r="%d" fill="%s" stroke="%s" stroke-width="8"/>' % (x, y, r, DEEP, DEEP))
    # the body covers every inner outline, leaving only the billowing edge inked
    rows.append('<rect x="-10" y="-10" width="700" height="820" fill="%s"/>' % WHITE)
    for x, y, r in blobs:
        rows.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (x, y, r, CREAM))
    # white tops over cream undersides, so each puff has volume
    for x, y, r in blobs:
        rows.append('<circle cx="%d" cy="%d" r="%d" fill="#fff"/>' % (x - r * .1, y - r * .14, r * .82))
    for x, y, r in edge:
        rows.append('<path d="M %d %d a %d %d 0 0 0 %d 0" fill="none" stroke="%s" stroke-width="9" '
                    'stroke-linecap="round" opacity=".5"/>' % (x - r * .55, y + r * .45, r * .55, r * .3, r * 1.1, SAGE))
        rows.append('<circle cx="%d" cy="%d" r="%d" fill="#fff" opacity=".8"/>' % (x - r * .3, y - r * .38, r * .16))
    rows.append("</svg>")
    return "".join(rows)


def ribbon_flight():
    from park_map import bird
    return ('<svg viewBox="0 0 900 220" aria-hidden="true">'
            '<path d="M 150 110 C 260 60 330 170 450 120 C 570 70 640 170 760 116" fill="none" stroke="%s" stroke-width="2"/>'
            '<path d="M 170 96 C 280 50 340 150 450 104 C 560 58 630 150 740 100 L 750 142 C 640 192 570 102 450 146 '
            'C 330 192 270 96 180 142 Z" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
            '<text x="460" y="134" text-anchor="middle" font-family="Cormorant Garamond,Georgia,serif" font-size="34" '
            'font-style="italic" font-weight="600" fill="%s">Welcome to the Valley</text>'
            '<g class="park-map" style="overflow:visible">%s%s</g></svg>' % (
                DEEP, CREAM, DEEP, DEEP, bird(150, 104, 1.6), bird(790, 108, 1.6)))


def vines():
    """Two vines growing from the top of the frame down both sides to meet at
    the bottom, with leaves and flowers opening behind them as they go."""
    W, H, m = 2000, 800, 30
    # perimeter from top middle, clockwise to bottom middle
    pts_r = [(W / 2, m), (W - m, m), (W - m, H - m), (W / 2, H - m)]

    def walk(corners):
        out = []
        for (ax, ay), (bx, by) in zip(corners, corners[1:]):
            n = int(math.hypot(bx - ax, by - ay) / 36)
            for k in range(n):
                t = k / float(n)
                out.append((ax + (bx - ax) * t, ay + (by - ay) * t, (bx - ax, by - ay)))
        out.append((corners[-1][0], corners[-1][1], (-1, 0)))
        return out

    art = []
    for side in (1, -1):
        corners = [(W / 2 + side * (x - W / 2), y) for x, y in pts_r]
        pts = walk(corners)
        path = []
        leaves = []
        for i, (x, y, (dx, dy)) in enumerate(pts):
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            wob = math.sin(i * .9) * 9
            px, py = x + nx * wob, y + ny * wob
            path.append((px, py))
            if i % 2 == 0 and 0 < i < len(pts) - 1:
                s = 1 if (i // 2) % 2 else -1
                ang = math.degrees(math.atan2(ny * s, nx * s)) + (30 * side)
                leaves.append((px, py, ang, i / float(len(pts)), (i // 2) % 5 == 2))
        d = "M %.0f %.0f " % path[0] + " ".join(
            "Q %.0f %.0f %.0f %.0f" % (path[k][0], path[k][1], (path[k][0] + path[k + 1][0]) / 2,
                                       (path[k][1] + path[k + 1][1]) / 2) for k in range(1, len(path) - 1))
        art.append('<path class="vine" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="7" '
                   'stroke-linecap="round"/>' % (d, DEEP))
        art.append('<path class="vine" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="4" '
                   'stroke-linecap="round"/>' % (d, OLIVE))
        for x, y, ang, t, flower in leaves:
            delay = .2 + t * 2.4
            if flower:
                petals = "".join(
                    '<circle cx="%.1f" cy="%.1f" r="7" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                        math.cos(math.radians(a)) * 8, math.sin(math.radians(a)) * 8, WHITE, DEEP)
                    for a in range(0, 360, 72))
                art.append('<g transform="translate(%.0f %.0f)"><g class="leaf" style="--ld:%.2fs">%s'
                           '<circle r="5" fill="%s" stroke="%s" stroke-width="1.4"/></g></g>' % (
                               x, y, delay, petals, CLAY, DEEP))
            else:
                art.append('<g transform="translate(%.0f %.0f) rotate(%.0f)"><path class="leaf" style="--ld:%.2fs" '
                           'd="M 0 0 Q 12 -12 30 0 Q 12 12 0 0 Z" fill="%s" stroke="%s" stroke-width="1.8" '
                           'stroke-linejoin="round"/></g>' % (x, y, ang, delay, SAGE if int(t * 40) % 3 else OLIVE, DEEP))
    return ('<svg class="vines" viewBox="0 0 2000 800" aria-hidden="true">%s</svg>' % "".join(art))


def seal():
    pts = []
    for k in range(48):
        a = k / 48.0 * math.pi * 2
        r = 96 if k % 2 else 88
        pts.append("%.1f,%.1f" % (100 + r * math.cos(a), 100 + r * math.sin(a)))
    return ('<svg viewBox="0 0 200 200" aria-hidden="true"><polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="100" r="66" fill="none" stroke="%s" '
            'stroke-width="2.4"/><circle cx="100" cy="100" r="58" fill="none" stroke="%s" stroke-width="1" opacity=".8"/>'
            '<text x="100" y="118" text-anchor="middle" font-family="Cormorant Garamond,Georgia,serif" '
            'font-size="58" font-style="italic" font-weight="600" fill="%s">VV</text>'
            '<path d="M 60 70 q 8 -14 20 -16 M 140 130 q -8 14 -20 16" stroke="%s" stroke-width="3" fill="none" '
            'stroke-linecap="round" opacity=".6"/></svg>' % (" ".join(pts), CLAY, DEEP, CREAM, CREAM, CREAM, CREAM))


COACH = (
    '<g class="coach-flip">'
    # shadow
    '<ellipse cx="20" cy="2" rx="96" ry="9" fill="#34372F" opacity=".16"/>'
    # the horse
    '<g class="horse">'
    '<path class="leg l1" d="M 62 -20 L 58 0" stroke="#34372F" stroke-width="5" stroke-linecap="round"/>'
    '<path class="leg l2" d="M 90 -20 L 96 0" stroke="#34372F" stroke-width="5" stroke-linecap="round"/>'
    '<ellipse cx="76" cy="-30" rx="26" ry="14" fill="#FFFFFF" stroke="#34372F" stroke-width="2.6"/>'
    '<path d="M 94 -38 L 108 -62 Q 116 -66 122 -58 L 124 -50 Q 118 -46 110 -50 L 102 -32 Z" fill="#FFFFFF" '
    'stroke="#34372F" stroke-width="2.6" stroke-linejoin="round"/>'
    '<path d="M 100 -40 Q 104 -58 114 -66 Q 106 -52 108 -40" fill="#B38A64" stroke="#34372F" stroke-width="1.6"/>'
    '<path d="M 110 -66 Q 108 -80 118 -86 Q 116 -74 118 -66 Z" fill="#679AA7" stroke="#34372F" stroke-width="1.6"/>'
    '<circle cx="116" cy="-57" r="1.8" fill="#34372F"/>'
    '<path d="M 50 -34 Q 38 -30 40 -16" fill="none" stroke="#B38A64" stroke-width="5" stroke-linecap="round"/>'
    '<path class="leg l3" d="M 66 -20 L 70 0" stroke="#34372F" stroke-width="5" stroke-linecap="round"/>'
    '<path class="leg l4" d="M 86 -20 L 82 0" stroke="#34372F" stroke-width="5" stroke-linecap="round"/>'
    '</g>'
    '<path d="M 26 -26 L 58 -30" stroke="#34372F" stroke-width="3"/>'
    # the coach: round, white, clay trim, a star on top
    '<path d="M -34 -26 Q -40 -76 0 -80 Q 40 -76 34 -26 Q 0 -16 -34 -26 Z" fill="#FFFFFF" stroke="#34372F" '
    'stroke-width="2.8" stroke-linejoin="round"/>'
    '<path d="M -30 -34 Q 0 -24 30 -34" fill="none" stroke="#B38A64" stroke-width="4"/>'
    '<path d="M 0 -80 Q -6 -52 0 -26 M -22 -74 Q -28 -50 -24 -30 M 22 -74 Q 28 -50 24 -30" fill="none" '
    'stroke="#B38A64" stroke-width="2" opacity=".8"/>'
    '<ellipse cx="0" cy="-54" rx="12" ry="14" fill="#679AA7" fill-opacity=".55" stroke="#34372F" stroke-width="2"/>'
    '<path d="M 0 -80 L 0 -92" stroke="#34372F" stroke-width="2"/>'
    '<path transform="translate(0 -98) scale(.8)" d="' + STAR + '" fill="#FFF0DA" stroke="#34372F" stroke-width="1.8"/>'
    # wheels
    '<g transform="translate(-22 -10)"><g class="wheel"><circle r="12" fill="#FFF0DA" stroke="#34372F" stroke-width="2.6"/>'
    '<path d="M -12 0 H 12 M 0 -12 V 12 M -8 -8 L 8 8 M 8 -8 L -8 8" stroke="#B38A64" stroke-width="1.6"/></g></g>'
    '<g transform="translate(24 -10)"><g class="wheel"><circle r="12" fill="#FFF0DA" stroke="#34372F" stroke-width="2.6"/>'
    '<path d="M -12 0 H 12 M 0 -12 V 12 M -8 -8 L 8 8 M 8 -8 L -8 8" stroke="#B38A64" stroke-width="1.6"/></g></g>'
    '</g>'
)

D0 = "M 1075 800 C 1075 720 1040 660 1010 610 C 980 560 975 520 975 470"
D1 = " C 1080 470 1160 456 1228 444 C 1292 432 1340 424 1392 420"
LOOP = " C 900 486 840 492 786 490 C 676 498 566 486 522 456"
WEST = " C 460 468 380 470 300 466 C 240 470 190 466 150 452"
TOURS = [
    D0 + LOOP + " C 486 430 508 398 572 386 C 652 372 742 378 792 400 C 828 416 822 450 792 468 "
    "C 784 474 790 484 786 490 C 676 498 566 486 522 456" + WEST +
    " C 108 430 112 372 128 318 C 146 258 200 222 268 206 C 420 172 700 140 900 118 C 1010 106 1100 98 1180 94",
    D0 + D1 + " C 1420 398 1436 360 1452 330 C 1470 296 1508 282 1548 282",
    D0 + D1 + " C 1388 460 1380 492 1372 520",
    D0 + LOOP + WEST + " C 118 490 96 540 92 592 C 88 648 118 686 165 700",
]


def V(slug, name, blurb, css, js, pop=True, **kw):
    d = dict(slug=slug, name=name, blurb=blurb, renderer="park", opts=dict(fairy=True),
             css=FAIRY_CSS + (POP_CSS if pop else "") + css, js=HELPERS + js + TAIL)
    d.update(kw)
    return d


FAIRY = [

    V("16", "Once Upon a Time",
      "The map arrives as a closed storybook: an olive cover, a title, a glint across the lettering. "
      "The cover swings open on its spine, sparkles spill out over the page, and the estate builds "
      "itself underneath.",
      css="""
.lab-stage{--o:2.5s}
.book{position:relative;perspective:2400px}
.cover{display:none;position:absolute;inset:0;z-index:20;transform-origin:0 50%;transform-style:preserve-3d;pointer-events:none}
.go .cover{display:block;animation:open 3.3s cubic-bezier(.65,0,.3,1) forwards}
@keyframes open{0%,34%{transform:rotateY(0)}88%{transform:rotateY(-168deg);opacity:1}100%{transform:rotateY(-180deg);opacity:0}}
.cv-front,.cv-back{position:absolute;inset:0;backface-visibility:hidden;border-radius:18px;overflow:hidden}
.cv-front{background:var(--olive);display:grid;place-items:center;color:var(--cream);
  box-shadow:inset 0 0 0 clamp(8px,1.2vw,16px) var(--olive),inset 0 0 0 clamp(10px,1.4vw,19px) var(--cream),
  inset 0 0 0 clamp(14px,2vw,26px) var(--olive),inset 0 0 0 clamp(15px,2.1vw,28px) var(--cream)}
.cv-back{background:var(--cream);transform:rotateY(180deg);box-shadow:inset -30px 0 60px rgba(52,55,47,.12)}
.cv-in{text-align:center;padding:1rem}
.cv-once{font:600 clamp(.6rem,1.1vw,.9rem)/1.3 var(--sans);letter-spacing:.3em;text-transform:uppercase;margin:.6rem 0}
.cv-title{font-family:var(--display);font-style:italic;font-weight:500;font-size:clamp(2.2rem,7vw,6.4rem);
  line-height:1;margin:.1em 0 .15em}
.cv-sub{font:500 clamp(.6rem,1vw,.85rem)/1.3 var(--sans);letter-spacing:.24em;text-transform:uppercase;margin:.4rem 0 .8rem}
.orn{width:clamp(120px,22vw,300px);height:auto;color:var(--cream)}
.cv-shine{position:absolute;inset:0;background:linear-gradient(105deg,rgba(255,255,255,0) 42%,rgba(255,255,255,.5) 50%,rgba(255,255,255,0) 58%);
  background-size:260% 100%;background-position:120% 0}
.go .cv-shine{animation:shine 1.1s ease-in-out .25s forwards}
@keyframes shine{to{background-position:-60% 0}}
""",
      js="""
hooks.push(function(){
  later(function(){for(var i=0;i<46;i++)(function(i){later(function(){
    spark(80+Math.random()*900,80+Math.random()*640,{dx:(Math.random()-.2)*160,dy:(Math.random()-.5)*120,life:1300});},i*22);})(i);},1500);
});
""",
      wrap=('<div class="book">', '<div class="cover" aria-hidden="true"><div class="cv-front"><div class="cv-in">'
            + flourish() + '<p class="cv-once">Once upon a time, beneath Lookout Mountain</p>'
            '<h2 class="cv-title">The Valley Venues</h2><p class="cv-sub">An estate map &middot; Wildwood, Georgia</p>'
            + flourish() + '</div><span class="cv-shine"></span></div><div class="cv-back"></div></div></div>')),

    V("17", "Pixie Dust",
      "A wand-light swoops in from the woods and sweeps across the estate in one long arc. Everything it "
      "passes comes into being behind it, in a trail of sparkles, and each place jumps awake as it is "
      "touched.",
      pop=False,
      css="""
.park-map .wand{pointer-events:none}
.park-map .wand circle{animation:glow .5s ease-in-out infinite alternate}
@keyframes glow{to{opacity:.35}}
.go .park-map .ban{transform-origin:50% 50%}
""",
      js="""
var TRAIL='M 60 820 C 120 560 380 420 620 360 C 880 300 900 640 1180 610 C 1460 580 1380 200 1680 170 C 1880 150 1980 300 2120 250';
var world=null;
hooks.push(function(){
  if(!world){world=document.createElementNS(NS,'g');world.setAttribute('class','world');
    Array.prototype.slice.call(map.childNodes).forEach(function(n){if(n.nodeName!=='defs')world.appendChild(n);});
    map.appendChild(world);}
  var defs=map.querySelector('defs');
  var m=mk('mask',{id:'dust',maskUnits:'userSpaceOnUse',x:-300,y:-300,width:2600,height:1400},defs);
  var base=mk('rect',{x:-300,y:-300,width:2600,height:1400,fill:'#fff','fill-opacity':0},m);
  var p=mk('path',{d:TRAIL,fill:'none',stroke:'#fff','stroke-width':520,'stroke-linecap':'round',pathLength:1,
    'stroke-dasharray':'1 1','stroke-dashoffset':1},m);
  var guide=mk('path',{d:TRAIL,fill:'none'},defs);
  world.setAttribute('mask','url(#dust)');
  var head=mk('g',{'class':'wand'});
  mk('circle',{r:30,fill:'#FFF0DA',opacity:.8},head);
  mk('path',{d:STAR,fill:'#fff',stroke:'#34372F','stroke-width':1.2,transform:'scale(2.2)'},head);
  var L=guide.getTotalLength(),t0=null,D=3200,done={},raf=0;
  var spots=KEYS.map(function(k){var q=where(k);return {k:k,x:q.x,y:q.y};});
  function finish(){base.style.transition='fill-opacity .7s ease';base.style.fillOpacity=1;
    spots.forEach(function(s){if(!done[s.k]){done[s.k]=1;hit(s.k);}});
    later(function(){world.removeAttribute('mask');m.remove();guide.remove();},800);}
  function step(now){if(t0===null)t0=now;var k=Math.min(1,(now-t0)/D),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    p.setAttribute('stroke-dashoffset',(1-e).toFixed(4));
    var pt=guide.getPointAtLength(e*L);head.setAttribute('transform','translate('+pt.x.toFixed(1)+' '+pt.y.toFixed(1)+')');
    for(var i=0;i<3;i++)spark(pt.x+(Math.random()-.5)*50,pt.y+(Math.random()-.5)*50,{dy:30+Math.random()*80,life:1300});
    spots.forEach(function(s){if(!done[s.k]&&Math.hypot(pt.x-s.x,pt.y-s.y)<300){done[s.k]=1;hit(s.k,18);}});
    if(k<1)raf=requestAnimationFrame(step);else{head.remove();finish();}}
  raf=requestAnimationFrame(step);
  cleanups.push(function(){cancelAnimationFrame(raf);if(world)world.removeAttribute('mask');m.remove();guide.remove();});
});
"""),

    V("18", "Fireworks over Magnolia House",
      "Magnolia House is the castle on this map, so it gets the castle's moment. The estate pops up "
      "as in 11, then fireworks go up over the house in daylight colours, and a sparkling arc draws "
      "itself over the roof before it fades.",
      css="""
.park-map .bl{transform-box:view-box;transform-origin:0 0;animation:bloom 1.6s cubic-bezier(.1,.8,.3,1) forwards}
@keyframes bloom{0%{transform:scale(.08);opacity:1}70%{opacity:1}100%{transform:scale(1.15);opacity:0}}
.park-map .rocket{stroke-dasharray:1 1;animation:rise .6s cubic-bezier(.2,.6,.4,1) forwards}
@keyframes rise{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
""",
      js="""
function bloom(x,y,col,big){var g=mk('g',{transform:'translate('+x+' '+y+')'}),b=mk('g',{'class':'bl'},g),n=big?22:16,r=big?120:88;
  for(var i=0;i<n;i++){var a=i/n*6.283;
    mk('line',{x1:(Math.cos(a)*16).toFixed(1),y1:(Math.sin(a)*16).toFixed(1),x2:(Math.cos(a)*r).toFixed(1),y2:(Math.sin(a)*r).toFixed(1),
      stroke:col,'stroke-width':big?5:4,'stroke-linecap':'round'},b);
    mk('path',{d:STAR,transform:'translate('+(Math.cos(a)*(r+14)).toFixed(1)+' '+(Math.sin(a)*(r+14)).toFixed(1)+') scale(.55)',
      fill:i%2?'#FFFFFF':'#FFF0DA',stroke:'#34372F','stroke-width':1.6},b);}
  mk('circle',{r:10,fill:'#FFFFFF',stroke:'#34372F','stroke-width':1.6},b);
  burst(x,y,10,big?150:110);setTimeout(function(){g.remove();},1700);}
function rocket(x,y,col,at,big){later(function(){
  var sx=652+(x-652)*.3,sy=330;
  mk('path',{d:'M '+sx+' '+sy+' Q '+((sx+x)/2+30)+' '+(y+90)+' '+x+' '+y,fill:'none',stroke:'#B38A64','stroke-width':3,
    'stroke-linecap':'round',pathLength:1,'class':'rocket'});
  later(function(){layer().querySelectorAll('.rocket').forEach(function(r){r.remove();});bloom(x,y,col,big);},600);},at);}
hooks.push(function(){
  var T=2500;
  rocket(652,120,'#B38A64',T,true);
  rocket(470,170,'#679AA7',T+500);
  rocket(840,160,'#AABEB3',T+800);
  rocket(560,70,'#9A9F83',T+1250);
  rocket(760,80,'#679AA7',T+1500);
  rocket(652,130,'#B38A64',T+2000,true);
  // the arc over the roof
  later(function(){var A={x:420,y:360},C={x:652,y:-10},B={x:900,y:340},n=34;
    for(var i=0;i<=n;i++)(function(i){later(function(){var t=i/n,u=1-t;
      var x=u*u*A.x+2*u*t*C.x+t*t*B.x,y=u*u*A.y+2*u*t*C.y+t*t*B.y;
      spark(x,y,{dx:0,dy:6,s:.5+Math.sin(t*Math.PI)*.6,life:2200,fill:i%3?'#FFFFFF':'#FFF0DA'});
      if(i%4===0)spark(x,y,{dy:40,life:1200});},i*38);})(i);
    later(function(){hit('magnolia',22);},n*38);},T+2900);
});
"""),

    V("19", "The Pop-up Book",
      "The page starts lying flat, tilted away from you like a book open on a table. It lifts up to "
      "face you, and the trees and buildings stand up off the paper the way pop-up pieces do when "
      "the page opens.",
      css="""
.lab-stage{perspective:1500px;--o:1.1s}
.popup{transform-origin:50% 100%;border-radius:18px}
.go .popup{animation:lift 1.6s cubic-bezier(.3,1.05,.4,1) backwards}
@keyframes lift{0%{transform:rotateX(66deg) translateY(10%) scale(.86)}100%{transform:none}}
.popup::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:18px;
  background:linear-gradient(90deg,rgba(52,55,47,0) 47%,rgba(52,55,47,.13) 50%,rgba(52,55,47,0) 53%);opacity:0}
.go .popup::after{animation:crease 2.4s ease forwards}
@keyframes crease{0%,40%{opacity:1}100%{opacity:0}}
.popup{position:relative}
.go .park-map .t{transform-origin:50% 100%;animation:stand .7s cubic-bezier(.3,1.7,.5,1) backwards;
  animation-delay:calc(1.1s + var(--d) * .6)}
@keyframes stand{from{transform:scaleY(0) skewX(-24deg)}}
.go .park-map .b{animation:standb 1s cubic-bezier(.25,1.7,.45,1) backwards;animation-delay:calc(1.5s + var(--bd) * 1.6)}
@keyframes standb{0%{transform:scaleY(0) skewX(12deg)}100%{transform:none}}
.go .park-map .ban{animation-delay:calc(2.3s + var(--bd))}
.go .rd-edge,.go .rd-body,.go .rd-shine{animation:none}
""",
      js="""
hooks.push(function(){KEYS.forEach(function(k,i){later(function(){var p=where(k);burst(p.x,p.y+10,8,90);},1600+i*160);});});
""",
      wrap=('<div class="popup">', '</div>')),

    V("20", "The Clouds Part",
      "The map opens behind a bank of storybook cloud. Two bluebirds fly through carrying a ribbon "
      "that says Welcome to the Valley, the clouds roll back to either side like curtains, and the "
      "estate is there underneath.",
      css="""
.lab-stage{--o:1.7s}
.skyveil{position:relative;overflow:hidden;border-radius:18px}
.veil{display:none;position:absolute;inset:0;z-index:20;pointer-events:none}
.go .veil{display:block}
.veil::before{content:"";position:absolute;inset:0;background:var(--sage)}
.go .veil::before{animation:skyoff 1.4s ease 1.6s forwards}
@keyframes skyoff{to{opacity:0}}
.cl{position:absolute;top:-6%;height:112%;width:60%}
.cl svg{width:100%;height:100%;display:block}
.cl.left{left:-2%}
.cl.right{right:-2%}
.cl.right svg{transform:scaleX(-1)}
.go .cl.left{animation:partl 2.4s cubic-bezier(.6,0,.3,1) 1.2s forwards}
.go .cl.right{animation:partr 2.4s cubic-bezier(.6,0,.3,1) 1.2s forwards}
@keyframes partl{to{transform:translateX(-108%) scale(1.1)}}
@keyframes partr{to{transform:translateX(108%) scale(1.1)}}
.flight{position:absolute;left:0;top:26%;width:52%;z-index:3}
.flight svg{width:100%;height:auto;display:block;overflow:visible}
.go .flight{animation:flight 3.4s cubic-bezier(.45,.05,.55,.95) .1s both}
@keyframes flight{0%{transform:translate(-105%,30%) rotate(4deg)}50%{transform:translate(48%,-6%) rotate(-2deg)}
  100%{transform:translate(210%,-70%) rotate(-8deg)}}
.flight .wing{transform-box:fill-box;transform-origin:50% 100%;animation:flap .6s ease-in-out infinite alternate}
""",
      js="",
      wrap=('<div class="skyveil">', '<div class="veil" aria-hidden="true"><div class="cl left">' + cloud_bank()
            + '</div><div class="cl right">' + cloud_bank() + '</div><div class="flight">' + ribbon_flight()
            + '</div></div></div>')),

    V("21", "The Storybook Page",
      "The map as a page from the book. A line of the story writes itself above it, and a flowering "
      "vine grows round the frame from the top down both sides, leaves and blossoms opening behind it "
      "as the estate appears.",
      css="""
.lab-stage{--o:.7s}
.tale{max-width:62rem;margin:.4rem auto 1rem;padding:0 1rem;font-family:var(--display);font-style:italic;
  font-size:clamp(1.1rem,2.2vw,1.6rem);line-height:1.35;color:var(--deep);min-height:2.7em}
.tale .cap{float:left;font-style:normal;font-weight:500;font-size:3.4em;line-height:.8;color:var(--clay);
  margin:.06em .12em 0 0;padding:.06em .14em;border:1.5px solid var(--olive);border-radius:6px;background:#fff}
.page21{position:relative}
.vines{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:4;overflow:visible}
.vines .vine{stroke-dasharray:1 1}
.go .vines .vine{animation:draw 2.8s cubic-bezier(.45,0,.4,1) backwards}
.vines .leaf{transform-box:fill-box;transform-origin:0 50%}
.vines g > g.leaf{transform-origin:50% 50%}
.go .vines .leaf{animation:pop .5s cubic-bezier(.3,1.7,.5,1) backwards;animation-delay:var(--ld)}
""",
      js="""
var TALE=document.querySelector('.tale-text'),TEXT=TALE.textContent;
hooks.push(function(){TALE.textContent='';var i=0;
  (function type(){if(i>TEXT.length)return;TALE.textContent=TEXT.slice(0,i);i+=1;later(type,22);})();});
""",
      wrap=('<p class="tale"><span class="cap">O</span><span class="tale-text">nce upon a time, beneath Lookout '
            'Mountain and fifteen minutes from downtown Chattanooga, there was a valley of seventy-four acres.'
            '</span></p><div class="page21">', vines() + '</div>')),

    V("22", "The Carriage Ride",
      "After the estate pops up, a little white carriage sets out from the front gate and keeps "
      "touring the drives: round Magnolia House and up to the village, to Davis Hall, down to the "
      "meadow, out to the cabin in the woods. Each place wakes with a sparkle as it passes.",
      css="""
.park-map .coach{pointer-events:none;transition:opacity .5s ease}
.park-map .wheel{transform-box:fill-box;transform-origin:50% 50%;animation:roll .9s linear infinite}
@keyframes roll{to{transform:rotate(360deg)}}
.park-map .leg{transform-box:fill-box;transform-origin:50% 0;animation:trot .36s ease-in-out infinite alternate}
.park-map .l2,.park-map .l3{animation-delay:-.18s}
@keyframes trot{from{transform:rotate(-18deg)}to{transform:rotate(18deg)}}
.park-map .coach-flip{transition:transform .35s ease}
""",
      js="""
var TOURS=%(tours)s;
hooks.push(function(){
  var coach=null,raf=0,leg=0;
  function run(){
    var d=TOURS[leg%%TOURS.length];leg+=1;
    var guide=mk('path',{d:d,fill:'none'});var L=guide.getTotalLength(),t0=null,D=L/.2,done={},lastX=null,flip=1,n=0;
    if(!coach){coach=mk('g',{'class':'coach'});coach.innerHTML='%(coach)s';}
    var inner=coach.querySelector('.coach-flip');coach.style.opacity=0;
    var spots=KEYS.map(function(k){var q=where(k);return {k:k,x:q.x,y:q.y};});
    function step(now){if(t0===null){t0=now;coach.style.opacity=1;}
      var k=Math.min(1,(now-t0)/D),pt=guide.getPointAtLength(k*L);
      if(lastX!==null&&Math.abs(pt.x-lastX)>.4){var f=pt.x<lastX?-1:1;if(f!==flip){flip=f;inner.setAttribute('transform','scale('+f+' 1)');}}
      lastX=pt.x;coach.setAttribute('transform','translate('+pt.x.toFixed(1)+' '+(pt.y+4).toFixed(1)+') scale(1.05)');
      if((n++)%%6===0)spark(pt.x-flip*30,pt.y-20,{dy:-10-Math.random()*30,dx:-flip*(10+Math.random()*30),life:1000,s:.5});
      spots.forEach(function(s){if(!done[s.k]&&Math.hypot(pt.x-s.x,pt.y-s.y)<170){done[s.k]=1;hit(s.k,16);}});
      if(k<1)raf=requestAnimationFrame(step);
      else{coach.style.opacity=0;guide.remove();later(run,1400);}}
    raf=requestAnimationFrame(step);}
  later(run,2600);
  cleanups.push(function(){cancelAnimationFrame(raf);});
});
""" % dict(tours="[" + ",".join("'%s'" % t for t in TOURS) + "]", coach=COACH)),

    V("23", "The Living Map",
      "Everything on the map is alive once it has popped up: the trees sway, the creek runs, the "
      "pennants blow, bluebirds and butterflies go about their business. Your pointer becomes a wand "
      "that trails sparkles, and a click scatters a handful of them.",
      css="""
.go .park-map .t{animation:pop .55s cubic-bezier(.3,1.7,.55,1) backwards,sway 3.4s ease-in-out infinite alternate;
  animation-delay:calc(.35s + var(--d)),calc(2.4s + var(--d) * 3)}
@keyframes sway{from{transform:rotate(-2.2deg)}to{transform:rotate(2.2deg)}}
.park-map .water path:nth-child(3){animation:flow 1.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-64}}
.park-map .rd-dash{animation:none}
.lab-stage.wandy{cursor:none}
.wspark{position:absolute;z-index:50;pointer-events:none;width:22px;height:22px;margin:-11px 0 0 -11px;
  animation:wsp .9s ease-out forwards}
.wspark svg{width:100%;height:100%;display:block}
.wtip{position:absolute;z-index:51;pointer-events:none;width:30px;height:30px;margin:-15px 0 0 -15px;display:none}
.wandy .wtip{display:block}
@keyframes wsp{0%{transform:scale(1) rotate(0)}100%{transform:translate(var(--x),var(--y)) scale(0) rotate(160deg);opacity:.2}}
""",
      js="""
var STARSVG='<svg viewBox="-12 -12 24 24"><path d="'+STAR+'" fill="FILL" stroke="#34372F" stroke-width="1.4"/></svg>';
var tip=document.createElement('div');tip.className='wtip';tip.innerHTML=STARSVG.replace('FILL','#FFFFFF');st.appendChild(tip);
var lastSpark=0;
function wspark(x,y,dx,dy){var s=document.createElement('div');s.className='wspark';
  s.innerHTML=STARSVG.replace('FILL',INKS[Math.random()*INKS.length|0]);
  s.style.left=x+'px';s.style.top=y+'px';s.style.setProperty('--x',dx+'px');s.style.setProperty('--y',dy+'px');
  var k=.5+Math.random()*.7;s.style.width=s.style.height=(22*k)+'px';st.appendChild(s);setTimeout(function(){s.remove();},950);}
st.addEventListener('mousemove',function(e){if(!MOTION_OK)return;var r=st.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
  st.classList.add('wandy');tip.style.left=x+'px';tip.style.top=y+'px';
  var now=Date.now();if(now-lastSpark<28)return;lastSpark=now;wspark(x,y,(Math.random()-.5)*40,10+Math.random()*40);});
st.addEventListener('mouseleave',function(){st.classList.remove('wandy');});
st.addEventListener('click',function(e){if(!MOTION_OK||e.target.closest('.again,a'))return;var r=st.getBoundingClientRect();
  for(var i=0;i<16;i++){var a=i/16*6.283;wspark(e.clientX-r.left,e.clientY-r.top,Math.cos(a)*70,Math.sin(a)*70);}});
"""),

    V("24", "The Sealed Scroll",
      "A scroll arrives rolled and sealed with a clay VV. The seal cracks, the two rollers run apart "
      "to the edges of the page, and the map unrolls between them before the buildings spring up.",
      css="""
.lab-stage{--o:2.6s}
.scroll{position:relative}
.go .sheet{animation:unroll 1.9s cubic-bezier(.6,0,.3,1) 1.15s backwards}
@keyframes unroll{from{clip-path:inset(0 49.3% 0 49.3%)}to{clip-path:inset(0 0 0 0)}}
.rod{display:none;position:absolute;top:-2%;bottom:-2%;width:clamp(14px,1.9vw,28px);z-index:10;border-radius:999px;
  background:linear-gradient(90deg,var(--clay) 0 26%,var(--cream) 26% 40%,var(--clay) 40% 100%);border:2px solid var(--deep)}
.rod::before,.rod::after{content:"";position:absolute;left:50%;width:170%;aspect-ratio:1;border-radius:50%;
  background:var(--clay);border:2px solid var(--deep);transform:translateX(-50%)}
.rod::before{top:-12px}
.rod::after{bottom:-12px}
.go .rod{display:block}
.go .rl{animation:rodl 1.9s cubic-bezier(.6,0,.3,1) 1.15s both}
.go .rr{animation:rodr 1.9s cubic-bezier(.6,0,.3,1) 1.15s both}
@keyframes rodl{0%{left:calc(50% - clamp(14px,1.9vw,28px))}88%{left:-6px;opacity:1}100%{left:-6px;opacity:0}}
@keyframes rodr{0%{left:50%}88%{left:calc(100% - clamp(14px,1.9vw,28px) + 6px);opacity:1}100%{left:calc(100% - clamp(14px,1.9vw,28px) + 6px);opacity:0}}
.seal{display:none;position:absolute;left:50%;top:50%;width:clamp(76px,10vw,140px);aspect-ratio:1;
  transform:translate(-50%,-50%);z-index:12;pointer-events:none}
.go .seal{display:block;animation:sealin .5s cubic-bezier(.3,1.6,.5,1) backwards}
@keyframes sealin{from{transform:translate(-50%,-50%) scale(0) rotate(-40deg)}}
.half{position:absolute;inset:0}
.half svg{width:100%;height:100%;display:block}
.h1{clip-path:polygon(0 0,56% 0,44% 40%,58% 62%,42% 100%,0 100%)}
.h2{clip-path:polygon(56% 0,100% 0,100% 100%,42% 100%,58% 62%,44% 40%)}
.go .h1{animation:crackl 1.2s cubic-bezier(.5,0,.5,1) .5s forwards}
.go .h2{animation:crackr 1.2s cubic-bezier(.5,0,.5,1) .5s forwards}
@keyframes crackl{0%,30%{transform:none}38%{transform:rotate(-5deg)}46%{transform:rotate(4deg)}100%{transform:translate(-80%,70%) rotate(-50deg);opacity:0}}
@keyframes crackr{0%,30%{transform:none}38%{transform:rotate(5deg)}46%{transform:rotate(-4deg)}100%{transform:translate(80%,70%) rotate(50deg);opacity:0}}
.go .park-map .t{animation:none}
.go .rd-edge,.go .rd-body,.go .rd-shine{animation:none}
""",
      js="""
hooks.push(function(){later(function(){burst(1000,400,22,190);},1050);});
""",
      wrap=('<div class="scroll"><div class="sheet">', '</div><div class="rod rl"></div><div class="rod rr"></div>'
            '<div class="seal" aria-hidden="true"><span class="half h1">' + seal() + '</span><span class="half h2">'
            + seal() + '</span></div></div>')),

    V("25", "The Title Card",
      "It opens like the start of the film: a title card, and a sparkling arc sweeping over the name "
      "the way one sweeps over the castle. Then the whole card shrinks up into the corner of the map, "
      "becomes its title, and the estate pops up below.",
      css="""
.lab-stage{--o:2.7s}
.tcwrap{position:relative;overflow:hidden;border-radius:18px}
.tcard{display:none;position:absolute;inset:0;z-index:20;background:var(--cream);place-items:center;pointer-events:none;
  transform-origin:88% 10%}
.go .tcard{display:grid;animation:tcout 1.1s cubic-bezier(.6,0,.3,1) 2.5s forwards}
@keyframes tcout{to{transform:scale(.18);opacity:0;border-radius:40px}}
.tc-in{position:relative;text-align:center;color:var(--deep);padding:2rem 1rem}
.tc-arc{position:absolute;left:50%;top:50%;width:min(92%,900px);transform:translate(-50%,-62%);overflow:visible}
.tc-arc .arc{stroke-dasharray:1 1}
.go .tc-arc .arc{animation:draw 1.6s cubic-bezier(.5,0,.3,1) .35s backwards}
.tc-pre{font:600 clamp(.6rem,1.1vw,.9rem)/1 var(--sans);letter-spacing:.34em;text-transform:uppercase;margin:0 0 .6rem;color:var(--clay)}
.tc-title{font-family:var(--display);font-style:italic;font-weight:500;font-size:clamp(2.4rem,8vw,7rem);line-height:1;margin:0}
.tc-sub{font:500 clamp(.6rem,1vw,.85rem)/1 var(--sans);letter-spacing:.26em;text-transform:uppercase;margin:1rem 0 .6rem}
.tc-in .orn{width:clamp(140px,24vw,320px);color:var(--olive)}
.go .tc-title{animation:tcin 1s cubic-bezier(.2,.8,.3,1) backwards}
@keyframes tcin{from{opacity:0;transform:translateY(12px) scale(.96);letter-spacing:.06em}}
.go .tc-pre,.go .tc-sub,.go .tc-in .orn{animation:fade .8s ease .5s backwards}
""",
      js="""
hooks.push(function(){
  var svg=document.querySelector('.tc-arc'),arc=svg.querySelector('.arc'),L=arc.getTotalLength(),n=40;
  for(var i=0;i<=n;i++)(function(i){later(function(){var pt=arc.getPointAtLength(i/n*L);
    spark(pt.x,pt.y,{dx:(Math.random()-.5)*20,dy:10+Math.random()*30,life:1300,s:.5+Math.sin(i/n*Math.PI)*.7},svg);
    if(i===n)burst(pt.x,pt.y,12,60,svg);},350+i*40);})(i);
});
""",
      wrap=('<div class="tcwrap">', '<div class="tcard" aria-hidden="true"><div class="tc-in">'
            '<svg class="tc-arc" viewBox="0 0 900 300"><path class="arc" pathLength="1" '
            'd="M 40 280 Q 430 -120 860 170" fill="none" stroke="#B38A64" stroke-width="3" stroke-linecap="round"/></svg>'
            '<p class="tc-pre">Welcome to</p><h2 class="tc-title">The Valley Venues</h2>'
            '<p class="tc-sub">An estate map &middot; Wildwood, Georgia</p>' + flourish() + '</div></div></div>')),
]
