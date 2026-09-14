/* The gallery: filters, and the viewer.

   The wall itself is plain markup and CSS, so everything here is enhancement.
   Without this file every tile is still a link to the full photograph.

   Filters narrow the wall by place and by photographer, and write the choice
   into the address, so "the Magnolia House photographs" can be sent to
   somebody as a link.

   The viewer opens on ivory rather than black, keeps the photographer's credit
   under every frame, and moves the way a phone expects: drag the picture and
   it follows the finger, let go past a third of a thumb and it goes. Arrow
   keys and Escape on a keyboard; a filmstrip on a wide screen. The open photo
   is in the address too (#photo-id), and the back button closes it. */
(function () {
  var wall = document.querySelector(".gx");
  if (!wall) return;

  var items = [].slice.call(wall.querySelectorAll(".gx-item"));
  var chips = [].slice.call(document.querySelectorAll(".gx-chip"));
  var select = document.querySelector(".gx-select");
  var count = document.querySelector(".gx-count span");
  var bar = document.querySelector(".gx-bar");
  var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var head = document.querySelector(".site-head");
  function measure() {
    if (head) document.documentElement.style.setProperty("--head", head.offsetHeight + "px");
  }
  measure();
  addEventListener("resize", measure);
  var PLACE = {};
  chips.forEach(function (c) {
    if (c.dataset.place) PLACE[c.dataset.place] = c.firstChild.textContent.trim();
  });

  /* ---------------------------------------------------------- loading in */
  items.forEach(function (a) {
    var img = a.querySelector("img");
    img.draggable = false;
    function done() { img.classList.add("is-in"); }
    if (img.complete && img.naturalWidth) done();
    else { img.addEventListener("load", done, { once: true }); img.addEventListener("error", done, { once: true }); }
  });

  /* ------------------------------------------------------------- filters */
  var state = { place: "", credit: "" };
  var q = new URLSearchParams(location.search);
  if (PLACE[q.get("place")]) state.place = q.get("place");
  if (q.get("by")) state.credit = q.get("by");

  function shown() { return items.filter(function (a) { return !a.hidden; }); }

  function apply(animate) {
    var n = 0;
    items.forEach(function (a) {
      var ok = (!state.place || (" " + a.dataset.tags + " ").indexOf(" " + state.place + " ") > -1) &&
               (!state.credit || a.dataset.credit === state.credit);
      a.hidden = !ok;
      if (ok) n++;
    });
    if (count) count.textContent = n;
    chips.forEach(function (c) {
      c.setAttribute("aria-pressed", c.dataset.place === state.place ? "true" : "false");
    });
    if (select) select.value = state.credit;
    if (animate) { wall.classList.remove("is-sorting"); void wall.offsetWidth; wall.classList.add("is-sorting"); }

    var p = new URLSearchParams(location.search);
    if (state.place) p.set("place", state.place); else p.delete("place");
    if (state.credit) p.set("by", state.credit); else p.delete("by");
    var qs = p.toString();
    history.replaceState(history.state, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
  }

  function toBar() {
    if (bar && bar.getBoundingClientRect().top < 0) {
      bar.parentNode.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });
    }
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      state.place = c.dataset.place;
      apply(true);
      toBar();
      c.scrollIntoView({ inline: "nearest", block: "nearest" });
    });
  });
  if (select) select.addEventListener("change", function () { state.credit = select.value; apply(true); toBar(); });
  [].forEach.call(document.querySelectorAll(".gx-names button"), function (b) {
    b.addEventListener("click", function () {
      state.credit = b.dataset.credit;
      state.place = "";
      apply(true);
      bar.parentNode.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });
    });
  });
  if (state.place || state.credit) apply(false);

  /* -------------------------------------------------------------- viewer */
  var ICON = {
    close: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3 3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    prev: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 2 4 8l6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    next: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 2 6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  };
  var gv, stage, track, slides, strip, list = [], at = 0, lastFocus = null, busy = false;

  function big(a) { return "/assets/gallery/" + a.dataset.id + ".webp"; }
  function small(a) { return "/assets/gallery/" + a.dataset.id + "-sm.webp"; }
  function ratio(a) { return parseFloat(a.style.getPropertyValue("--r")) || 1.5; }

  function make() {
    gv = document.createElement("div");
    gv.className = "gv";
    gv.setAttribute("role", "dialog");
    gv.setAttribute("aria-modal", "true");
    gv.setAttribute("aria-label", "Photograph viewer");
    gv.innerHTML =
      '<div class="gv-top"><span class="gv-count"></span><span class="gv-place"></span>' +
      '<button type="button" class="gv-btn gv-close" aria-label="Close">' + ICON.close + '</button></div>' +
      '<div class="gv-stage"><div class="gv-track">' +
      '<div class="gv-slide"><img alt="" draggable="false"></div>' +
      '<div class="gv-slide"><img alt="" draggable="false"></div>' +
      '<div class="gv-slide"><img alt="" draggable="false"></div></div>' +
      '<button type="button" class="gv-btn gv-prev" aria-label="Previous photograph">' + ICON.prev + '</button>' +
      '<button type="button" class="gv-btn gv-next" aria-label="Next photograph">' + ICON.next + '</button></div>' +
      '<div class="gv-foot"><p class="gv-credit"></p><div class="gv-strip" role="group" aria-label="All photographs in view"></div></div>';
    document.body.appendChild(gv);
    stage = gv.querySelector(".gv-stage");
    track = gv.querySelector(".gv-track");
    slides = [].slice.call(gv.querySelectorAll(".gv-slide"));
    strip = gv.querySelector(".gv-strip");

    gv.querySelector(".gv-close").addEventListener("click", function () { close(true); });
    gv.querySelector(".gv-prev").addEventListener("click", function () { go(-1); });
    gv.querySelector(".gv-next").addEventListener("click", function () { go(1); });
    gv.addEventListener("keydown", key);
    stage.addEventListener("click", function (e) {
      // a click on the empty margin around the picture closes, as expected
      if (e.target === stage || e.target.classList.contains("gv-slide")) { if (!moved) close(true); }
    });
    drag();
    addEventListener("resize", function () { if (gv.classList.contains("is-open")) size(); });
  }

  // Size each picture to fit before its full-size file arrives, so swapping the
  // thumbnail for the photograph never changes its size on screen.
  function fit(img, a) {
    var r = ratio(a), sw = stage.clientWidth, sh = stage.clientHeight;
    var pad = parseFloat(getComputedStyle(img.parentNode).paddingLeft) * 2;
    var w = Math.min(sw - pad, (sh - 8) * r), h = w / r;
    img.style.width = Math.max(0, Math.floor(w)) + "px";
    img.style.height = Math.max(0, Math.floor(h)) + "px";
  }
  function size() { [-1, 0, 1].forEach(function (d, i) { if (list[at + d]) fit(slides[i].querySelector("img"), list[at + d]); }); }

  function fill(slide, a) {
    var img = slide.querySelector("img");
    if (!a) { img.removeAttribute("src"); img.alt = ""; img.dataset.id = ""; img.style.visibility = "hidden"; return; }
    img.style.visibility = "";
    fit(img, a);
    if (img.dataset.id === a.dataset.id) return;
    img.dataset.id = a.dataset.id;
    img.src = small(a);
    img.alt = a.querySelector("img").alt;
    var full = new Image();
    full.onload = function () { if (img.dataset.id === a.dataset.id) img.src = full.src; };
    full.src = big(a);
  }

  function place(x, animate) {
    track.style.transition = animate && !still ? "transform .42s cubic-bezier(.2,.8,.25,1)" : "none";
    track.style.transform = "translateX(calc(-100% + " + x + "px))";
  }

  function render() {
    var a = list[at];
    fill(slides[0], list[at - 1]);
    fill(slides[1], a);
    fill(slides[2], list[at + 1]);
    place(0, false);
    gv.querySelector(".gv-count").textContent = (at + 1) + " / " + list.length;
    gv.querySelector(".gv-place").textContent = a.dataset.tags.split(" ").map(function (t) { return PLACE[t] || ""; }).join(" · ");
    gv.querySelector(".gv-credit").innerHTML = "Photograph by <b></b>";
    gv.querySelector(".gv-credit b").textContent = a.dataset.credit;
    gv.querySelector(".gv-prev").disabled = at === 0;
    gv.querySelector(".gv-next").disabled = at === list.length - 1;
    [].forEach.call(strip.children, function (b, i) {
      b.setAttribute("aria-current", i === at ? "true" : "false");
      if (i === at) b.scrollIntoView({ inline: "center", block: "nearest", behavior: still ? "auto" : "smooth" });
    });
    history.replaceState({ gv: 1 }, "", location.pathname + location.search + "#" + a.dataset.id);
    // warm the next ones along
    [2, -2].forEach(function (d) { if (list[at + d]) new Image().src = big(list[at + d]); });
  }

  function go(dir) {
    if (busy) return;
    var next = at + dir;
    if (next < 0 || next >= list.length) { place(0, true); return; }
    if (still) { at = next; render(); return; }
    busy = true;
    place(-dir * stage.clientWidth, true);
    setTimeout(function () { at = next; render(); busy = false; }, 430);
  }

  function open(a, fromHistory) {
    if (!gv) make();
    list = shown();
    at = Math.max(0, list.indexOf(a));
    lastFocus = document.activeElement;
    strip.innerHTML = "";
    list.forEach(function (it, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", "Photograph " + (i + 1));
      b.innerHTML = '<img loading="lazy" alt="" src="' + small(it) + '">';
      b.addEventListener("click", function () { at = i; render(); });
      strip.appendChild(b);
    });
    document.body.classList.add("gv-lock");
    gv.classList.add("is-open");
    if (!fromHistory) history.pushState({ gv: 1 }, "", location.pathname + location.search + "#" + a.dataset.id);
    render();
    gv.querySelector(".gv-close").focus({ preventScroll: true });
  }

  function close(viaButton) {
    if (!gv || !gv.classList.contains("is-open")) return;
    gv.classList.remove("is-open");
    document.body.classList.remove("gv-lock");
    var a = list[at];
    if (viaButton && history.state && history.state.gv) history.back();
    else history.replaceState(null, "", location.pathname + location.search);
    if (a) { a.scrollIntoView({ block: "nearest" }); a.focus({ preventScroll: true }); }
    else if (lastFocus) lastFocus.focus({ preventScroll: true });
  }

  function key(e) {
    if (e.key === "ArrowRight") { go(1); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { go(-1); e.preventDefault(); }
    else if (e.key === "Escape") { close(true); e.preventDefault(); }
    else if (e.key === "Tab") {
      var f = [].slice.call(gv.querySelectorAll("button:not([disabled])")).filter(function (b) { return b.offsetParent; });
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { f[f.length - 1].focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { f[0].focus(); e.preventDefault(); }
    }
  }

  var moved = false;
  function drag() {
    var x0 = null, y0 = 0, t0 = 0, dx = 0, id = null, horizontal = null;
    stage.addEventListener("pointerdown", function (e) {
      if (e.button !== 0 || busy || e.target.closest(".gv-btn")) return;
      x0 = e.clientX; y0 = e.clientY; t0 = Date.now(); dx = 0; horizontal = null; moved = false; id = e.pointerId;
    });
    stage.addEventListener("pointermove", function (e) {
      if (x0 === null || e.pointerId !== id) return;
      dx = e.clientX - x0;
      var dy = e.clientY - y0;
      if (horizontal === null && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {
        horizontal = Math.abs(dx) > Math.abs(dy);
        if (horizontal) { stage.setPointerCapture(id); moved = true; }
      }
      if (!horizontal) return;
      // resist at either end of the set
      var edge = (at === 0 && dx > 0) || (at === list.length - 1 && dx < 0);
      place(edge ? dx / 3 : dx, false);
    });
    function end(e) {
      if (x0 === null || e.pointerId !== id) return;
      var fast = Math.abs(dx) / Math.max(1, Date.now() - t0) > .5;
      if (horizontal && (Math.abs(dx) > stage.clientWidth / 6 || (fast && Math.abs(dx) > 30))) go(dx < 0 ? 1 : -1);
      else if (horizontal) place(0, true);
      x0 = null;
      setTimeout(function () { moved = false; }, 0);
    }
    stage.addEventListener("pointerup", end);
    stage.addEventListener("pointercancel", end);
  }

  items.forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;   // new tab still works
      e.preventDefault();
      open(a);
    });
  });

  function fromHash(fromHistory) {
    var id = location.hash.slice(1);
    var a = id && items.filter(function (it) { return it.dataset.id === id; })[0];
    if (a) { if (a.hidden) { state.place = ""; state.credit = ""; apply(false); } open(a, fromHistory); }
    else close(false);
  }
  addEventListener("popstate", function () { fromHash(true); });
  if (location.hash.length > 1) fromHash(true);
})();
