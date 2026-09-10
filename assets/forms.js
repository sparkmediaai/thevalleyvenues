/**
 * The inquiry forms.
 *
 * Builds the payload the CRM expects, checks it, and posts it to the worker in
 * _worker/ -- never to GoHighLevel directly. The GHL webhook URL is its own
 * authentication and GHL charges per execution, so it cannot appear in a page
 * anybody can view the source of.
 *
 * Two rules from the spec drive most of what is here.
 *
 *   Key names are matched exactly, so every input's `name` is already the key
 *   the CRM wants and this file does no renaming.
 *
 *   Dropdown values are compared character for character, so every <option> is
 *   spelled the way the CRM spells it. That is why the selects say "Estate
 *   Weekend" rather than something friendlier: a near miss does not error, it
 *   just quietly leaves the field empty, and a planner sent as "planner"
 *   instead of "Planner" lands in the couples pipeline and gets the couples
 *   emails.
 */
(function () {
  "use strict";

  var MAILTO = "Info@thevalleyvenues.com";

  function el(id) { return document.getElementById(id); }

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

  function fieldOf(input) {
    return input.closest(".field") || input.parentNode;
  }

  /* The CRM only starts Kobi's sequence for an inquiry that has an experience
     type AND either a date or a season. Anything short of that is filed as
     not-yet-qualified and sits in the pipeline unworked, so the form asks for
     them rather than letting somebody skip both and never hear back. */
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
      if (!key || key === "_hp" || input.type === "submit") return;
      var value = (input.value || "").trim();
      if (!value) return;

      if (key === "guest_count") {
        var n = parseInt(value, 10);
        // A JSON number, not a quoted string. Quoted, the CRM field stays
        // empty and says nothing about why.
        if (!isNaN(n)) out.guest_count = n;
        return;
      }
      out[key] = value;
    });

    // Not location.href: ?notes and any other query would end up in the CRM.
    out.page_url = location.origin + location.pathname;
    out.submitted_at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    var hp = form.elements._hp;
    if (hp && hp.value) out._hp = hp.value;
    return out;
  }

  function fail(form, box, message) {
    box.hidden = false;
    box.innerHTML = message +
      ' Please email <a href="mailto:' + MAILTO + '">' + MAILTO + "</a>" +
      " and it will reach the same person.";
    form.classList.remove("is-sending");
    var button = form.querySelector('button[type="submit"]');
    if (button) { button.disabled = false; button.textContent = button.dataset.label; }
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

      var bad = validate(form);
      if (bad) {
        bad.focus();
        return;
      }

      var endpoint = window.FORM_ENDPOINT;
      if (!endpoint) {
        fail(form, box,
             "This form is not connected to anything yet — it is a prototype.");
        return;
      }

      form.classList.add("is-sending");
      if (button) { button.disabled = true; button.textContent = "Sending…"; }

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload(form)),
      }).then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        form.hidden = true;
        done.hidden = false;
        done.setAttribute("tabindex", "-1");
        done.focus();
      }).catch(function () {
        // Never swallow it. Somebody has just typed out what they want their
        // wedding to feel like; losing that silently is the worst thing this
        // page could do.
        fail(form, box, "Something went wrong sending that.");
      });
    });
  }

  document.querySelectorAll("form.inquiry").forEach(wire);
})();
