/* The wedding lab's motion. Written to /wedding-lab/motion.js by wedding_lab.py.

   One engine, ten choreographies. Every direction gets the same foundation --
   smooth scrolling on a desktop, a reading-progress thread, a header that steps
   aside while you read, magnetic buttons, and a slow zoom on every photograph you
   touch (the pointer itself is left alone) -- and then its own opening and
   its own way of revealing the page (see RECIPES, keyed by body[data-dir]).

   Two rules hold everywhere:
   - Words are never hidden waiting for a scroll. Text that arrives as you scroll
     rises and inks in from the olive, but it is readable the whole time. Only
     the opening, which plays at once, is allowed to mask type completely.
   - Photographs open from a partly visible frame, never from nothing.

   GSAP + ScrollTrigger (and Lenis for smooth scrolling) load from a CDN; if they
   do not, the pages are simply static and complete. */
(function () {
  "use strict";
  var INK = "#2B1B00", OLIVE = "#7B7951";
  var docEl = document.documentElement;
  var dir = document.body.getAttribute("data-dir");
  var fine = matchMedia("(hover:hover) and (pointer:fine)").matches;
  var wide = matchMedia("(min-width: 900px)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  if (!window.gsap || !window.ScrollTrigger) { docEl.classList.add("no-motion"); return; }
  var g = window.gsap, ST = window.ScrollTrigger;
  g.registerPlugin(ST);
  docEl.classList.add("motion");

  /* ------------------------------------------------------ smooth scrolling */
  var lenis = null;
  if (fine && window.Lenis) {
    lenis = new window.Lenis({ lerp: 0.085, wheelMultiplier: 0.9 });
    window.__lenis = lenis;
    lenis.on("scroll", ST.update);
    g.ticker.add(function (t) { lenis.raf(t * 1000); });
    g.ticker.lagSmoothing(0);
  }

  /* -------------------------------------------------------------- splitting */
  function split(el, mode) {
    if (!el) return [];
    if (el._split && el._split.mode === mode) return el._split.parts;
    var parts = [];
    var label = el.textContent.replace(/\s+/g, " ").trim();
    function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (t) {
            if (!t) return;
            if (/^\s+$/.test(t)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span"); w.className = "sw";
            var i = document.createElement("span"); i.className = "swi";
            if (mode === "chars") {
              Array.prototype.forEach.call(t, function (ch) {
                var c = document.createElement("span"); c.className = "sc"; c.textContent = ch;
                i.appendChild(c); parts.push(c);
              });
            } else { i.textContent = t; parts.push(i); }
            w.appendChild(i); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== "BR" && !n.classList.contains("sw")) walk(n);
      });
    }
    walk(el);
    if (mode === "chars") {
      el.setAttribute("aria-label", label);
      $$(".sw", el).forEach(function (s) { s.setAttribute("aria-hidden", "true"); });
    }
    el._split = { mode: mode, parts: parts };
    return parts;
  }
  function done(el) { if (el) el.setAttribute("data-m", "1"); return el; }
  function isDone(el) { return el.hasAttribute("data-m"); }
  function inkColoured(el) { return getComputedStyle(el).color === "rgb(43, 27, 0)"; }

  /* ---------------------------------------------------------------- effects */
  var E = {
    // Opening only: type rises out of a mask. Plays immediately, not on scroll.
    maskIn: function (el, o) {
      o = o || {}; if (!el) return g.timeline();
      done(el); el.classList.add("mask");
      var parts = split(el, o.chars ? "chars" : "words");
      return g.from(parts, { yPercent: 115, rotate: o.rotate || 0, duration: o.dur || 1.25,
        ease: "expo.out", stagger: o.stagger || (o.chars ? 0.022 : 0.06), delay: o.delay || 0 });
    },
    // On scroll: rises and inks in, readable throughout.
    softIn: function (el, o) {
      o = o || {}; if (!el || isDone(el)) return; done(el);
      var parts = split(el, o.chars ? "chars" : "words");
      var from = { y: o.chars ? "0.45em" : "0.6em", rotate: o.rotate || 0 };
      if (inkColoured(el)) from.color = OLIVE;
      g.from(parts, Object.assign(from, { duration: o.dur || 1.1, ease: "power3.out",
        stagger: o.stagger || (o.chars ? 0.014 : 0.028),
        scrollTrigger: { trigger: el, start: "top 90%", once: true } }));
    },
    // Scrubbed: each word inks from olive to brown as it is read.
    inkRead: function (el) {
      if (!el || isDone(el)) return; done(el);
      var parts = split(el, "words");
      if (!inkColoured(el)) { E.softIn(el); return; }
      g.fromTo(parts, { color: OLIVE }, { color: INK, ease: "none", stagger: 0.1,
        scrollTrigger: { trigger: el, start: "top 82%", end: "bottom 45%", scrub: true } });
    },
    // A block (paragraph, button, card) lifts into place.
    lift: function (els, o) {
      o = o || {}; els = [].concat(els).filter(function (e) { return e && !isDone(e); });
      if (!els.length) return; els.forEach(done);
      g.from(els, { y: o.y || 34, duration: o.dur || 1.2, ease: "power3.out", stagger: o.stagger || 0.1,
        delay: o.delay || 0, scrollTrigger: o.now ? null : { trigger: o.trigger || els[0], start: "top 92%", once: true } });
    },
    // Photographs open from a partly visible frame.
    reveal: function (img, o) {
      o = o || {}; if (!img || img._rev) return; img._rev = true; done(img);
      var vars = { clipPath: "inset(0% 0% 0% 0%)", scale: o.scaleTo || 1, duration: o.dur || 1.8,
        ease: "expo.out", delay: o.delay || 0 };
      if (!o.now) vars.scrollTrigger = { trigger: img.parentElement, start: o.start || "top 88%", once: true };
      g.fromTo(img, { clipPath: o.from || "inset(10% 8% 10% 8%)", scale: o.scale || 1.22 }, vars);
    },
    // The photograph drifts inside its frame as the page moves.
    drift: function (img, amt) {
      if (!img) return;
      g.fromTo(img, { yPercent: -(amt || 6) }, { yPercent: amt || 6, ease: "none",
        scrollTrigger: { trigger: img.parentElement, start: "top bottom", end: "bottom top", scrub: true } });
    },
    // A rule draws itself.
    line: function (el, o) {
      o = o || {}; if (!el) return;
      g.from(el, { scaleX: 0, transformOrigin: o.origin || "left center", duration: o.dur || 1.4, ease: "expo.inOut",
        delay: o.delay || 0, scrollTrigger: o.now ? null : { trigger: el, start: "top 92%", once: true } });
    },
    // Letters settle from wide tracking.
    track: function (el, o) {
      o = o || {}; if (!el) return;
      g.from(el, { letterSpacing: o.from || "0.6em", duration: o.dur || 2, ease: "expo.out", delay: o.delay || 0,
        scrollTrigger: o.now ? null : { trigger: el, start: "top 92%", once: true } });
    },
    // Letters shuffle and settle (short, and the text is complete after it).
    scramble: function (el) {
      if (!el || isDone(el)) return; done(el);
      var text = el.textContent, abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      ST.create({ trigger: el, start: "top 92%", once: true, onEnter: function () {
        var f = 0, n = 18;
        (function tick() {
          el.textContent = text.split("").map(function (ch, i) {
            if (ch === " " || i < (f / n) * text.length) return ch;
            return abc[(Math.random() * abc.length) | 0];
          }).join("");
          if (++f <= n) requestAnimationFrame(tick); else el.textContent = text;
        })();
      } });
    },
    // A running line of the estate's place names, quickening with the scroll.
    marquee: function (after, o) {
      o = o || {}; if (!after) return;
      var names = ["Magnolia House", "The Valley", "Davis Hall", "The Lookout Deck", "Overlook Village"];
      var wrap = document.createElement("div"); wrap.className = "mq " + (o.cls || ""); wrap.setAttribute("aria-hidden", "true");
      var track = document.createElement("div"); track.className = "mq-track";
      var run = names.map(function (n) { return "<span>" + n + "</span><i></i>"; }).join("");
      track.innerHTML = run + run + run + run;
      wrap.appendChild(track); after.parentNode.insertBefore(wrap, after.nextSibling);
      var tw = g.to(track, { xPercent: -50, ease: "none", duration: o.dur || 38, repeat: -1 });
      ST.create({ trigger: wrap, start: "top bottom", end: "bottom top", onUpdate: function (s) {
        var v = Math.min(Math.abs(s.getVelocity()) / 400, 5);
        g.to(tw, { timeScale: (s.direction < 0 ? -1 : 1) * (1 + v), duration: 0.3, overwrite: true });
        g.to(tw, { timeScale: 1, duration: 1.2, delay: 0.3, overwrite: false });
      } });
      return wrap;
    }
  };

  /* ------------------------------------------------------------ foundation */
  function foundation() {
    // reading thread
    var bar = document.createElement("div"); bar.className = "m-progress"; document.body.appendChild(bar);
    g.to(bar, { scaleX: 1, ease: "none", scrollTrigger: { start: 0, end: "max", scrub: 0.3 } });

    // the header steps aside while reading down, and returns on the way up
    var head = $(".lw-head");
    if (head && getComputedStyle(head).position !== "absolute") {
      head.classList.add("m-head");
      var last = 0;
      ST.create({ start: 0, end: "max", onUpdate: function (s) {
        var y = s.scroll();
        head.classList.toggle("m-hidden", y > 160 && y > last);
        head.classList.toggle("m-scrolled", y > 20);
        last = y;
      } });
    }

    // every photograph can be touched
    $$("img").forEach(function (img) {
      if (img.closest(".lw-head,.m-peek,.dip-img")) return;
      var p = img.parentElement, cs = getComputedStyle(p);
      var padded = (parseFloat(cs.paddingTop) + parseFloat(cs.paddingLeft)) > 0;
      if (padded || p.tagName === "A" || p.children.length > 1 && getComputedStyle(img).position !== "absolute") {
        var w = document.createElement("span"); w.className = "hzw";
        p.insertBefore(w, img); w.appendChild(img);
      } else p.classList.add("hz");
    });

    // links and buttons
    $$(".btn,.link,.lw-cta").forEach(function (b) {
      if (!fine) return;
      b.addEventListener("mousemove", function (e) {
        var r = b.getBoundingClientRect();
        g.to(b, { x: (e.clientX - r.left - r.width / 2) * 0.28, y: (e.clientY - r.top - r.height / 2) * 0.4,
          duration: 0.5, ease: "power3.out" });
      });
      b.addEventListener("mouseleave", function () { g.to(b, { x: 0, y: 0, duration: 0.9, ease: "elastic.out(1,0.4)" }); });
    });

  }

  /* --------------------------------------------------- defaults for the rest */
  function sweep() {
    $$("main h2, body > section h2, section h2, section h3").forEach(function (h) { if (!isDone(h)) E.softIn(h, { chars: h.tagName === "H2" }); });
    $$("section p, figcaption p").forEach(function (p) { if (!isDone(p)) E.lift(p, { y: 22 }); });
    $$(".btn,.link").forEach(function (b) { if (!isDone(b)) E.lift(b, { y: 18 }); });
    $$("img").forEach(function (img) {
      if (img._rev || img.closest(".lw-head,.m-peek,.dip-img") || img.getBoundingClientRect().top < innerHeight * 0.9 && !img.closest(".way,.panel,.feature,.still")) return;
      E.reveal(img);
    });
  }

  /* --------------------------------------------------------- choreographies */
  var R = {};

  R["01"] = function () { // Aegean: a curtain of parchment lifts off the meadow
    var curtain = document.createElement("div"); curtain.className = "m-curtain"; $(".hero").appendChild(curtain);
    var tl = g.timeline({ delay: 0.15 });
    tl.to(curtain, { yPercent: -100, duration: 1.6, ease: "expo.inOut" })
      .from(".hero img", { scale: 1.35, duration: 2.8, ease: "expo.out" }, 0.2);
    E.softIn($(".intro .eyebrow"));
    E.softIn($(".intro h1"), { chars: true, rotate: 4, stagger: 0.03 });
    E.lift([$(".intro p"), $(".intro .btn")], { stagger: 0.15 });
    E.inkRead($(".line"));
    E.softIn($(".center-h"), { chars: true });
    $$(".ways .way").forEach(function (w, i) {
      E.reveal($("img", w), { from: "inset(100% 0% 0% 0%)", scale: 1.3, delay: i * 0.12 });
      E.lift([$("h3", w), $("p", w), $("a", w)], { trigger: w, delay: 0.3 + i * 0.12, stagger: 0.08 });
    });
    E.marquee($(".ways"), { cls: "mq-serif" });
    var full = $(".full img"); E.reveal(full, { from: "inset(18% 30% 18% 30%)", scale: 1.4, scaleTo: 1.12 }); E.drift(full, 7);
    E.softIn($(".claim h2"), { chars: true }); E.inkRead($(".claim p"));
    g.fromTo(".book", { clipPath: "inset(0% 12% 0% 12%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
      scrollTrigger: { trigger: ".book", start: "top bottom", end: "top 35%", scrub: true } });
    E.softIn($(".book h2"), { chars: true });
  };

  R["02"] = function () { // Folio: the spread opens like a page turning
    var tl = g.timeline({ delay: 0.1 });
    tl.fromTo(".spread figure img", { clipPath: "inset(0% 100% 0% 0%)", scale: 1.3 },
      { clipPath: "inset(0% 0% 0% 0%)", scale: 1, duration: 1.7, ease: "expo.inOut" })
      .from(".kick", { scaleX: 0, transformOrigin: "left", duration: 1.2, ease: "expo.inOut" }, 0.5)
      .add(E.maskIn($(".spread-text h1"), { stagger: 0.09, dur: 1.4 }), 0.75)
      .from([".spread-text p", ".spread-text .btn"], { y: 30, duration: 1.2, ease: "power3.out", stagger: 0.12 }, 1.2);
    done($(".spread-text p")); done($(".spread-text .btn"));
    E.inkRead($(".pull"));
    $$(".feature").forEach(function (f, i) {
      var img = $("img", f), left = i % 2 === 0;
      E.reveal(img, { from: left ? "inset(0% 0% 0% 100%)" : "inset(0% 100% 0% 0%)", scale: 1.25, scaleTo: 1.12, dur: 2 });
      E.drift(img, 5);
      E.softIn($(".kind", f));
      E.softIn($("h3", f), { chars: true, rotate: 3 });
      E.lift([$("p", f), $("a", f)], { trigger: f, delay: 0.25 });
    });
    E.softIn($(".claim h2"), { chars: true }); E.inkRead($(".claim p"));
    E.softIn($(".book h2"), { rotate: -2 });
  };

  R["03"] = function () { // Horizon: each landscape opens like a letterbox widening
    E.maskIn($(".cap h1"), { chars: true, delay: 0.5, stagger: 0.03 });
    done($(".cap h1"));
    $$(".pano").forEach(function (p, i) {
      var img = $("img", p);
      done(img); img._rev = true;
      if (i === 0) {
        g.fromTo(img, { clipPath: "inset(50% 0% 50% 0%)", scale: 1.3 },
          { clipPath: "inset(0% 0% 0% 0%)", scale: 1, duration: 2.2, ease: "expo.inOut", delay: 0.1 });
        return;
      }
      g.fromTo(img, { clipPath: "inset(24% 6% 24% 6%)", scale: 1.25 }, { clipPath: "inset(0% 0% 0% 0%)", scale: 1, ease: "none",
        scrollTrigger: { trigger: p, start: "top 95%", end: "center 45%", scrub: true } });
    });
    $$(".cap").forEach(function (c) {
      E.softIn($(".eyebrow", c)); E.softIn($("h2", c), { chars: true }); E.lift([$("p", c), $(".link", c)], { trigger: c, stagger: 0.12 });
    });
    $$(".ways .way").forEach(function (w, i) {
      E.reveal($("img", w), { from: "inset(0% 0% 100% 0%)", scale: 1.2, delay: i * 0.15 });
      E.lift([$("h3", w), $("p", w), $(".link", w)], { trigger: w, delay: 0.25 + i * 0.15 });
    });
  };

  R["04"] = function () { // Atelier: the grid draws itself, labels set like type
    var tl = g.timeline({ delay: 0.2 });
    tl.add(E.maskIn($(".hero h1"), { stagger: 0.08, dur: 1.3 }))
      .from(".hero .side", { y: 30, duration: 1.2, ease: "power3.out" }, 0.4)
      .fromTo(".hero-img img", { clipPath: "inset(0% 0% 100% 0%)", scale: 1.25 }, { clipPath: "inset(0% 0% 0% 0%)", scale: 1.1, duration: 1.8, ease: "expo.inOut" }, 0.5);
    done($(".hero .side")); $(".hero-img img")._rev = true;
    E.drift($(".hero-img img"), 6);
    $$(".lab").forEach(E.scramble);
    $$(".rule").forEach(function (r) {
      var ln = document.createElement("span"); ln.className = "m-rule-line"; r.classList.add("m-rule"); r.appendChild(ln);
      E.line(ln, { dur: 1.8 });
    });
    E.inkRead($(".line"));
    $$(".way").forEach(function (w, i) {
      var img = $("img", w);
      E.reveal(img, { from: "inset(0% 40% 0% 0%)", scale: 1.3, scaleTo: 1.1, delay: i * 0.1 });
      g.to(img.parentElement, { y: [-40, 30, -60][i % 3], ease: "none",
        scrollTrigger: { trigger: w, start: "top bottom", end: "bottom top", scrub: true } });
      E.softIn($("h3", w), { chars: true }); E.lift([$("p", w), $("a", w)], { trigger: w });
    });
    E.marquee($$(".g")[2], { cls: "mq-sans" });
    E.softIn($(".claim h2"), { chars: true }); E.inkRead($(".claim p"));
    var ci = $(".claim-img img"); E.reveal(ci, { from: "inset(0% 0% 0% 60%)", scale: 1.3, scaleTo: 1.1 }); E.drift(ci, 6);
  };

  R["05"] = function () { // Promenade: the band rises, the rail travels sideways
    var tl = g.timeline({ delay: 0.1 });
    tl.from(".hero > img", { scale: 1.3, duration: 2.6, ease: "expo.out" })
      .from(".hero-band", { yPercent: 100, duration: 1.4, ease: "expo.out" }, 0.4)
      .add(E.maskIn($(".hero-band h1"), { stagger: 0.07 }), 0.8)
      .from([".hero-band p", ".hero-band .btn", ".hero-band .eyebrow"], { y: 24, duration: 1, ease: "power3.out", stagger: 0.1 }, 1);
    [".hero-band p", ".hero-band .btn"].forEach(function (s) { done($(s)); });
    $(".hero > img")._rev = true;
    E.inkRead($(".line"));
    var rail = $(".rail");
    if (rail && wide) {
      rail.classList.add("m-pinned");
      var dist = function () { return rail.scrollWidth - rail.clientWidth; };
      g.to(rail.children, { x: function () { return -dist(); }, ease: "none",
        scrollTrigger: { trigger: rail, start: "center center", end: function () { return "+=" + dist(); },
          pin: true, scrub: 0.6, invalidateOnRefresh: true } });
    }
    $$(".panel").forEach(function (p, i) {
      E.reveal($("img", p), { from: "inset(12% 12% 12% 12%)", scale: 1.25, delay: i * 0.1 });
      E.lift($("div", p), { trigger: p, delay: 0.3 + i * 0.1 });
    });
    g.fromTo(".claim", { clipPath: "inset(10% 6% 10% 6%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
      scrollTrigger: { trigger: ".claim", start: "top bottom", end: "top 40%", scrub: true } });
    E.softIn($(".claim h2"), { chars: true });
  };

  R["06"] = function () { // Diptych: the held photograph changes by wiping upward
    var imgs = $$(".dip-img img");
    imgs.forEach(function (im, i) { g.set(im, { opacity: 1, clipPath: i === 0 ? "inset(0% 0% 0% 0%)" : "inset(100% 0% 0% 0%)", zIndex: i }); im.classList.add("m-dip"); });
    g.from(imgs[0], { scale: 1.3, duration: 2.4, ease: "expo.out" });
    E.maskIn($(".dip-text section h1"), { stagger: 0.08, delay: 0.3 });
    var secs = $$(".dip-text section");
    secs.forEach(function (s, i) {
      if (i > 0 && imgs[i] && wide) {
        g.timeline({ scrollTrigger: { trigger: s, start: "top 75%", end: "top 25%", scrub: true } })
          .fromTo(imgs[i], { clipPath: "inset(100% 0% 0% 0%)", scale: 1.25 }, { clipPath: "inset(0% 0% 0% 0%)", scale: 1, ease: "none" })
          .to(imgs[i - 1], { scale: 1.12, ease: "none" }, 0);
      }
      $$("h2", s).forEach(function (h) { E.softIn(h, { chars: true }); });
      E.inkRead($(".line", s));
      $$(".way", s).forEach(function (w) { E.lift(w, { y: 26 }); });
    });
    var bar = document.createElement("div"); bar.className = "m-dip-bar"; $(".dip-text").appendChild(bar);
    g.fromTo(bar, { scaleY: 0 }, { scaleY: 1, ease: "none", scrollTrigger: { trigger: ".dip-text", start: "top top", end: "bottom bottom", scrub: true } });
  };

  R["07"] = function () { // Invitation: engraved capitals settle, rules and keylines draw
    var tl = g.timeline({ delay: 0.2 });
    tl.add(E.track($(".col .cap"), { now: true, from: "1.2em" }), 0.1)
      .add(E.maskIn($(".col h1"), { stagger: 0.1, dur: 1.5 }), 0.3)
      .from([".col p", ".col .btn"], { y: 22, duration: 1.2, ease: "power3.out", stagger: 0.12 }, 0.9);
    done($$(".col p")[0]); done($$(".col .btn")[0]);
    $$(".orn").forEach(function (o) { E.line(o, { origin: "center center" }); });
    $$(".plate").forEach(function (p, i) {
      p.classList.add("m-plate");
      ST.create({ trigger: p, start: "top 88%", once: true, onEnter: function () { p.classList.add("is-drawn"); } });
      var img = $("img", p);
      E.reveal(img, { from: "inset(6% 6% 6% 6%)", scale: 1.18, dur: 2.2, delay: 0.35 });
      if (!p.closest(".way")) E.drift(img, 4);
    });
    $$(".cap").forEach(function (c, i) { if (i) E.track(c, { from: "0.9em" }); });
    E.inkRead($(".line"));
    $$(".col h2").forEach(function (h) { E.softIn(h, { chars: true }); });
    $$(".way").forEach(function (w, i) { E.lift([$("h3", w), $("p", w), $("a", w)], { trigger: w, delay: 0.3 + i * 0.12, stagger: 0.06 }); });
  };

  R["08"] = function () { // Cinema: the film gives way to the page, the stills roll like frames
    var film = $(".film");
    g.to(film, { clipPath: "inset(6% 6% 6% 6%)", ease: "none",
      scrollTrigger: { trigger: film, start: "top top", end: "bottom top", scrub: true } });
    g.to(".film video, .film img", { scale: 1.15, ease: "none", scrollTrigger: { trigger: film, start: "top top", end: "bottom top", scrub: true } });
    E.softIn($(".band h1"), { chars: true, rotate: 3 });
    E.lift([$(".band p"), $(".band .btn")], { trigger: ".band" });
    E.inkRead($(".line"));
    $$(".still").forEach(function (s) {
      var img = $("img", s);
      g.fromTo(img, { clipPath: "inset(20% 0% 20% 0%)", scale: 1.3 }, { clipPath: "inset(0% 0% 0% 0%)", scale: 1.05, ease: "none",
        scrollTrigger: { trigger: s, start: "top bottom", end: "top 20%", scrub: true } });
      img._rev = true; done(img);
      E.softIn($("h3", s), { chars: true });
      E.lift([$(".kind", s), $("p", s), $("a", s)], { trigger: $("figcaption", s), stagger: 0.08 });
    });
    E.softIn($(".claim h2"), { chars: true });
    g.fromTo(".claim", { clipPath: "inset(0% 50% 0% 50%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
      scrollTrigger: { trigger: ".claim", start: "top bottom", end: "top 50%", scrub: true } });
  };

  R["09"] = function () { // Olive Grove: colour floods in and the type rises through it
    var tl = g.timeline({ delay: 0.1 });
    tl.fromTo(".hero.olive", { clipPath: "inset(0% 50% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.5, ease: "expo.inOut" })
      .fromTo(".hero figure img", { clipPath: "inset(100% 0% 0% 0%)", scale: 1.35 }, { clipPath: "inset(0% 0% 0% 0%)", scale: 1, duration: 1.8, ease: "expo.inOut" }, 0.35)
      .add(E.maskIn($(".hero h1"), { stagger: 0.08 }), 0.7)
      .from([".hero-text .eyebrow", ".hero-text p", ".hero-text .btn"], { y: 26, duration: 1.1, ease: "power3.out", stagger: 0.12 }, 1);
    $(".hero figure img")._rev = true; done($(".hero-text p")); done($(".hero-text .btn"));
    E.inkRead($(".line"));
    E.marquee($(".line"), { cls: "mq-olive" });
    $$(".ways .way").forEach(function (w, i) {
      E.reveal($("img", w), { from: "inset(0% 0% 0% 100%)", scale: 1.3, delay: i * 0.14 });
      var d = $("div", w);
      if (i === 1) g.fromTo(d, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.4, ease: "expo.inOut",
        scrollTrigger: { trigger: w, start: "top 80%", once: true } });
      E.softIn($("h3", w), { chars: true }); E.lift([$("p", w), $("a", w)], { trigger: w, delay: 0.3 });
    });
    g.fromTo(".claim.olive", { clipPath: "inset(0% 10% 0% 10%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
      scrollTrigger: { trigger: ".claim", start: "top bottom", end: "top 35%", scrub: true } });
    E.softIn($(".claim h2"), { rotate: 2 });
    var bi = $(".book img"); E.reveal(bi, { from: "inset(0% 100% 0% 0%)", scale: 1.3, scaleTo: 1.1 }); E.drift(bi, 6);
  };

  R["10"] = function () { // Mosaic: the headline builds letter by letter over tiles that fall into place
    var tl = g.timeline({ delay: 0.15 });
    tl.add(E.maskIn($(".mast h1"), { chars: true, stagger: 0.028, dur: 1.3, rotate: 6 }))
      .from(".thread", { scaleX: 0, transformOrigin: "left", duration: 1.2, ease: "expo.inOut" }, 0.6)
      .from([".mast-row p", ".mast-row .btn"], { y: 24, duration: 1.1, ease: "power3.out", stagger: 0.1 }, 0.8);
    done($(".mast-row p")); done($(".mast-row .btn"));
    $$(".mosaic figure").forEach(function (f, i) {
      var img = $("img", f);
      E.reveal(img, { now: true, from: ["inset(0% 0% 100% 0%)", "inset(0% 100% 0% 0%)", "inset(100% 0% 0% 0%)", "inset(0% 0% 0% 100%)", "inset(50% 50% 50% 50%)"][i % 5],
        scale: 1.3, dur: 1.6, delay: 0.6 + i * 0.12 });
    });
    E.inkRead($(".line"));
    // list rows: a photograph follows the pointer
    if (fine) {
      var peek = document.createElement("div"); peek.className = "m-peek"; document.body.appendChild(peek);
      var px = g.quickTo(peek, "x", { duration: 0.6, ease: "power3" }), py = g.quickTo(peek, "y", { duration: 0.6, ease: "power3" });
      $$(".ways .way").forEach(function (row) {
        var src = $("img", row).currentSrc || $("img", row).src;
        row.addEventListener("mouseenter", function () { peek.style.backgroundImage = "url('" + src + "')"; peek.classList.add("on"); });
        row.addEventListener("mouseleave", function () { peek.classList.remove("on"); });
        row.addEventListener("mousemove", function (e) { px(e.clientX); py(e.clientY); });
      });
    }
    $$(".ways .way").forEach(function (row, i) {
      E.softIn($("h3", row), { chars: true });
      E.reveal($("img", row), { from: "inset(0% 100% 0% 0%)", scale: 1.2, delay: i * 0.08 });
      E.lift([$("p", row), $("span", row)], { trigger: row });
    });
    E.softIn($(".claim h2"), { chars: true, rotate: 3 }); E.inkRead($(".claim p"));
    E.softIn($(".book h2"), { chars: true });
  };

  /* ------------------------------------------------------------------- run */
  function run() {
    foundation();
    if (R[dir]) R[dir]();
    sweep();
    ST.refresh();
  }
  if (document.readyState === "complete") run(); else addEventListener("load", run);
})();
