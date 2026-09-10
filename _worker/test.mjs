/**
 * The worker's rules, exercised without deploying anything.
 *
 * Node 18+ has fetch, Request and Response, which is all the worker touches,
 * so it runs here as-is with the outbound fetch stubbed. The point of these is
 * the spec's Rule 2: a wrong dropdown value must be REJECTED rather than
 * quietly forwarded, because GHL accepts it and mis-files the contact.
 */
import worker from "./src/index.js";

const ORIGIN = "https://thevalley.sparkmedia.ai";
const env = {
  GHL_WEBHOOK_URL: "https://ghl.invalid/hook",
  ALLOWED_ORIGINS: ORIGIN,
};

let forwarded = null;
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  forwarded = JSON.parse(opts.body);
  return new Response("{}", { status: 200 });
};

const post = (body, origin = ORIGIN) =>
  worker.fetch(new Request("https://w.invalid/", {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: origin },
    body: JSON.stringify(body),
  }), env);

const COUPLE = {
  first_name: "Hannah", last_name: "Reyes", email: "hannah.reyes@example.com",
  phone: "(423) 555-0147", inquiry_type: "Couple", event_date: "2027-10-16",
  season: "Fall", date_flexible: "Yes", guest_count: 120,
  experience_type: "Estate Weekend", lodging_interest: "Yes",
  feeling: "Warm and unhurried.", referral_source: "Instagram",
  working_with_planner: "No", page_url: "https://x/inquire",
};

let pass = 0, fail = 0;
async function check(name, fn) {
  forwarded = null;
  try { await fn(); console.log("  ok   " + name); pass++; }
  catch (e) { console.log("  FAIL " + name + "\n         " + e.message); fail++; }
}
const eq = (a, b, m) => { if (a !== b) throw new Error(`${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`); };

console.log("\nthe worker:");

await check("a good couple payload is forwarded", async () => {
  eq((await post(COUPLE)).status, 200, "status");
  eq(forwarded.inquiry_type, "Couple", "inquiry_type");
  eq(forwarded.guest_count, 120, "guest_count stays a number");
  eq(typeof forwarded.guest_count, "number", "guest_count type");
});

await check("phone is normalised to E.164", async () => {
  await post(COUPLE);
  eq(forwarded.phone, "+14235550147", "phone");
});

await check("submitted_at is set by the worker, not the browser", async () => {
  await post({ ...COUPLE, submitted_at: "not a time at all" });
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(forwarded.submitted_at))
    throw new Error("got " + forwarded.submitted_at);
});

await check('lowercase "planner" is REJECTED, not forwarded', async () => {
  const r = await post({ ...COUPLE, inquiry_type: "planner" });
  eq(r.status, 400, "status");
  eq(forwarded, null, "must not reach GHL");
});

await check('"estate_weekend" is REJECTED', async () => {
  eq((await post({ ...COUPLE, experience_type: "estate_weekend" })).status, 400, "status");
  eq(forwarded, null, "must not reach GHL");
});

await check("booleans for date_flexible are REJECTED", async () => {
  eq((await post({ ...COUPLE, date_flexible: true })).status, 400, "status");
  eq(forwarded, null, "must not reach GHL");
});

await check("a quoted guest_count is coerced to a number", async () => {
  await post({ ...COUPLE, guest_count: "120" });
  eq(forwarded.guest_count, 120, "guest_count");
});

await check("a planner payload keeps no wedding fields", async () => {
  await post({
    first_name: "Marisol", email: "m@okaforevents.com", inquiry_type: "Planner",
    planner_name: "Okafor Events", referral_source: "Planner referral",
  });
  eq(Object.keys(forwarded).sort().join(","),
     "email,first_name,inquiry_type,planner_name,referral_source,submitted_at", "keys");
});

await check("a honeypot hit gets 200 and is NOT forwarded", async () => {
  eq((await post({ ...COUPLE, _hp: "http://spam" })).status, 200, "status");
  eq(forwarded, null, "must not reach GHL");
});

await check("unknown keys are dropped", async () => {
  await post({ ...COUPLE, total_budget: "50000", guestCount: 9 });
  eq("total_budget" in forwarded, false, "total_budget");
  eq("guestCount" in forwarded, false, "guestCount");
});

await check("no email and no phone is rejected", async () => {
  const r = await post({ inquiry_type: "Couple", first_name: "X" });
  eq(r.status, 400, "status");
});

await check("another site's Origin is refused", async () => {
  eq((await post(COUPLE, "https://evil.example")).status, 403, "status");
  eq(forwarded, null, "must not reach GHL");
});

await check("GHL being down reports 502 rather than pretending", async () => {
  globalThis.fetch = async () => { throw new Error("connection refused"); };
  eq((await post(COUPLE)).status, 502, "status");
  globalThis.fetch = async (u, o) => { forwarded = JSON.parse(o.body); return new Response("{}", { status: 200 }); };
});

console.log(`\n${pass} passed, ${fail} failed\n`);
globalThis.fetch = realFetch;
process.exit(fail ? 1 : 0);
