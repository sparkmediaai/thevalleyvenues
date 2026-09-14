"""Variation 11: the park map, drawn by _tools/park_map.py.

11 was the pick of the last round and stays exactly as it was. Its stylesheet is
split in two so the fairy-tale round (map_lab_fairy.py) can borrow the parts it
wants: BASE is the stage, the hover and the ambient life; POP is 11's arrival.

Every intro runs only when the stage carries .go, so the resting state is always
the finished map.
"""

BASE_CSS = """
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

.again{position:absolute;right:clamp(.8rem,2vw,1.6rem);bottom:clamp(.8rem,2vw,1.6rem);z-index:60;
  font:600 .7rem/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--deep);
  background:var(--cream);border:1px solid var(--deep);padding:.6rem .8rem;border-radius:999px;cursor:pointer}
.again:hover{background:#fff}
@media (max-width:760px){.lab-stage{overflow-x:auto}.park-map{min-width:860px}}
"""

# 11's arrival. --o offsets the whole sequence so another intro can go first.
POP_CSS = """
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
"""

PARK_CSS = BASE_CSS + POP_CSS

PARK_JS = """
peekInit();
var st=document.querySelector('.lab-stage');
function play(){st.classList.remove('go');void st.offsetWidth;st.classList.add('go');}
if(!matchMedia('(prefers-reduced-motion:reduce)').matches) play();
document.querySelector('.again').addEventListener('click',play);
"""

PARK = [
    dict(
        slug="11", name="The Park Map", renderer="park",
        blurb="The estate drawn the way a park map draws a kingdom, in the client's seven colours: "
              "puffy trees, ribbon banners, a gate on Pope Creek Road. The drives draw themselves in, "
              "the woods pop up west to east, and each building bounces into place.",
        opts={},
        css=PARK_CSS,
        js=PARK_JS,
    ),
]
