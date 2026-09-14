"""Variations 11-15: the park map, drawn by _tools/park_map.py.

The note on the last round was fewer gimmicks, more variations of the original
look, and as Disney as the palette allows. So these share one drawing and differ
in three honest ways: what the ground is made of (rolling hills, or the LiDAR
survey), what the places are drawn from (traced line art, or the photographs
themselves), and how the map arrives.

Every intro is short, plays once, can be replayed, and never leaves anything
hidden at rest: the resting state is the finished map, and the animation only
runs when the stage carries .go.
"""

# Shared by all five: the pop-up vocabulary. --o offsets the whole sequence so a
# variation can put its own moment first.
PARK_CSS = """
.lab-stage{background:var(--cream);padding:clamp(.4rem,1.6vw,1.2rem)}
.park-map .t,.park-map .b,.park-map .ban,.park-map .cart,.park-map .gate,
.park-map .map-art,.park-map .cloud,.park-map .smoke{transform-box:fill-box}
.map-halo{display:none}
.map-place .map-art{transform-origin:50% 100%;transition:transform .45s cubic-bezier(.3,1.5,.5,1)}
.map-place:hover .map-art,.map-place:focus-visible .map-art{transform:translateY(-8px) scale(1.07)}
.map-place:hover .ban rect,.map-place:focus-visible .ban rect{fill:var(--paper,#fff)}
.map-place:focus{outline:none}

/* ambient, always: clouds drift, the fire pit smokes */
.park-map .cloud{animation:drift 26s ease-in-out infinite alternate}
.park-map .sky .cloud:nth-of-type(2){animation-duration:34s;animation-delay:-12s}
@keyframes drift{from{translate:-18px 0}to{translate:22px 0}}
.park-map .smoke{transform-origin:50% 100%;animation:smoke 3.2s ease-in-out infinite}
@keyframes smoke{0%{opacity:0;translate:0 6px}40%{opacity:.7}100%{opacity:0;translate:0 -14px}}

/* the intro */
.go .rd-edge,.go .rd-body,.go .rd-shine{stroke-dasharray:1 1;
  animation:draw 1.5s cubic-bezier(.55,0,.3,1) backwards;animation-delay:var(--o,0s)}
@keyframes draw{from{stroke-dashoffset:1}}
.go .rd-dash,.go .water,.go .parking,.go .signs,.go .meadow{
  animation:fade .7s ease backwards;animation-delay:calc(var(--o,0s) + 1.1s)}
@keyframes fade{from{opacity:0}}
.go .park-map .t{transform-origin:50% 100%;
  animation:pop .55s cubic-bezier(.3,1.7,.55,1) backwards;animation-delay:calc(var(--o,0s) + .35s + var(--d))}
@keyframes pop{from{transform:scale(0)}}
.go .park-map .b{transform-origin:50% 100%;
  animation:bounce .8s cubic-bezier(.3,1.2,.5,1) backwards;animation-delay:calc(var(--o,0s) + 1.15s + var(--bd))}
@keyframes bounce{0%{transform:scale(.1,0)}55%{transform:scale(.94,1.12)}78%{transform:scale(1.04,.96)}100%{transform:none}}
.go .park-map .ban{transform-origin:50% 50%;
  animation:unfurl .6s cubic-bezier(.3,1.5,.5,1) backwards;animation-delay:calc(var(--o,0s) + 1.6s + var(--bd))}
@keyframes unfurl{from{transform:scaleX(0)}}
.go .park-map .cart,.go .park-map .gate{transform-origin:50% 0;
  animation:hang .9s cubic-bezier(.3,1.6,.5,1) backwards;animation-delay:calc(var(--o,0s) + 2s)}
@keyframes hang{from{transform:translateY(-24px) rotate(-4deg);opacity:0}}

.again{position:absolute;right:clamp(.8rem,2vw,1.6rem);bottom:clamp(.8rem,2vw,1.6rem);z-index:30;
  font:600 .7rem/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--deep);
  background:var(--cream);border:1px solid var(--deep);padding:.6rem .8rem;border-radius:999px;cursor:pointer}
.again:hover{background:#fff}
@media (max-width:760px){.lab-stage{overflow-x:auto}.park-map{min-width:860px}}
"""

PARK_JS = """
peekInit();
var st=document.querySelector('.lab-stage');
function play(){st.classList.remove('go');void st.offsetWidth;st.classList.add('go');}
if(!matchMedia('(prefers-reduced-motion:reduce)').matches) play();
document.querySelector('.again').addEventListener('click',play);
"""

PHOTO_ICONS = {k: "/map-lab/icons/%s.png" % k for k in ("magnolia", "valley", "deck", "village", "woods")}

