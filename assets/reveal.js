/* The arrival.

   Things on a page arrive when they come into view: they play once, at their
   own pace, and stay. The first version scrubbed each reveal against the
   scroll position with a view timeline, which had two problems. Firefox and
   older Safari never enter that @supports block, so on those the site simply
   sat there; and on a fast scroll a scrubbed fade is over before it registers.

   The head script adds `io` to <html> before first paint when this can run,
   which is what lets the stylesheet hide anything. If this file never arrives
   the head script takes `io` off again after three seconds, so a failed fetch
   costs a moment, never the page. Nothing here runs under reduced motion. */
(function () {
  window.__reveal = true;
  var root = document.documentElement;
  if (!root.classList.contains("io")) return;

  // Observed one by one: each arrives when it does.
  var EACH = ".reveal, main .lede, main .card, main .split, main .step, main .note, " +
             "main .named li, main .form .field, main .statement, main .closing-body, " +
             "main .facts li, main .onward, .wk, .wipe";
  // Observed as a unit: the children stagger off the parent's arrival.
  var UNIT = ".rise-words, .nots, .gallery, .cluster, .band";

  var els = [].slice.call(document.querySelectorAll(EACH + ", " + UNIT));
  if (!els.length) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add("in");
      io.unobserve(en.target);
    });
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.01 });

  els.forEach(function (el) { io.observe(el); });

  // Printing: everything shown, whatever the scroll.
  addEventListener("beforeprint", function () {
    els.forEach(function (el) { el.classList.add("in"); });
  });
})();
