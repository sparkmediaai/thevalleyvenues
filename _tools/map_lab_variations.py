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
        blurb="The plate tipped back the way a scale model sits on a table, lit from above "
              "and casting a shadow. Move the pointer to walk around it.",
        opts={},
        wrap=('<div class="tilt">', "</div>"),
        css="""
.lab-stage{background:linear-gradient(180deg,#EFE8D8,var(--cream));
  perspective:1800px;perspective-origin:50% 44%;overflow:hidden;
  padding:clamp(1rem,4vh,3rem) 0 clamp(1rem,4vh,3rem)}
/* Scaled so the tipped plate stays inside its stage; at full size the far
   corners leave the frame and the cottage in the woods is the first to go. */
.tilt{transform-style:preserve-3d;transition:transform .2s ease-out;will-change:transform}
.tilt svg{display:block;filter:drop-shadow(0 46px 52px rgba(52,55,47,.34))}
/* SVG children do not join the parent's 3D context, so the buildings cannot
   truly stand up. They are lifted with a shadow instead, which reads as raised
   from this angle and costs nothing. */
.map-place .map-art{filter:drop-shadow(0 3px 4px rgba(52,55,47,.45))}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.3}
.map-label{font-size:23px}
""",
        js="""
peekInit();
var stage=document.querySelector('.lab-stage'), tilt=document.querySelector('.tilt');
var BX=52, BZ=-24, S=0.80;
function set(rx,rz){
  tilt.style.transform='scale('+S+') rotateX('+rx+'deg) rotateZ('+rz+'deg)';
}
set(BX,BZ);
stage.addEventListener('pointermove',function(e){
  var r=stage.getBoundingClientRect();
  var px=(e.clientX-r.left)/r.width-0.5, py=(e.clientY-r.top)/r.height-0.5;
  set(BX-py*13, BZ+px*17);
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
// The hall and its deck are one building, so their anchors are 140 units apart
// and two 120px medallions on top of each other. Pushed apart by hand: this is
// the one place on the estate where the drawing is tighter than the photographs.
var NUDGE={hall:[-70,-52], deck:[86,44], valley:[0,26]};
svg.querySelectorAll('.map-place').forEach(function(a){
  var k=a.getAttribute('data-place'), info=window.LAB_PHOTOS[k];
  var halo=a.querySelector('.map-halo');
  var n=NUDGE[k]||[0,0];
  var cx=+halo.getAttribute('cx')+n[0], cy=+halo.getAttribute('cy')+n[1];
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

    dict(
        slug="06", name="Depth",
        blurb="A diorama rather than a drawing. Mountain, far woodland, near woodland and "
              "buildings each sit on their own plane and move at their own rate.",
        opts={},
        css="""
