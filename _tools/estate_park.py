"""
The estate map on /the-estate/: the Pixie Dust park map from the map lab.

    python _tools/estate_park.py      # then _build/build.py

Writes three assets from the lab's own sources, so the page and the lab can
never drift apart:

  assets/park-map.svg     the drawing, with the storybook layer on
  assets/estate-park.css  the storybook motion, hover and sparkle styles
  assets/estate-park.js   the wand intro, sparkles on hover, photo peek

The intro plays once, when the map is first scrolled into view (a map that
finished animating above the fold before anyone reached it would be wasted).
It plays whatever the visitor's motion setting, as the hero film does, at the
owner's request.
"""
import os

import park_map
from map_lab import LAB_CSS, PEEK_JS, photos_json
from map_lab_fairy import FAIRY_CSS, HELPERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

EXTRA_CSS = """
/* ---- the estate page's framing of the lab map ---- */
.park-stage{position:relative;background:var(--cream);border-radius:var(--round-lg,28px);
  padding:clamp(.4rem,1.2vw,.9rem);box-shadow:0 30px 70px rgba(52,55,47,.14)}
.park-stage .park-map{border-radius:18px}
.park-map .wand{pointer-events:none}
.park-map .wand circle{animation:glow .5s ease-in-out infinite alternate}
@keyframes glow{to{opacity:.35}}
.park-again{position:absolute;right:clamp(.9rem,2vw,1.6rem);bottom:clamp(.9rem,2vw,1.6rem);z-index:5;
  font:600 .66rem/1 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--deep);
  background:var(--paper);border:1px solid var(--sage);padding:.55rem .8rem;border-radius:999px;cursor:pointer}
.park-again:hover{background:var(--sage)}
.park-again[hidden]{display:none}
@media (max-width:900px){
  .park-scroll{overflow-x:auto;border-radius:18px;-webkit-overflow-scrolling:touch}
  .park-scroll .park-map{min-width:860px}
  .park-again{bottom:auto;top:clamp(.9rem,2vw,1.6rem)}
}
"""

