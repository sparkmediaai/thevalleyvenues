"""The ten treatments. Each is name, blurb, svg options, css and js.

Kept apart from the harness in map_lab.py so that adding an eleventh is a dict
in this list and nothing else.
"""

VARIATIONS = [

    dict(
        slug="01", name="Storybook Plate",
        blurb="The drawing as a printed plate: paper ground, a ruled border, a breeze "
              "through the woodland, and a building that lifts when you reach for it.",
        opts={},
        wrap=('<div class="plate">', "</div>"),
        css="""
.lab-stage{background:var(--cream);padding:clamp(.5rem,2vw,1.4rem)}
.plate{position:relative;border:1px solid var(--olive);padding:clamp(.4rem,1.4vw,1rem);
  background:var(--cream);box-shadow:inset 0 0 120px rgba(52,55,47,.10)}
.plate::after{content:"";position:absolute;inset:0;pointer-events:none;
  box-shadow:inset 0 0 70px rgba(52,55,47,.13)}
.map-place .map-art{transition:transform .45s cubic-bezier(.16,.8,.24,1);
  transform-box:fill-box;transform-origin:50% 90%}
.map-place:hover .map-art,.map-place:focus-visible .map-art{transform:translateY(-7px) scale(1.05)}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.28}
.map-place:hover .map-label{text-decoration:underline;text-underline-offset:3px}
/* A breeze, applied to the ten tone groups rather than to a thousand trees. */
.map-woods > g{transform-box:view-box;animation:breeze 13s ease-in-out infinite alternate}
.map-woods > g:nth-child(2n){animation-duration:17s;animation-delay:-4s}
.map-woods > g:nth-child(3n){animation-duration:21s;animation-delay:-9s}
@keyframes breeze{from{transform:skewX(-.35deg)}to{transform:skewX(.35deg)}}
""",
        js="peekInit();",
    ),

    dict(
        slug="02", name="Golden Hour",
        blurb="The same ground in daylight and again after dark, cross-faded on a slow "
              "clock. Drag the hour if you would rather choose it yourself.",
        opts={},
        dusk=dict(ground="#2B2E26", wood="#3E4436", wood2="#495040", road="#6E5A44"),
        css="""
.lab-stage{background:#2B2E26}
.hours{position:relative}
.hours .layer{position:absolute;inset:0}
.hours .layer.day{position:relative}
.hours .dusk{opacity:0}
.hours .dusk .map-label{fill:var(--cream);stroke:#2B2E26}
.hours .dusk .map-sign{fill:var(--cream);stroke:#2B2E26}
.sun{position:absolute;width:44px;height:44px;border-radius:50%;pointer-events:none;z-index:20;
  background:radial-gradient(circle,#FFF6DD,#E9BC70 58%,rgba(233,188,112,0) 72%)}
.dial{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;
  padding:1rem clamp(1.1rem,4vw,3rem);background:var(--deep);color:var(--cream)}
.dial input{flex:1;min-width:12rem;accent-color:var(--clay)}
.dial label{font:600 .72rem/1 var(--sans);letter-spacing:.14em;text-transform:uppercase}
.dial output{font-family:var(--display);font-size:1.35rem;min-width:6rem;text-align:right}
""",
        js="""
peekInit();
var hours=document.querySelector('.hours'), dusk=hours.querySelector('.dusk');
var sun=document.createElement('div'); sun.className='sun'; hours.appendChild(sun);
var range=document.getElementById('t'), out=document.getElementById('tv'), auto=true, t=+range.value;
function render(v){
  dusk.style.opacity=Math.max(0,Math.min(1,(v-52)/44));
  var a=Math.PI*(v/100);
  sun.style.left=(4+90*(v/100))+'%';
  sun.style.top=(74-60*Math.sin(a))+'%';
  sun.style.opacity=v>94?0:1;
  var mins=Math.round(8*60+v*(13*60)/100), h=Math.floor(mins/60), m=mins%60;
  out.textContent=((h>12?h-12:h))+':'+(m<10?'0':'')+m+(h>=12?' pm':' am');
}
range.addEventListener('input',function(){auto=false;t=+range.value;render(t);});
render(t);
setInterval(function(){ if(!auto) return; t=(t+0.2)%100; range.value=t; render(t); },90);
""",
    ),

    dict(
        slug="03", name="The Weekend",
        blurb="A marker walks the estate in the order a wedding meets it, pausing where "
              "the weekend pauses. Scrub it, or let it run.",
        opts=dict(route=True),
        css="""
.lab-stage{background:var(--cream)}
.map-route{stroke:var(--clay);stroke-width:3;stroke-dasharray:2 9;stroke-linecap:round;opacity:.85}
.map-stop{fill:var(--cream);stroke:var(--deep);stroke-width:2.4;transition:fill .3s,r .3s}
.map-stop.on{fill:var(--clay)}
.walker{fill:var(--deep);stroke:var(--cream);stroke-width:3}
.rail{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;
  padding:1rem clamp(1.1rem,4vw,3rem);background:var(--deep);color:var(--cream)}
.rail button{font:600 .72rem/1 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  background:none;border:1px solid var(--cream);color:var(--cream);padding:.55rem .95rem;cursor:pointer}
.rail button:hover{background:var(--cream);color:var(--deep)}
.rail input{flex:1;min-width:12rem;accent-color:var(--clay)}
.rail .now{font-family:var(--display);font-size:1.4rem;min-width:13rem}
""",
        js="""
peekInit();
var svg=document.querySelector('.lab-stage svg');
var route=svg.querySelector('.map-route');
var stops=[].slice.call(svg.querySelectorAll('.map-stop'));
var len=route.getTotalLength();
var walker=document.createElementNS('http://www.w3.org/2000/svg','circle');
walker.setAttribute('r','11'); walker.setAttribute('class','walker');
route.parentNode.appendChild(walker);
var now=document.getElementById('now'), bar=document.getElementById('bar');
var play=document.getElementById('play'), running=true, u=0;
var at=stops.map(function(s){
  var best=0,bd=1e9,cx=+s.getAttribute('cx'),cy=+s.getAttribute('cy');
  for(var i=0;i<=len;i+=6){var p=route.getPointAtLength(i);
    var d=(p.x-cx)*(p.x-cx)+(p.y-cy)*(p.y-cy); if(d<bd){bd=d;best=i;}}
  return best/len;
});
function render(v){
  var p=route.getPointAtLength(v*len);
  walker.setAttribute('cx',p.x); walker.setAttribute('cy',p.y);
  var near=-1;
  at.forEach(function(a,i){ if(Math.abs(a-v)<0.05) near=i; });
  stops.forEach(function(s,i){ s.classList.toggle('on', i===near); });
  now.textContent = near>=0 ? window.LAB_PHOTOS[stops[near].getAttribute('data-place')].title : '\\u2014';
  bar.value=v*100;
}
bar.addEventListener('input',function(){running=false;play.textContent='Play';u=bar.value/100;render(u);});
play.addEventListener('click',function(){running=!running;play.textContent=running?'Pause':'Play';});
render(0);
setInterval(function(){ if(!running) return; u=(u+0.0022)%1; render(u); },40);
""",
    ),

    dict(
        slug="04", name="The Model",
        blurb="The plate tipped back into three dimensions, the way a scale model sits on "
              "a table, with the buildings standing up off it. Move the pointer to walk around it.",
        opts={},
        wrap=('<div class="tilt">', "</div>"),
        css="""
.lab-stage{background:linear-gradient(180deg,#EFE8D8,var(--cream));
  perspective:1700px;perspective-origin:50% 42%;
  padding:clamp(1rem,5vh,4rem) 0 clamp(2rem,9vh,7rem)}
.tilt{transform-style:preserve-3d;transition:transform .2s ease-out;will-change:transform}
.tilt svg{display:block;filter:drop-shadow(0 42px 48px rgba(52,55,47,.32))}
.map-place .map-art{transform-box:fill-box;transform-origin:50% 100%;
  transition:transform .4s cubic-bezier(.16,.8,.24,1)}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.3}
.map-label{font-size:23px}
""",
        js="""
peekInit();
var stage=document.querySelector('.lab-stage'), tilt=document.querySelector('.tilt');
var BX=54, BZ=-25;
function set(rx,rz){ tilt.style.transform='rotateX('+rx+'deg) rotateZ('+rz+'deg)'; }
set(BX,BZ);
// stand every building back up against the tipped plane
document.querySelectorAll('.map-place .map-art').forEach(function(g){
  g.style.transform='rotateX(-'+BX+'deg)';
});
stage.addEventListener('pointermove',function(e){
  var r=stage.getBoundingClientRect();
  var px=(e.clientX-r.left)/r.width-0.5, py=(e.clientY-r.top)/r.height-0.5;
  set(BX-py*14, BZ+px*18);
});
stage.addEventListener('pointerleave',function(){ set(BX,BZ); });
""",
    ),

    dict(
        slug="05", name="Medallions",
        blurb="No illustration at all. The drives stay, the woodland goes, and each place "
              "is the photograph of itself. The quietest of the ten, and the most editorial.",
        opts=dict(labels=False),
        css="""
.lab-stage{background:var(--ivory);position:relative}
.map-woods,.map-mountains,.map-parking,.map-arrows,.map-wayfinding{display:none}
.map-drives path{opacity:.45}
.map-pope path{opacity:.3}
.map-creek{opacity:.3}
.map-place .map-art{opacity:0}
.med{position:absolute;transform:translate(-50%,-50%);z-index:10;text-align:center;
  text-decoration:none;color:var(--deep)}
.med i{display:block;width:clamp(74px,8vw,120px);height:clamp(74px,8vw,120px);border-radius:50%;
  overflow:hidden;border:3px solid var(--cream);box-shadow:0 10px 26px rgba(52,55,47,.24);
  transition:transform .45s cubic-bezier(.16,.8,.24,1),box-shadow .45s}
.med img{width:100%;height:100%;object-fit:cover;display:block}
.med b{display:block;margin-top:.6rem;font:600 .68rem/1.25 var(--sans);letter-spacing:.13em;
  text-transform:uppercase;text-shadow:0 1px 0 var(--ivory),0 0 7px var(--ivory)}
.med:hover i,.med:focus-visible i{transform:scale(1.15);box-shadow:0 18px 36px rgba(52,55,47,.32)}
.med:hover b{text-decoration:underline;text-underline-offset:3px}
""",
        js="""
var stage=document.querySelector('.lab-stage'), svg=stage.querySelector('svg');
var vb=svg.viewBox.baseVal;
svg.querySelectorAll('.map-place').forEach(function(a){
  var k=a.getAttribute('data-place'), info=window.LAB_PHOTOS[k];
  var halo=a.querySelector('.map-halo');
  var cx=+halo.getAttribute('cx'), cy=+halo.getAttribute('cy');
  var m=document.createElement('a');
  m.className='med'; m.href=a.getAttribute('href');
  m.style.left=((cx-vb.x)/vb.width*100)+'%';
  m.style.top=((cy-vb.y)/vb.height*100)+'%';
  m.innerHTML='<i><img alt="" src="/assets/img/'+info.photos[0]+'.webp"></i><b>'+info.title+'</b>';
  var n=0,t=null,img=m.querySelector('img');
  m.addEventListener('mouseenter',function(){
    t=setInterval(function(){n=(n+1)%info.photos.length;
      img.src='/assets/img/'+info.photos[n]+'.webp';},1300);
  });
  m.addEventListener('mouseleave',function(){clearInterval(t);});
  stage.appendChild(m);
});
""",
    ),
]
