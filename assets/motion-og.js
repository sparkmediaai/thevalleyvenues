/* Motion for the whole site, in the Olive Grove direction.

   The engine from the wedding lab, on the real pages. Every page gets the
   same foundation -- smooth scrolling with a mouse, a reading thread in the
   accent, a header that steps aside while reading down and returns on the
   way up, buttons that lean toward the pointer, and a slow zoom on the
   photographs you can hover -- then the home and Weddings pages get their own
   opening, and everything else a quiet sweep: headings rise and ink in,
   photographs open from a partly visible frame.

   Rules:
   - Words are never hidden waiting for a scroll. They rise and ink in from
     the olive, readable throughout; only an opening, which plays at once,
     masks type.
   - The pointer itself is left alone.
   - Nothing here fights the site's older motion: elements already handled by
     reveal.js / motion.css (.reveal, .rise-words, .wipe, .par, the cluster,
     the claim's drift) are skipped.

   GSAP + ScrollTrigger + Lenis are bundled in /assets/vendor. If they fail to
   load the pages are simply static and complete. */
(function () {
  "use strict";
  if (!window.gsap || !window.ScrollTrigger) return;
  var g = window.gsap, ST = window.ScrollTrigger;
  g.registerPlugin(ST);

  var INK = "#2B1B00", OLIVE = "#7B7951";
  var page = document.body.getAttribute("data-page") || "";
  var fine = matchMedia("(hover:hover) and (pointer:fine)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var SKIP = ".reveal,.rise-words,.wipe,.par,.cluster,.claim-img,.gx,.gv,.park-stage,.walk-map,.ghl-form,.site-head,.site-foot,.hero-stage,.opening";

  /* -------------------------------------------------------- smooth scrolling */
  if (fine && window.Lenis) {
    var lenis = new window.Lenis({ lerp: 0.09, wheelMultiplier: 0.9 });
    window.__lenis = lenis;
    lenis.on("scroll", ST.update);
    g.ticker.add(function (t) { lenis.raf(t * 1000); });
    g.ticker.lagSmoothing(0);
    // the gallery viewer scrolls its own strip and locks the page behind it
    new MutationObserver(function () {
      if (document.body.classList.contains("gv-lock")) lenis.stop(); else lenis.start();
    }).observe(document.body, { attributes: true, attributeFilter: ["class"] });
  }

  /* --------------------------------------------------------------- splitting */
  function split(el, mode) {
    if (el._split) return el._split;
    var parts = [], label = el.textContent.replace(/\s+/g, " ").trim();
    (function walk(node) {
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
        } else if (n.nodeType === 1 && n.tagName !== "BR") walk(n);
      });
    })(el);
    if (mode === "chars") {
      el.setAttribute("aria-label", label);
      $$(".sw", el).forEach(function (s) { s.setAttribute("aria-hidden", "true"); });
    }
    return (el._split = parts);
  }
  function mark(el) { el.setAttribute("data-m", ""); return el; }
  function marked(el) { return el.hasAttribute("data-m"); }
  function isInk(el) { return getComputedStyle(el).color === "rgb(43, 27, 0)"; }

  var E = {
    maskIn: function (el, o) {
      o = o || {}; if (!el) return g.timeline();
      mark(el); el.classList.add("m-mask");
      return g.from(split(el, o.chars ? "chars" : "words"), { yPercent: 115, duration: o.dur || 1.25,
        ease: "expo.out", stagger: o.stagger || (o.chars ? 0.022 : 0.07), delay: o.delay || 0 });
    },
    softIn: function (el, o) {
      o = o || {}; if (!el || marked(el)) return; mark(el);
      var from = { y: o.chars ? "0.45em" : "0.6em" };
      if (isInk(el)) from.color = OLIVE;
      g.from(split(el, o.chars ? "chars" : "words"), Object.assign(from, { duration: 1.1, ease: "power3.out",
        stagger: o.chars ? 0.014 : 0.03, scrollTrigger: { trigger: el, start: "top 90%", once: true } }));
    },
    inkRead: function (el) {
      if (!el || marked(el)) return; mark(el);
      if (!isInk(el)) return E.softIn(el);
      g.fromTo(split(el, "words"), { color: OLIVE }, { color: INK, ease: "none", stagger: 0.1,
        scrollTrigger: { trigger: el, start: "top 82%", end: "bottom 45%", scrub: true } });
    },
    lift: function (els, o) {
      o = o || {};
      els = [].concat(els).filter(function (e) { return e && !marked(e); });
      if (!els.length) return;
      els.forEach(function (e) {
        mark(e);
        if (getComputedStyle(e).display === "inline") e.style.display = "inline-block";
      });
      g.from(els, { y: o.y || 30, duration: 1.2, ease: "power3.out", stagger: o.stagger || 0.1, delay: o.delay || 0,
        scrollTrigger: { trigger: o.trigger || els[0], start: "top 92%", once: true } });
    },
    reveal: function (img, o) {
      o = o || {}; if (!img || img._rev) return; img._rev = true;
      g.fromTo(img, { clipPath: o.from || "inset(10% 8% 10% 8%)", scale: o.scale || 1.2 },
        { clipPath: "inset(0% 0% 0% 0%)", scale: 1, duration: 1.8, ease: "expo.out", delay: o.delay || 0,
          scrollTrigger: { trigger: img.parentElement, start: "top 88%", once: true } });
    },
    drift: function (img, amt) {
      if (!img) return;
      g.fromTo(img, { yPercent: -(amt || 5) }, { yPercent: amt || 5, ease: "none",
        scrollTrigger: { trigger: img.parentElement, start: "top bottom", end: "bottom top", scrub: true } });
    },
    marquee: function (after) {
      if (!after) return;
      var names = ["Magnolia House", "The Valley", "Davis Hall", "The Lookout Deck", "Overlook Village"];
      var wrap = document.createElement("div"); wrap.className = "mq"; wrap.setAttribute("aria-hidden", "true");
      var run = names.map(function (n) { return "<span>" + n + "</span><i></i>"; }).join("");
      wrap.innerHTML = '<div class="mq-track">' + run + run + run + run + "</div>";
      after.parentNode.insertBefore(wrap, after.nextSibling);
      var tw = g.to(wrap.firstChild, { xPercent: -50, ease: "none", duration: 40, repeat: -1 });
      ST.create({ trigger: wrap, start: "top bottom", end: "bottom top", onUpdate: function (s) {
        var v = Math.min(Math.abs(s.getVelocity()) / 400, 5);
        g.to(tw, { timeScale: (s.direction < 0 ? -1 : 1) * (1 + v), duration: 0.3, overwrite: true });
        g.to(tw, { timeScale: 1, duration: 1.2, delay: 0.3, overwrite: false });
      } });
    }
  };

  /* -------------------------------------------------------------- foundation */
  function foundation() {
    var bar = document.createElement("div"); bar.className = "m-progress"; document.body.appendChild(bar);
    g.to(bar, { scaleX: 1, ease: "none", scrollTrigger: { start: 0, end: "max", scrub: 0.3 } });

    var head = $(".site-head"), last = 0;
    if (head) ST.create({ start: 0, end: "max", onUpdate: function (s) {
      var y = s.scroll();
      if (!head.classList.contains("nav-open")) head.classList.toggle("m-hidden", y > 200 && y > last);
      last = y;
    } });

    // photographs that can be hovered zoom slowly inside their frame
    $$("main img").forEach(function (img) {
      if (img.closest(SKIP) || img.closest(".og-way,.og-book,.wk,.card-door,.split,.spot-photo,.place-photo,.kobi-photo,.room-photo") == null) return;
      var p = img.parentElement;
      if (p.classList.contains("hzw")) return;
      var w = document.createElement("span"); w.className = "hzw";
      p.insertBefore(w, img); w.appendChild(img);
      var decide = function () {
        var ih = img.getBoundingClientRect().height;
        if (ih > 40 && Math.abs(p.getBoundingClientRect().height - ih) < 4) w.classList.add("hzw-fill");
      };
      if (img.complete && img.naturalWidth) decide(); else img.addEventListener("load", decide, { once: true });
    });

    // buttons lean toward the pointer
    if (fine) $$(".btn").forEach(function (b) {
      b.addEventListener("mousemove", function (e) {
        var r = b.getBoundingClientRect();
        g.to(b, { x: (e.clientX - r.left - r.width / 2) * 0.22, y: (e.clientY - r.top - r.height / 2) * 0.35,
          duration: 0.5, ease: "power3.out" });
      });
      b.addEventListener("mouseleave", function () { g.to(b, { x: 0, y: 0, duration: 0.9, ease: "elastic.out(1,0.4)" }); });
    });
  }

  /* -------------------------------------------------------------------- pages */
  var R = {};

  R.home = function () { // the film alone, settling; its words rise in beneath it
    g.from(".hero-stage", { scale: 1.08, duration: 2.8, ease: "expo.out" });
    var body = $(".hero-clock .hero-body");
    if (!body) return;
    E.maskIn($("h1", body), { stagger: 0.08, delay: 0.4 });
    E.lift($$(".eyebrow, p, .hero-actions", body), { stagger: 0.12, trigger: body });
  };

  R.weddings = function () {
    var tl = g.timeline({ delay: 0.1 });
    tl.from(".fh-media", { scale: 1.14, duration: 2.8, ease: "expo.out" })
      .from(".fh-band", { yPercent: 100, duration: 1.4, ease: "expo.out" }, 0.35)
      .add(E.maskIn($(".fh-band h1"), { stagger: 0.08 }), 0.75)
      .from([".fh-band .eyebrow", ".fh-band p", ".fh-band .btn"], { y: 24, duration: 1.1, ease: "power3.out", stagger: 0.12 }, 1)
      .from(".fh-pause", { y: 20, opacity: 0, duration: 0.8, ease: "power3.out" }, 1.4);
    [".fh-band p", ".fh-band .btn", ".fh-band .eyebrow"].forEach(function (s) { if ($(s)) mark($(s)); });
    g.to(".fh-media", { yPercent: 12, ease: "none", scrollTrigger: { trigger: ".fh", start: "top top", end: "bottom top", scrub: true } });

    E.inkRead($(".og-line"));
    E.marquee($(".og-line"));
    $$(".og-way").forEach(function (w, i) {
      E.reveal($("img", w), { from: "inset(0% 0% 0% 100%)", scale: 1.3, delay: i * 0.14 });
      var d = $("div", w);
      if (i === 1) g.fromTo(d, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.4,
        ease: "expo.inOut", scrollTrigger: { trigger: w, start: "top 80%", once: true } });
      E.softIn($("h3", w), { chars: true });
      E.lift([$(".eyebrow", w), $("p", w), $("a", w)], { trigger: w, delay: 0.3 });
    });
    g.fromTo(".og-claim", { clipPath: "inset(0% 10% 0% 10%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none",
      scrollTrigger: { trigger: ".og-claim", start: "top bottom", end: "top 35%", scrub: true } });
    E.softIn($(".og-claim h2"));
    var bi = $(".og-book img"); E.reveal(bi, { from: "inset(0% 100% 0% 0%)", scale: 1.3 }); E.drift(bi, 6);
  };

  /* every page: a quiet sweep over what the page's own recipe did not take */
  function sweep() {
    $$("main h2, main h3").forEach(function (h) {
      if (marked(h) || h.closest(SKIP) || h.closest(".statement,.claim,.band,.closing") && h.closest(".rise-words")) return;
      if (h.closest(SKIP)) return;
      E.softIn(h, { chars: h.tagName === "H2" });
    });
    $$(".band-img").forEach(function (img) { E.reveal(img, { from: "inset(14% 0% 14% 0%)", scale: 1.15 }); E.drift(img, 5); });
    $$(".split img, .spot-photo img, .kobi-photo img, .room-photo img, .wk img, .card-door img").forEach(function (img) {
      if (img.closest(SKIP) || img.matches(".par,.wipe")) return;
      E.reveal(img);
    });
  }

  function run() {
    foundation();
    if (R[page]) R[page]();
    sweep();
    ST.refresh();
  }
  if (document.readyState === "complete") run(); else addEventListener("load", run);
})();
