/* The hero clock.

   Five frames from one day, crossfading. Three things this has to get right,
   and they are all about not making the page worse to arrive at:

   1. Only the first frame is fetched with the document. It is the largest thing
      the page paints, so the other four wait until load and then come in
      quietly. A hero that ships five 2200px images is a slow hero.
   2. It stops when the tab is hidden. Nobody needs a crossfade running in a
      background tab on a laptop battery.
   3. It never runs at all under prefers-reduced-motion, and with JavaScript off
      the first frame simply stays put. The page reads either way. */
(function () {
  var stage = document.querySelector(".hero-stage");
  if (!stage) return;

  var slides = [].slice.call(stage.querySelectorAll(".slide"));
  var dots = [].slice.call(stage.querySelectorAll(".hero-dots button"));
  var hour = stage.querySelector(".hero-hour span");
  if (slides.length < 2) return;

  var at = 0, timer = null;
  var HOLD = 6200;
  var still = matchMedia("(prefers-reduced-motion: reduce)");

  function show(next) {
    if (next === at) return;
    slides[at].classList.remove("is-on");
    at = (next + slides.length) % slides.length;
    slides[at].classList.add("is-on");
    if (hour) hour.textContent = slides[at].getAttribute("data-moment") || "";
    dots.forEach(function (d, i) {
      d.setAttribute("aria-current", i === at ? "true" : "false");
    });
  }

  function play() {
    stop();
    if (still.matches) return;
    timer = setInterval(function () { show(at + 1); }, HOLD);
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  dots.forEach(function (d, i) {
    d.addEventListener("click", function () { show(i); play(); });
  });

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
