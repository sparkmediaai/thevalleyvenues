/**
 * The bit of server the site does not otherwise have.
 *
 * The site is static: GitHub Pages serves files and runs nothing. The GHL spec
 * is explicit that the webhook URL must not be posted from the browser, because
 * the URL *is* the authentication -- anyone who views source can then post to
 * the CRM as often as they like, and GHL bills Inbound Webhook per execution.
 * So the form posts here instead, and this holds the URL as a secret.
 *
 * It does three other jobs worth having.
 *
 *   1. It enforces the exact strings. The spec's Rule 2 is that GHL compares
 *      dropdown values character for character and a wrong one fails silently
 *      -- "planner" instead of "Planner" routes every planner into the couples
 *      pipeline and nobody finds out. A silent failure in a CRM is worse than
 *      a loud one on a form, so a bad value is rejected here, at the door.
 *   2. It absorbs the spam that would otherwise cost money per submission.
 *   3. It never lets an inquiry vanish. If GHL is down the caller is told, so
 *      the page can offer an email address instead of swallowing the message.
 *
 * Deploy:  see ../README.md
 */

const GHL_TIMEOUT_MS = 8000;

// Straight from the spec. GHL matches these character for character.
const ENUMS = {
  inquiry_type: ["Couple", "Planner", "Other"],
  season: ["Spring", "Summer", "Fall", "Winter", "Not sure"],
  date_flexible: ["Yes", "No"],
  experience_type: ["Estate Weekend", "Single Day", "Undecided"],
  lodging_interest: ["Yes", "No"],
  referral_source: ["Instagram", "TikTok", "Google", "Planner referral",
                    "Past couple", "Wedding site", "Other"],
  working_with_planner: ["Yes", "No", "Looking for one"],
};

const STRINGS = ["first_name", "last_name", "email", "phone", "event_date",
                 "feeling", "planner_name", "page_url", "submitted_at"];

// Anything not in ENUMS or STRINGS or guest_count is dropped rather than
// forwarded. GHL built its field mapping from a fixed sample payload; keys it
// has never seen do nothing, and passing them through only makes a 1 MB limit
// easier to hit with junk.
const ALLOWED = new Set([...STRINGS, ...Object.keys(ENUMS), "guest_count"]);

const cors = (origin, allowed) => ({
  "Access-Control-Allow-Origin": allowed.includes(origin) ? origin : allowed[0],
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
  "Vary": "Origin",
});

const json = (body, status, headers) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });

export default {
  async fetch(request, env) {
    const allowed = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
    const origin = request.headers.get("Origin") || "";
    const head = cors(origin, allowed.length ? allowed : ["*"]);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: head });
    if (request.method !== "POST") return json({ error: "POST only" }, 405, head);
    if (allowed.length && !allowed.includes(origin)) {
      return json({ error: "origin not allowed" }, 403, head);
    }
    if (!env.GHL_WEBHOOK_URL) {
      return json({ error: "not configured" }, 500, head);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "expected JSON" }, 400, head);
    }
    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return json({ error: "expected a JSON object" }, 400, head);
    }

    // The honeypot is a field no person can see and no person will fill in.
    // A bot that fills it gets a 200 and nothing else: telling it that it
    // failed only teaches it to try again differently.
    if (typeof body._hp === "string" && body._hp.trim() !== "") {
      return json({ ok: true }, 200, head);
    }

    const out = {};
    const errors = [];

    for (const [key, value] of Object.entries(body)) {
      if (!ALLOWED.has(key)) continue;

      if (key === "guest_count") {
        if (value === "" || value === null || value === undefined) continue;
        const n = Number(value);
        // A quoted string here is the difference between a number in the CRM
        // and an empty field, and the spec is specific about it.
        if (!Number.isFinite(n) || n < 0 || n > 100000) {
          errors.push("guest_count must be a number");
        } else {
          out.guest_count = Math.round(n);
        }
        continue;
      }

      if (ENUMS[key]) {
        if (value === "" || value === null || value === undefined) continue;
        if (!ENUMS[key].includes(value)) {
          errors.push(`${key} must be one of: ${ENUMS[key].join(", ")}`);
        } else {
          out[key] = value;
        }
        continue;
      }

      if (typeof value === "string") {
        const v = value.trim();
        if (v) out[key] = v.slice(0, 5000);
      }
    }

    if (!out.email && !out.phone) errors.push("email or phone is required");
    if (out.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(out.email)) {
      errors.push("email does not look like an address");
    }
    if (!out.inquiry_type) errors.push("inquiry_type is required");
    if (errors.length) return json({ error: "invalid submission", errors }, 400, head);

    // North American numbers arrive in every shape a person can type one.
    // Anything already in international form is left alone.
    if (out.phone) {
      const digits = out.phone.replace(/[^\d+]/g, "");
      if (digits.startsWith("+")) out.phone = digits;
      else if (digits.length === 10) out.phone = "+1" + digits;
      else if (digits.length === 11 && digits.startsWith("1")) out.phone = "+" + digits;
      else out.phone = digits;
    }

    // Set here rather than trusted from the browser: a clock that is wrong or
    // a client that omits it should not put a wrong time in the CRM.
    out.submitted_at = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");

    const timeout = AbortSignal.timeout
      ? AbortSignal.timeout(GHL_TIMEOUT_MS)
      : undefined;

    let res;
    try {
      res = await fetch(env.GHL_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(out),
        signal: timeout,
      });
    } catch (e) {
      // The caller is told, so the page can show an email address instead of
      // pretending the inquiry landed.
      return json({ error: "could not reach the CRM", detail: String(e) }, 502, head);
    }

    if (!res.ok) {
      return json({ error: "the CRM rejected it", status: res.status }, 502, head);
    }
    return json({ ok: true }, 200, head);
  },
};