SITE_JS = """
(function(){
var st=document.querySelector('.park-stage');
if(!st)return;
%(helpers)s
%(peek)s
// reach for a place and it throws a little sparkle
var lastHover={};
map.querySelectorAll('.map-place').forEach(function(a){
  a.addEventListener('mouseenter',function(){var k=a.getAttribute('data-place'),now=Date.now();
    if(now-(lastHover[k]||0)<700)return;lastHover[k]=now;var p=where(k);burst(p.x,p.y-60,10,80);});
});

var TRAIL='M 60 820 C 120 560 380 420 620 360 C 880 300 900 640 1180 610 C 1460 580 1380 200 1680 170 C 1880 150 1980 300 2120 250';
var world=document.createElementNS(NS,'g');world.setAttribute('class','world');
Array.prototype.slice.call(map.childNodes).forEach(function(n){if(n.nodeName!=='defs')world.appendChild(n);});
map.appendChild(world);
var defs=map.querySelector('defs'),mask=null,again=st.querySelector('.park-again');

// Hidden under the mask until the wand reaches it. If the intro cannot run
// for any reason the mask is never added, so the map simply shows.
function cover(){
  mask=mk('mask',{id:'dust',maskUnits:'userSpaceOnUse',x:-300,y:-300,width:2600,height:1400},defs);
  mk('rect',{x:-300,y:-300,width:2600,height:1400,fill:'#fff','fill-opacity':0,'class':'dust-base'},mask);
  mk('path',{d:TRAIL,fill:'none',stroke:'#fff','stroke-width':520,'stroke-linecap':'round',pathLength:1,
    'stroke-dasharray':'1 1','stroke-dashoffset':1,'class':'dust-trail'},mask);
  world.setAttribute('mask','url(#dust)');
}
function uncover(){world.removeAttribute('mask');if(mask){mask.remove();mask=null;}}

var raf=0;
function play(){
  clearAll();cancelAnimationFrame(raf);uncover();cover();
  if(again)again.hidden=true;
  var base=mask.querySelector('.dust-base'),p=mask.querySelector('.dust-trail');
  var guide=mk('path',{d:TRAIL,fill:'none'},defs);
  var head=mk('g',{'class':'wand'});
  mk('circle',{r:30,fill:'#FFF0DA',opacity:.8},head);
  mk('path',{d:STAR,fill:'#fff',stroke:'#34372F','stroke-width':1.2,transform:'scale(2.2)'},head);
  var L=guide.getTotalLength(),t0=null,D=3200,done={};
  var spots=KEYS.map(function(k){var q=where(k);return {k:k,x:q.x,y:q.y};});
  function finish(){
    base.style.transition='fill-opacity .7s ease';base.style.fillOpacity=1;
    spots.forEach(function(s){if(!done[s.k]){done[s.k]=1;hit(s.k);}});
    later(function(){uncover();guide.remove();if(again)again.hidden=false;},800);
  }
  function step(now){
    if(t0===null)t0=now;
    var k=Math.min(1,(now-t0)/D),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    p.setAttribute('stroke-dashoffset',(1-e).toFixed(4));
    var pt=guide.getPointAtLength(e*L);
    head.setAttribute('transform','translate('+pt.x.toFixed(1)+' '+pt.y.toFixed(1)+')');
    for(var i=0;i<3;i++)spark(pt.x+(Math.random()-.5)*50,pt.y+(Math.random()-.5)*50,{dy:30+Math.random()*80,life:1300});
    spots.forEach(function(s){if(!done[s.k]&&Math.hypot(pt.x-s.x,pt.y-s.y)<300){done[s.k]=1;hit(s.k,18);}});
    if(k<1)raf=requestAnimationFrame(step);else{head.remove();finish();}
  }
  raf=requestAnimationFrame(step);
}
if(again)again.addEventListener('click',play);

if('IntersectionObserver' in window){
  var r=st.getBoundingClientRect();
  // Only hide it in advance if it is not already on screen.
  if(r.top>innerHeight*.9)cover();
  var io=new IntersectionObserver(function(es){
    if(es[0].intersectionRatio>=.35){io.disconnect();play();}
  },{threshold:[0,.35,.6]});
  io.observe(st);
}else if(again){again.hidden=false;}
})();
"""


def main():
    svg, meta = park_map.build(fairy=True)
    with open(os.path.join(ASSETS, "park-map.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # the photograph a hover reveals, lifted out of the lab's shared sheet
    peek_css = LAB_CSS[LAB_CSS.index("/* The photograph that a hover reveals."):LAB_CSS.index("@media (prefers-reduced-motion")]
    peek_css = peek_css.replace("border-radius:2px", "border-radius:16px").replace(
        ".peek img{", ".peek img{border-radius:12px;")
    css = FAIRY_CSS.replace(".lab-stage", ".park-stage") + peek_css + EXTRA_CSS
    # the lab chrome that FAIRY_CSS carries along is not wanted on the site
    css = css.replace(".again{", ".lab-again-unused{").replace(".again:hover", ".lab-again-unused:hover")
    with open(os.path.join(ASSETS, "estate-park.css"), "w", encoding="utf-8") as f:
        f.write("/* Generated by _tools/estate_park.py from the map lab. Edit there. */\n" + css)

    helpers = HELPERS.replace("document.querySelector('.lab-stage')", "st").replace("var st=st;", "")
    peek = photos_json() + PEEK_JS.replace(".lab-stage", ".park-stage") + "\npeekInit();"
    js = SITE_JS % dict(helpers=helpers, peek=peek)
    with open(os.path.join(ASSETS, "estate-park.js"), "w", encoding="utf-8") as f:
        f.write("/* Generated by _tools/estate_park.py from the map lab. Edit there. */\n" + js)
    print("park map: %d trees, %.0f KB" % (meta["trees"], len(svg) / 1024.0))


if __name__ == "__main__":
    main()