PARK = [

    dict(
        slug="11", name="The Park Map", renderer="park",
        blurb="The estate drawn the way a park map draws a kingdom, in the client's seven colours: "
              "puffy trees, ribbon banners, a gate on Pope Creek Road. The drives draw themselves in, "
              "the woods pop up west to east, and each building bounces into place.",
        opts={},
        css="",
        js="",
    ),

    dict(
        slug="12", name="Lidar Terraces", renderer="park",
        blurb="The same map on the real ground. The hills are the county's LiDAR survey of these "
              "74 acres, contoured and softened into terraces; the map rises out of the valley "
              "floor one level at a time before anything is built on it. The survey is warped onto "
              "Kobi's plan, which is drawn to be read, not to scale -- so the terraces are true in "
              "shape and approximate in place.",
        opts=dict(ground="terraces"),
        css="""
.lab-stage{--o:1.3s}
.park-map .lvl{transform-box:view-box}
.go .park-map .lvl{animation:rise .7s cubic-bezier(.3,1.3,.5,1) backwards;
  animation-delay:calc(var(--l) * .11s)}
@keyframes rise{from{opacity:0;transform:translateY(18px)}}
""",
        js="",
    ),

    dict(
        slug="13", name="Ink, then Colour", renderer="park",
        blurb="The map arrives as the artist's line drawing, and colour floods outward from the "
              "front gate like a wash across the page. When it settles it is the park map, "
              "with every building clickable.",
        opts={},
        css="""
.inkwash{position:relative}
.inkwash .colour{position:relative;z-index:2}
.inkwash .ink{position:absolute;inset:0;z-index:1;pointer-events:none}
.inkwash .ink *{fill:none !important;stroke:var(--deep) !important;stroke-width:1.1px !important;
  stroke-dasharray:none !important;opacity:1 !important;animation:none !important}
.inkwash .ink image,.inkwash .ink .land ellipse,.inkwash .ink .meadow{display:none}
.inkwash .ink .frame{stroke:var(--olive) !important;stroke-width:12px !important}
.go .inkwash .ink{animation:fade .8s ease backwards}
.go .inkwash .colour{animation:wash 2.8s cubic-bezier(.6,0,.35,1) 1.1s backwards}
@keyframes wash{from{clip-path:circle(0% at 53% 92%)}to{clip-path:circle(125% at 53% 92%)}}
.go .inkwash .colour .t,.go .inkwash .colour .b,.go .inkwash .colour .ban,
.go .inkwash .colour .cart,.go .inkwash .colour .gate{animation:none}
.go .inkwash .colour .rd-edge,.go .inkwash .colour .rd-body,.go .inkwash .colour .rd-shine,
.go .inkwash .colour .rd-dash,.go .inkwash .colour .water,.go .inkwash .colour .parking,
.go .inkwash .colour .signs,.go .inkwash .colour .meadow{animation:none}
.inkwash .colour .cloud{animation:drift 26s ease-in-out infinite alternate !important}
.inkwash .colour .smoke{animation:smoke 3.2s ease-in-out infinite !important}
""",
        js="",
    ),

    dict(
        slug="14", name="Screenprints", renderer="park",
        blurb="The places as posters cut from the photographs. Each picture is separated into the "
              "seven palette inks the way a screen printer would -- foliage, sky, timber, shadow -- "
              "and hung on the map in an arched frame. Davis Hall keeps its drawing: there is no "
              "exterior photograph of it yet. The frames drop in on their flagpoles.",
        opts=dict(icons="photo", photo_hrefs=PHOTO_ICONS),
        css="""
.go .park-map .b{animation:drop .9s cubic-bezier(.3,1.35,.5,1) backwards;
  animation-delay:calc(1.1s + var(--bd))}
@keyframes drop{0%{transform:translateY(-140px);opacity:0}30%{opacity:1}100%{transform:none}}
""",
        js="",
    ),

    dict(
        slug="15", name="Morning Mist", renderer="park",
        blurb="How the valley actually looks at seven in the morning: the map waits under a bank "
              "of mist that parts and lifts off the meadow, the buildings rise gently out of it, "
              "and the banners open last. Softer than the pop-up, and nothing bounces.",
        opts={},
        wrap=('<div class="misty">', '<div class="mist m1"></div><div class="mist m2"></div>'
              '<div class="mist m3"></div></div>'),
        css="""
.misty{position:relative;overflow:hidden}
.mist{position:absolute;pointer-events:none;z-index:5;opacity:0;inset:-10% -20%}
.m1{background:radial-gradient(ellipse 45% 40% at 30% 55%,var(--cream) 30%,rgba(255,240,218,0) 70%),
               radial-gradient(ellipse 40% 34% at 70% 40%,var(--cream) 25%,rgba(255,240,218,0) 70%)}
.m2{background:radial-gradient(ellipse 55% 30% at 50% 75%,#fff 20%,rgba(255,255,255,0) 70%)}
.m3{background:linear-gradient(var(--cream),var(--cream));}
.go .m1{animation:partL 3.4s cubic-bezier(.4,0,.3,1) .3s backwards}
.go .m2{animation:lift 3.2s cubic-bezier(.4,0,.3,1) .5s backwards}
.go .m3{animation:veil 1.6s ease .1s backwards}
@keyframes partL{from{opacity:1;transform:none}to{opacity:0;transform:translateX(-18%) scale(1.15)}}
@keyframes lift{from{opacity:1;transform:none}to{opacity:0;transform:translateY(-22%)}}
@keyframes veil{from{opacity:.94}to{opacity:0}}
.lab-stage{--o:.9s}
.go .park-map .t{animation:none}
.go .park-map .b{animation:emerge 1.4s cubic-bezier(.2,.8,.3,1) backwards;animation-delay:calc(1.4s + var(--bd) * 2)}
@keyframes emerge{from{transform:translateY(22px);opacity:0}}
.go .park-map .ban{animation-delay:calc(2.8s + var(--bd))}
.go .rd-edge,.go .rd-body,.go .rd-shine{animation:none}
""",
        js="",
    ),
]

for v in PARK:
    v["css"] = PARK_CSS + v["css"]
    v["js"] = PARK_JS + v["js"]
