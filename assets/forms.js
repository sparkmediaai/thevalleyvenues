/**
 * The inquiry forms.
 *
 * These post straight to the GoHighLevel webhook from the browser. That was a
 * deliberate decision, taken against the CRM spec's own advice, and it has two
 * consequences worth knowing when reading this file:
 *
 *   The webhook URL is in the page. It is the endpoint's only authentication
 *   and GHL bills Inbound Webhook per execution, so the honeypot below is not
 *   decoration -- it is the only thing between a scraper and the invoice.
 *
 *   There is no server to validate against, so every rule the CRM depends on
 *   has to be enforced here. GHL accepts a wrong value without complaint and
 *   files the contact wrongly, which means a mistake in this file surfaces as
 *   a planner receiving bridal emails a week later rather than as an error.
 *
 * Two rules from the spec drive most of it.
 *
 *   Key names are matched exactly, so every input's `name` is already the key
 *   the CRM wants and nothing here renames anything.
 *
 *   Option values are compared character for character. "planner" is not
 *   "Planner"; "Yes" is not true. EXACT below is the whole allowlist, and a
 *   value that is not in it is dropped rather than sent, because an empty
 *   field in the CRM is at least visible and a wrong one is not.
 *
 * Verified 10 Sep 2026: the endpoint answers a preflight with
 * Access-Control-Allow-Origin: *, so this runs in normal cors mode and the
 * response is readable. That is what lets a failure show the visitor an email
 * address instead of silently losing what they wrote.
 */