.lab-stage{background:linear-gradient(180deg,#E7E0CE 0%,var(--cream) 46%);overflow:hidden}
.lab-stage svg{transform:scale(1.06);transform-origin:50% 50%}
.map-mountains,.map-woods,.map-drives,.map-pope,.map-creek,.map-places,
.map-parking,.map-arrows,.map-wayfinding{transition:transform .45s cubic-bezier(.2,.7,.2,1)}
.map-place .map-art{filter:drop-shadow(0 4px 6px rgba(52,55,47,.3))}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.3}
""",
        js="""
peekInit();
var stage=document.querySelector('.lab-stage'), svg=stage.querySelector('svg');
// furthest away moves least, which is the whole trick
var planes=[
  ['.map-mountains', 6], ['.map-creek', 14], ['.map-pope', 16],
  ['.map-drives', 20], ['.map-woods', 30], ['.map-parking', 22],
  ['.map-wayfinding', 24], ['.map-arrows', 22], ['.map-places', 40]
];
var layers=planes.map(function(p){ return [svg.querySelector(p[0]), p[1]]; })
                 .filter(function(l){ return l[0]; });
function move(px,py){
  layers.forEach(function(l){
    l[0].style.transform='translate('+(-px*l[1])+'px,'+(-py*l[1]*.5)+'px)';
  });
}
stage.addEventListener('pointermove',function(e){
  var r=stage.getBoundingClientRect();
  move((e.clientX-r.left)/r.width-0.5, (e.clientY-r.top)/r.height-0.5);
});
stage.addEventListener('pointerleave',function(){ move(0,0); });
""",
    ),

    dict(
        slug="07", name="Four Seasons",
        blurb="One drawing, four times of year. The woodland and the ground change and "
              "nothing else does, which is the point: the estate sells a different day each season.",
        opts={},
        css="""
.lab-stage{background:var(--cream);transition:background .9s ease}
.lab-stage svg .map-ground{transition:fill .9s ease}
.map-woods > g{transition:fill .9s ease}
/* The fills are presentation attributes on the tone groups, which CSS wins
   against, so one drawing serves all four. */
.season-spring .map-woods > g{fill:#93A97C}
.season-spring .map-ground{fill:#F7F2E2}
.season-summer .map-woods > g{fill:#7E8F63}
.season-summer .map-ground{fill:#FFF0DA}
.season-autumn .map-woods > g{fill:#B08248}
.season-autumn .map-ground{fill:#F7E6C8}
.season-autumn .map-mountains path:first-child{fill:#B08248}
.season-winter .map-woods > g{fill:#9FAEA4}
.season-winter .map-ground{fill:#EDEDE6}
.season-winter .map-creek{stroke:#9BB6C2}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.28}
.seasons{display:flex;gap:.4rem;flex-wrap:wrap;padding:1rem clamp(1.1rem,4vw,3rem);
  background:var(--deep)}
.seasons button{font:600 .72rem/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;
  background:none;border:1px solid var(--cream);color:var(--cream);padding:.6rem 1.1rem;cursor:pointer;
  transition:background .25s,color .25s}
.seasons button:hover{background:rgba(255,240,218,.16)}
.seasons button[aria-pressed="true"]{background:var(--cream);color:var(--deep)}
""",
        js="""
peekInit();
var stage=document.querySelector('.lab-stage');
var btns=[].slice.call(document.querySelectorAll('.seasons button'));
function pick(s){
  stage.className='lab-stage stage-07 season-'+s;
  btns.forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.s===s)); });
}
btns.forEach(function(b){ b.addEventListener('click',function(){ pick(b.dataset.s); }); });
pick('summer');
""",
    ),

    dict(
        slug="08", name="The Fold",
        blurb="A paper map, folded in three and opening as you arrive. The creases stay, "
              "because a map that has been in somebody's pocket is a map that was used.",
        opts={},
        css="""
.lab-stage{background:#E9E2D0;perspective:2200px;overflow:hidden;
  padding:clamp(1rem,4vh,3rem) 0}
.fold{display:flex;width:100%;transform-style:preserve-3d}
.panel{width:33.3333%;overflow:hidden;position:relative;
  transform-origin:left center;backface-visibility:hidden;
  animation:open 1.5s cubic-bezier(.2,.75,.25,1) both}
.panel:nth-child(1){transform-origin:right center;animation-delay:.15s}
.panel:nth-child(2){animation:none;transform:none}
.panel:nth-child(3){animation-delay:.3s}
@keyframes open{from{transform:rotateY(-72deg)}to{transform:rotateY(0)}}
.panel:nth-child(3){animation-name:open3}
@keyframes open3{from{transform:rotateY(72deg)}to{transform:rotateY(0)}}
.panel svg{width:300%;display:block}
.panel:nth-child(2) svg{margin-left:-100%}
.panel:nth-child(3) svg{margin-left:-200%}
/* the creases, and the shading either side of them */
.panel:nth-child(1)::after,.panel:nth-child(3)::after{
  content:"";position:absolute;inset:0;pointer-events:none}
.panel:nth-child(1)::after{background:linear-gradient(90deg,rgba(52,55,47,0) 82%,rgba(52,55,47,.13))}
.panel:nth-child(3)::after{background:linear-gradient(270deg,rgba(52,55,47,0) 82%,rgba(52,55,47,.13))}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.28}
.again{position:absolute;right:clamp(1rem,4vw,3rem);top:1rem;z-index:30;
  font:600 .7rem/1 var(--sans);letter-spacing:.13em;text-transform:uppercase;
  background:var(--deep);color:var(--cream);border:0;padding:.6rem 1rem;cursor:pointer}
""",
        js="""
peekInit();
var again=document.querySelector('.again');
again.addEventListener('click',function(){
  document.querySelectorAll('.panel').forEach(function(p){
    p.style.animation='none'; void p.offsetWidth; p.style.animation='';
  });
});
""",
    ),

    dict(
        slug="09", name="The Tour",
        blurb="It shows itself. The frame travels the estate on its own, resting on each "
              "place long enough to look at it, and stops the moment you take hold of it.",
        opts={},
        css="""
.lab-stage{background:var(--cream);position:relative}
.map-place:hover .map-halo,.map-place:focus-visible .map-halo{opacity:.3}
.map-place.lit .map-halo{opacity:.34}
.card{position:absolute;left:clamp(1rem,4vw,3rem);bottom:clamp(1rem,4vw,3rem);z-index:30;
  width:clamp(230px,26vw,340px);background:var(--cream);padding:.55rem .55rem .2rem;
  box-shadow:0 20px 44px rgba(52,55,47,.3);opacity:0;transform:translateY(12px);
  transition:opacity .5s ease,transform .5s cubic-bezier(.16,.8,.24,1)}
.card.on{opacity:1;transform:none}
.card img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}
.card b{display:block;font-family:var(--display);font-weight:400;font-size:1.3rem;
  line-height:1.15;padding:.55rem .25rem .1rem}
.card span{display:block;font-size:.8rem;opacity:.75;padding:0 .25rem .6rem}
.hold{position:absolute;right:clamp(1rem,4vw,3rem);top:1rem;z-index:30;
  font:600 .7rem/1 var(--sans);letter-spacing:.13em;text-transform:uppercase;
  background:var(--deep);color:var(--cream);border:0;padding:.6rem 1rem;cursor:pointer}
""",
        js="""
peekInit();
var svg=document.querySelector('.lab-stage svg');
var card=document.querySelector('.card'), hold=document.querySelector('.hold');
var img=card.querySelector('img'), ttl=card.querySelector('b'), sub=card.querySelector('span');
var full=[0,0,2000,800], order=['magnolia','valley','deck','hall','village','woods'];
var places={};
svg.querySelectorAll('.map-place').forEach(function(a){
  var h=a.querySelector('.map-halo');
  places[a.getAttribute('data-place')]={el:a,x:+h.getAttribute('cx'),y:+h.getAttribute('cy')};
});
var cur=full.slice(), want=full.slice(), i=-1, running=true, wait=0;
function frame(){
  for(var k=0;k<4;k++) cur[k]+=(want[k]-cur[k])*0.075;
  svg.setAttribute('viewBox',cur.map(function(v){return v.toFixed(1);}).join(' '));
  requestAnimationFrame(frame);
}
frame();
function go(){
  if(!running) return;
  i=(i+1)%(order.length+1);
  if(i===order.length){ want=full.slice(); card.classList.remove('on');
    Object.keys(places).forEach(function(k){places[k].el.classList.remove('lit');});
    wait=setTimeout(go,2600); return; }
  var k=order[i], p=places[k], info=window.LAB_PHOTOS[k], w=620, h=248;
  want=[p.x-w/2, p.y-h/2, w, h];
  Object.keys(places).forEach(function(n){ places[n].el.classList.toggle('lit', n===k); });
  img.src='/assets/img/'+info.photos[0]+'.webp'; img.alt=info.title;
  ttl.textContent=info.title; sub.textContent=info.blurb;
  card.classList.add('on');
  wait=setTimeout(go,3400);
}
go();
hold.addEventListener('click',function(){
  running=!running; hold.textContent=running?'Stop the tour':'Start the tour';
  if(running){ go(); } else { clearTimeout(wait); want=full.slice(); card.classList.remove('on');
    Object.keys(places).forEach(function(k){places[k].el.classList.remove('lit');}); }
});
""",
    ),

    dict(
        slug="10", name="Endpaper",
        blurb="The inside cover of the book. No roads and no woodland -- six framed "
              "photographs on bare ground, joined by the path a weekend takes between them.",
        opts=dict(labels=False, route=True),
        css="""
.lab-stage{background:var(--cream);position:relative;
  background-image:radial-gradient(circle at 50% 40%,rgba(154,159,131,.10),transparent 62%)}
.map-woods,.map-drives,.map-pope,.map-parking,.map-arrows,.map-wayfinding,
.map-mountains,.map-creek{display:none}
.map-place .map-art{opacity:0}
.map-route{stroke:var(--clay);stroke-width:2.5;stroke-dasharray:1 10;stroke-linecap:round;
  opacity:.9;stroke-dashoffset:0;animation:trail 26s linear infinite}
@keyframes trail{to{stroke-dashoffset:-220}}
.map-stop{fill:var(--clay);stroke:var(--cream);stroke-width:3}
.plate10{position:absolute;transform:translate(-50%,-50%) rotate(var(--r));z-index:10;
  width:clamp(120px,13vw,196px);text-decoration:none;color:var(--deep);
  transition:transform .45s cubic-bezier(.16,.8,.24,1)}
.plate10 figure{margin:0;background:#fff;padding:.42rem .42rem .1rem;
  box-shadow:0 10px 26px rgba(52,55,47,.22)}
.plate10 img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}
.plate10 figcaption{font:600 .6rem/1.3 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  padding:.45rem .1rem .5rem;text-align:center}
.plate10:hover,.plate10:focus-visible{transform:translate(-50%,-50%) rotate(0deg) scale(1.1);z-index:20}
""",
        js="""
var stage=document.querySelector('.lab-stage'), svg=stage.querySelector('svg');
var vb=svg.viewBox.baseVal;
var NUDGE={hall:[-90,-70],deck:[100,56],valley:[0,40],magnolia:[0,-30]};
var TILT={magnolia:'-2.2deg',valley:'1.8deg',hall:'-1.4deg',deck:'2.4deg',
          village:'-1.8deg',woods:'2deg'};
svg.querySelectorAll('.map-place').forEach(function(a){
  var k=a.getAttribute('data-place'), info=window.LAB_PHOTOS[k];
  var h=a.querySelector('.map-halo'), n=NUDGE[k]||[0,0];
  var cx=+h.getAttribute('cx')+n[0], cy=+h.getAttribute('cy')+n[1];
  var el=document.createElement('a');
  el.className='plate10'; el.href=a.getAttribute('href');
  el.style.setProperty('--r', TILT[k]||'0deg');
  el.style.left=((cx-vb.x)/vb.width*100)+'%';
  el.style.top=((cy-vb.y)/vb.height*100)+'%';
  el.innerHTML='<figure><img alt="" src="/assets/img/'+info.photos[0]+
    '.webp"><figcaption>'+info.title+'</figcaption></figure>';
  var n2=0,t=null,img=el.querySelector('img');
  el.addEventListener('mouseenter',function(){
    t=setInterval(function(){n2=(n2+1)%info.photos.length;
      img.src='/assets/img/'+info.photos[n2]+'.webp';},1200);
  });
  el.addEventListener('mouseleave',function(){clearInterval(t);});
  stage.appendChild(el);
});
""",
    ),
]
