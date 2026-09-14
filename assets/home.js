/* The hero film.

   A background film is only worth having if it never makes the page worse to
   arrive at, so:

   1. The still comes first. The poster is an ordinary image in the markup, and
      the video has no source until this script gives it one, after load. A
      phone gets the 720px cut; a wide screen gets WebM, or MP4 where WebM is
      not supported.
   2. It fades in only once it is really playing, so there is no black frame.
   3. It plays for everyone, reduced motion included -- the owner's call, since
      the film is the pitch. The pause button is the answer for anyone who
      wants it still, and it is always shown. With JavaScript off the still
      simply stays.
   4. It can be stopped. Anything that moves for more than five seconds needs a
      pause control, and the choice is remembered for the visit.
   5. It rests when nobody can see it: a hidden tab, or scrolled out of view. */
(function () {
  var stage = document.querySelector(".hero-stage");
  var video = stage && stage.querySelector(".hero-video");
  if (!video) return;
  var button = stage.querySelector(".hero-pause");
  var label = button && button.querySelector("span");
  var small = matchMedia("(max-width: 760px)");
  var visible = true, loaded = false;
  // Playing unless this visit has already pressed pause.
  var choice = null;
  try { choice = sessionStorage.getItem("vv_film"); } catch (e) {}
  var paused = choice === "paused";

  function source() {
    if (small.matches) return video.dataset.sm;
    return video.canPlayType('video/webm; codecs="vp9"') ? video.dataset.webm : video.dataset.mp4;
  }

  function load() {
    if (loaded) return;
    loaded = true;
    video.src = source();
    video.preload = "auto";
  }

  function wanted() { return !paused && visible && !document.hidden; }

  function sync() {
    if (button) {
      button.hidden = false;
      button.setAttribute("aria-pressed", paused ? "true" : "false");
      if (label) label.textContent = paused ? "Play film" : "Pause film";
    }
    if (wanted()) {
      load();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});   // autoplay refused: the still stays
    } else if (loaded) {
      video.pause();
    }
  }

  video.addEventListener("playing", function () { video.classList.add("is-on"); });

  if (button) {
    button.addEventListener("click", function () {
      paused = !paused;
      choice = paused ? "paused" : "playing";
      try { sessionStorage.setItem("vv_film", choice); } catch (e) {}
      sync();
    });
  }

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      sync();
    }).observe(stage);
  }

  document.addEventListener("visibilitychange", sync);

  if (document.readyState === "complete") sync();
  else addEventListener("load", sync);
})();