(function () {
  "use strict";

  var MAILTO = "Info@thevalleyvenues.com";
  var LOADED_AT = Date.now();

  // Straight from the CRM spec. Character for character.
  var EXACT = {
    inquiry_type: ["Pricing Pamphlet", "Couple", "Planner", "Other"],
    season: ["Spring", "Summer", "Fall", "Winter", "Not sure"],
    date_flexible: ["Yes", "No"],
    experience_type: ["Estate Weekend", "Single Day", "Undecided"],
    lodging_interest: ["Yes", "No"],
    referral_source: ["Instagram", "TikTok", "Google", "Planner referral",
                      "Past couple", "Wedding site", "Other"],
    working_with_planner: ["Yes", "No", "Looking for one"],
    // Plain hyphens, matching the option values rather than the labels. See the
    // note on the select in build.py: the en dash is display only.
    estimated_venue_budget: ["Under $15,000", "$15,000-$25,000", "$25,000-$40,000",
                             "$40,000-$60,000", "$60,000-$100,000", "$100,000+",
                             "Not sure yet"],
  };

  /* Where they came from, remembered from the first page they landed on.
     Somebody who arrives from an ad and then reads three pages before asking
     for the pamphlet is still that ad's lead, so the first values win and
     later pages cannot overwrite them. Session storage rather than local:
     attribution belongs to this visit, not to this browser forever.

     Only ever sent when present, which is why the sample payload that
     registers these keys with the CRM has to carry all of them at once. */
  var TRACK = ["utm_source", "utm_campaign", "utm_ad"];
  // utm_content is what most ad platforms actually emit; it lands on utm_ad.
  var FROM = { utm_source: "utm_source", utm_campaign: "utm_campaign",
               utm_ad: "utm_ad", utm_content: "utm_ad" };

  function attribution() {
    var store = {};
    try { store = JSON.parse(sessionStorage.getItem("vv_attr") || "{}"); } catch (e) {}
    var q, dirty = false;
    try { q = new URLSearchParams(location.search); } catch (e) { return store; }
    Object.keys(FROM).forEach(function (param) {
      var key = FROM[param], v = q.get(param);
      // First touch wins: an explicit utm_ad is not overwritten by utm_content,
      // and a later page cannot overwrite the page they arrived on.
      if (v && !store[key]) { store[key] = v.toLowerCase().slice(0, 200); dirty = true; }
    });
    if (dirty) {
      try { sessionStorage.setItem("vv_attr", JSON.stringify(store)); } catch (e) {}
    }
    return store;
  }

  // Run on every page, not only the one with the form on it.
  attribution();

  function el(id) { return document.getElementById(id); }
  function fieldOf(input) { return input.closest(".field") || input.parentNode; }

  function setBad(field, message) {
    field.classList.add("is-bad");
    var p = field.querySelector(".field-msg");
    if (!p) {
      p = document.createElement("p");
      p.className = "field-msg";
      field.appendChild(p);
    }
    p.textContent = message;
  }

  function clearBad(form) {
    form.querySelectorAll(".field.is-bad").forEach(function (f) {
      f.classList.remove("is-bad");
      var p = f.querySelector(".field-msg");
      if (p) p.remove();
    });
  }

  /* North American numbers arrive in every shape a person can type one, and
     the CRM wants E.164. Anything already international is left alone. */
  function e164(raw) {
    var d = String(raw).replace(/\D/g, "");
    if (d.length === 10) return "+1" + d;
    if (d.length === 11 && d.charAt(0) === "1") return "+" + d;
    return "+" + d;
  }

  /* The CRM only starts Kobi's sequence for an inquiry that has an experience
     type AND either a date or a season. Anything short of that is filed
     not-yet-qualified and sits in the pipeline unworked, so the form asks
     rather than letting somebody skip both and never hear back. */
  function validate(form) {
    clearBad(form);
    var bad = null;

    form.querySelectorAll("[required]").forEach(function (input) {
      if (!input.value.trim()) {
        setBad(fieldOf(input), "This one we do need.");
        bad = bad || input;
      }
    });

    var email = form.elements.email;
    if (email && email.value.trim() &&
        !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim())) {
      setBad(fieldOf(email), "That does not look like an email address.");
      bad = bad || email;
    }

    var date = form.elements.event_date;
    var season = form.elements.season;
    if (date && season && !date.value && !season.value) {
      setBad(fieldOf(season), "A date or a season — either is enough.");
      bad = bad || season;
    }
    return bad;
  }

  function payload(form) {
    var out = { inquiry_type: form.dataset.inquiryType };

    Array.prototype.forEach.call(form.elements, function (input) {
      var key = input.name;
      // `company` is the honeypot and never leaves the browser.
      if (!key || key === "company" || input.type === "submit") return;
      var value = (input.value || "").trim();

      // The brief is explicit: send an empty string rather than leaving the
      // key out. A workflow can test a blank; it cannot test a key that is
      // not there, and the trigger only ever learns keys it has actually seen.
      if (!value) { out[key] = ""; return; }

      if (key === "guest_count") {
        // A JSON number, not a quoted string. Quoted, the CRM field stays
        // empty and says nothing about why.
        var n = parseInt(value, 10);
        out.guest_count = (!isNaN(n) && n >= 0) ? n : "";
        return;
      }

      if (key === "phone") { out.phone = e164(value); return; }

      if (EXACT[key]) {
        if (EXACT[key].indexOf(value) === -1) {
          // Only reachable if the markup and this list have drifted apart.
          // Blanking it leaves the CRM field empty; sending it would file the
          // contact wrongly and tell nobody.
          if (window.console) console.warn("blanking " + key + "=" + value +
            " — not one of: " + EXACT[key].join(", "));
          out[key] = "";
          return;
        }
        out[key] = value;
        return;
      }

      out[key] = value;
    });

    // Always present, blank when the visit carried no campaign.
    var from = attribution();
    TRACK.forEach(function (k) { out[k] = from[k] || ""; });

    // The full URL, per the brief. On the prototype that means ?notes can
    // reach the CRM; it is a prototype-only toggle and goes before launch.
    out.page_url = location.href;
    out.submitted_at = new Date().toISOString();
    return out;
  }

  function fail(form, box, button, message) {
    box.hidden = false;
    box.innerHTML = message +
      ' Please email <a href="mailto:' + MAILTO + '">' + MAILTO + "</a>" +
      " and it will reach the same person.";
    form.classList.remove("is-sending");
    if (button) { button.disabled = false; button.textContent = button.dataset.label; }
  }

  function succeed(form, done) {
    form.hidden = true;
    done.hidden = false;
    done.setAttribute("tabindex", "-1");
    done.focus();
  }

  function wire(form) {
    var box = el(form.id + "-error");
    var done = el(form.id + "-done");
    var button = form.querySelector('button[type="submit"]');
    if (button) button.dataset.label = button.textContent;

    // The studio name is only worth asking for once somebody says yes.
    var planner = form.elements.working_with_planner;
    var plannerField = el("planner-name-field");
    if (planner && plannerField) {
      planner.addEventListener("change", function () {
        plannerField.hidden = planner.value !== "Yes";
        if (plannerField.hidden && form.elements.planner_name) {
          form.elements.planner_name.value = "";
        }
      });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      box.hidden = true;

      // A field no person can see and no person will fill in. Nothing is
      // posted, and the visitor -- which is to say the bot -- is shown the
      // same thank-you as everyone else. Telling it that it failed only
      // teaches it to try again differently, and every post that does go
      // through is billable.
      var hp = form.elements.company;
      if (hp && hp.value.trim() !== "") {
        succeed(form, done);
        return;
      }

      // Nobody reads four fields and fills them in inside two seconds. A bot
      // does. Same silent fake success as the honeypot: telling it that it
      // failed only teaches it to wait, and every post that does go through
      // is billable.
      if (Date.now() - LOADED_AT < 2000) {
        succeed(form, done);
        return;
      }

      var bad = validate(form);
      if (bad) { bad.focus(); return; }

      var endpoint = window.FORM_ENDPOINT;
      if (!endpoint) {
        fail(form, box, button,
             "This form is not connected to anything yet — it is a prototype.");
        return;
      }

      form.classList.add("is-sending");
      if (button) { button.disabled = true; button.textContent = "Sending…"; }

      var body = JSON.stringify(payload(form));

      // A 5xx is the endpoint having a moment; a 4xx is us, and repeating it
      // only bills the account twice for the same mistake.
      function post(attempt) {
        return fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // The endpoint answers with Access-Control-Allow-Origin: * AND
          // Access-Control-Allow-Credentials: true, which a browser refuses to
          // accept together if credentials are in play. Omitting them keeps the
          // response readable, which is what makes the failure branch work.
          credentials: "omit",
          body: body,
        }).then(function (res) {
          if (res.status >= 500 && attempt === 1) return post(2);
          return res;
        });
      }

      post(1).then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        succeed(form, done);
      }).catch(function () {
        // Never swallow it. Somebody has just typed out what they want their
        // wedding to feel like; losing that silently is the worst thing this
        // page could do.
        fail(form, box, button, "Something went wrong sending that.");
      });
    });
  }

  document.querySelectorAll("form.inquiry").forEach(wire);
})();
