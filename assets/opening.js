/* The opening band.

   One announcement with an expiry. The two instants on the element are UTC,
   because 4pm EDT is 20:00Z and a browser in Denver has to count to the same
   moment rather than to four o'clock wherever it happens to be.

   Three states and the third is the one that matters:

     before  days, hours, minutes and seconds to the doors opening
     during  it says so, and stops counting
     after   the band removes itself

   A countdown that has gone negative is worse than no countdown, and a grand
   opening still being advertised in October says more about the agency than it
   does about the estate. Nobody is going to remember to take this down, so it
   takes itself down.

   The blocks are built once and only their digits are written afterwards.
   Rebuilding the row every second would throw away any text selection, and it
   would also mean the browser could never animate a digit, because the element
   it was animating no longer existed a moment later.

   It sleeps while the tab is hidden. A one-second timer nobody is looking at is
   just a battery charge. */
(function () {
  var band = document.getElementById("opening");
  if (!band) return;

  var out = band.querySelector(".opening-count");
  var until = Date.parse(band.getAttribute("data-until"));
  var through = Date.parse(band.getAttribute("data-through"));
  if (!out || isNaN(until) || isNaN(through)) return;

  var MIN = 60000, HOUR = 60 * MIN, DAY = 24 * HOUR;
  var still = matchMedia("(prefers-reduced-motion: reduce)");
  var timer = null, cells = null;

  function build(keys) {
    out.className = "opening-count";
    out.textContent = "";
    cells = {};
    keys.forEach(function (k) {
      var wrap = document.createElement("span");
      wrap.className = "opening-unit";
      var n = document.createElement("b");
      var label = document.createElement("span");
      label.textContent = k === "sec" ? "sec" : k;
      wrap.appendChild(n);
      wrap.appendChild(label);
      out.appendChild(wrap);
      cells[k] = n;
    });
  }

  function put(key, value) {
    var cell = cells[key];
    if (!cell || cell.textContent === value) return;
    cell.textContent = value;
    // The lift is what separates a clock running from a number being swapped.
    if (!still.matches && cell.animate) {
      cell.animate(
        [{ opacity: 0.25, transform: "translateY(0.16em)" }, { opacity: 1, transform: "none" }],
        { duration: 420, easing: "cubic-bezier(.16,.8,.24,1)" }
      );
    }
  }

  function pad(n) { return n < 10 ? "0" + n : "" + n; }

  function tick() {
    var now = Date.now();

    if (now >= through) {                 // it has been and gone
      band.remove();
      if (timer) clearInterval(timer);
      return;
    }
    if (until - now <= 0) {               // the doors are open
      if (timer) { clearInterval(timer); timer = null; }
      out.className = "opening-count is-now";
      out.textContent = "Happening now";
      cells = null;
      return;
    }

    var left = until - now;
    var d = Math.floor(left / DAY);
    var h = Math.floor((left % DAY) / HOUR);
    var m = Math.floor((left % HOUR) / MIN);
    var sec = Math.floor((left % MIN) / 1000);

    var keys = d ? ["days", "hours", "min", "sec"] : ["hours", "min", "sec"];
    // Rebuild only when the shape changes -- which is once, as days runs out.
    if (!cells || Object.keys(cells).length !== keys.length) build(keys);

    if (d) put("days", String(d));
    put("hours", pad(h));
    put("min", pad(m));
    put("sec", pad(sec));
  }

  function run() {
    if (timer) clearInterval(timer);
    timer = null;
    tick();
    if (document.getElementById("opening") && !document.hidden && until - Date.now() > 0) {
      timer = setInterval(tick, 1000);
    }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { if (timer) { clearInterval(timer); timer = null; } }
    else run();
  });

  run();
})();
