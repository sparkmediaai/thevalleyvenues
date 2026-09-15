/* The phone menu.

   Under 861px the header is the wordmark and a Menu button; the navigation
   opens as a panel beneath it. Without this script the button never appears
   (it is only shown under .js) and the navigation stays listed in the header,
   as it always was. Escape, a tap outside, or following a link closes it. */
(function () {
  var head = document.querySelector(".site-head");
  var btn = head && head.querySelector(".nav-toggle");
  var nav = head && head.querySelector(".site-nav");
  if (!btn || !nav) return;

  function set(open) {
    head.classList.toggle("nav-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.querySelector(".nav-word").textContent = open ? "Close" : "Menu";
  }
  btn.addEventListener("click", function () { set(!head.classList.contains("nav-open")); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && head.classList.contains("nav-open")) { set(false); btn.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (head.classList.contains("nav-open") && !head.contains(e.target)) set(false);
  });
  nav.addEventListener("click", function (e) { if (e.target.closest("a")) set(false); });
  matchMedia("(min-width: 861px)").addEventListener("change", function (m) { if (m.matches) set(false); });

  // Other scripts (the gallery's sticky bar) read the header's height.
  function measure() { document.documentElement.style.setProperty("--head", head.offsetHeight + "px"); }
  measure();
  addEventListener("resize", measure);
})();
