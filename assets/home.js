/* The hero clock.

   Five frames from one day, crossfading. Four things this has to get right,
   and they are all about not making the page worse to arrive at:

   1. Only the first frame is fetched with the document. It is the largest thing
      the page paints, so the other four wait until load and then come in
      quietly. A hero that ships five 2200px images is a slow hero.
   2. It stops when the tab is hidden. Nobody needs a crossfade running in a
      background tab on a laptop battery.
   3. It never runs at all under prefers-reduced-motion, and with JavaScript off
      the first frame simply stays put. The page reads either way.
   4. It can be driven. Arrows, marks, arrow keys and swipe all do the same
      thing, and any of them holds the timer -- being carried off a frame you
      were looking at because six seconds elapsed is the whole reason the first
      version felt hard to use. */
(function () {
  var stage = document.querySelector(".hero-stage");
  if (!stage) return;

  var hero = stage.closest(".hero") || stage;
  var slides = [].slice.call(stage.querySelectorAll(".slide"));
  var dots = [].slice.call(stage.querySelectorAll(".hero-dots button"));
  var steps = [].slice.call(stage.querySelectorAll(".hero-step"));
  var hour = stage.querySelector(".hero-hour span");
  if (slides.length < 2) return;

  var at = 0, timer = null, held = false;
  var HOLD = 6200;
  var still = matchMedia("(prefers-reduced-motion: reduce)");

  // The bar under the active mark is a CSS animation of this length. Telling
  // the stylesheet the number from here keeps the two from drifting apart.
  stage.style.setProperty("--hold", HOLD + "ms");

  function show(next) {
    next = (next + slides.length) % slides.length;
    if (next === at) return;
    slides[at].classList.remove("is-on");
    at = next;
    slides[at].classList.add("is-on");
    if (hour) hour.textContent = slides[at].getAttribute("data-moment") || "";
    dots.forEach(function (d, i) {
      d.setAttribute("aria-current", i === at ? "true" : "false");
    });
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  function play() {
    stop();
    if (still.matches || held || document.hidden) return;
    timer = setInterval(function () { show(at + 1); }, HOLD);
  }

  /* Held while somebody is reading it. The bar pauses with the timer, so it
     never promises a change that is not coming. */
  function hold(on) {
    held = on;
    stage.classList.toggle("is-held", on);
    if (on) stop(); else play();
  }

  // A press moves the slide and restarts the six seconds, rather than leaving
  // a half-elapsed timer to yank the frame away a moment later.
  function go(next) { show(next); if (!held) play(); }

  dots.forEach(function (d, i) {
    d.addEventListener("click", function () { go(i); });
  });
  steps.forEach(function (b) {
    b.addEventListener("click", function () {
      go(at + (parseInt(b.getAttribute("data-step"), 10) || 1));
    });
  });

  hero.addEventListener("pointerenter", function () { hold(true); });
  hero.addEventListener("pointerleave", function () { hold(false); });
  hero.addEventListener("focusin", function () { hold(true); });
  hero.addEventListener("focusout", function (e) {
    if (!hero.contains(e.relatedTarget)) hold(false);
  });

  hero.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") { go(at - 1); e.preventDefault(); }
    if (e.key === "ArrowRight") { go(at + 1); e.preventDefault(); }
  });

  /* Swipe. On a phone the marks are small, the arrows are not much bigger, and
     the gesture anybody would try first is dragging the picture. */
  var x0 = null, y0 = null;
  stage.addEventListener("touchstart", function (e) {
    x0 = e.changedTouches[0].clientX;
    y0 = e.changedTouches[0].clientY;
  }, { passive: true });
  stage.addEventListener("touchend", function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    var dy = e.changedTouches[0].clientY - y0;
    // Horizontal enough to be a swipe rather than the start of a scroll.
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      go(at + (dx < 0 ? 1 : -1));
    }
    x0 = y0 = null;
  }, { passive: true });

  // Fetch the rest only once the page itself has finished arriving.
  function loadRest() {
    slides.forEach(function (s) {
      var img = s.querySelector("img[data-src]");
      if (!img) return;
      if (img.dataset.srcset) img.srcset = img.dataset.srcset;
      img.src = img.dataset.src;
      img.removeAttribute("data-src");
      img.removeAttribute("data-srcset");
    });
    play();
  }
  if (document.readyState === "complete") loadRest();
  else addEventListener("load", loadRest);

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else play();
  });
  still.addEventListener("change", function () { still.matches ? stop() : play(); });
})();
