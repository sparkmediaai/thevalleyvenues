# The inquiry worker — NOT IN USE

> **The forms do not post here.** On 10 Sep 2026 the decision was taken to post
> client-side, straight to GoHighLevel, and not to rotate the webhook URL. The
> rules below now live in `assets/forms.js` instead, and the GHL URL sits in
> `_build/build.py` and therefore in this public repo.
>
> This is kept, deployed nowhere, because it is written and tested and the
> reasons for it have not gone away: that URL is the endpoint's only
> authentication and GHL bills per execution. If spam starts costing money,
> deploying this and swapping `FORM_ENDPOINT` is an hour's work.

The site is static — GitHub Pages serves files and runs nothing — so there is
no server for the forms to post through. This is that server: forty lines on
Cloudflare Workers, which is free at this volume.

It exists because the GHL spec says the webhook URL must not be posted from the
browser. That is not fussiness. The URL **is** the authentication, GHL bills
Inbound Webhook per execution, and a URL in page source is a URL anyone can
point a script at.

## Deploy

```
cd _worker
npx wrangler login
npx wrangler secret put GHL_WEBHOOK_URL     # paste the hooks.leadconnectorhq.com URL
npx wrangler deploy
```

`wrangler deploy` prints the worker's URL. Put that in `_build/build.py` as
`FORM_ENDPOINT`, rebuild, and push.

The webhook URL is a **secret**, set with `wrangler secret put`. It is not in
`wrangler.toml`, it is not in this repo, and it must not be — this repo is
public.

## What it does beyond forwarding

- **Rejects wrong dropdown values.** The spec's Rule 2 is that GHL compares
  these character for character and a wrong one fails *silently* — send
  `"planner"` instead of `"Planner"` and every planner is routed into the
  couples pipeline with nobody the wiser. A silent failure in a CRM is worse
  than a loud one on a form, so the allowlists live in `src/index.js` and a bad
  value gets a 400.
- **Drops unknown keys.** GHL maps on exact key names it learned from one
  sample payload; keys it has not seen do nothing.
- **Swallows honeypot hits** with a 200 and no forward. Telling a bot it failed
  only teaches it to try again differently.
- **Normalises the phone** to E.164 and **sets `submitted_at`** itself, rather
  than trusting a browser clock.
- **Reports failure honestly** with a 502, so the page can offer an email
  address instead of pretending the inquiry landed.

## Rate limiting

Not in code. Cloudflare's own rate limiting rules are the right place —
dashboard → the worker's route → Security → Rate limiting. Something like 5
requests per minute per IP is generous for a wedding inquiry form and closes
the "spam costs money" hole the spec warns about.

## Tests

```
node _worker/test.mjs
```

Thirteen checks, no deploy and no network — Node has `fetch`, `Request` and
`Response`, which is everything the worker touches, so it runs as-is with the
outbound call stubbed. Four of them are the exact bugs the CRM spec found in
the original sample payload: `"planner"` lowercase, `"estate_weekend"`,
booleans for `date_flexible`, and a quoted `guest_count`. Each must be
**rejected or corrected, never forwarded** — GHL accepts a wrong value and
mis-files the contact without erroring.

## Testing against the real CRM

```
curl -X POST https://<worker>.workers.dev \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://thevalley.sparkmedia.ai' \
  -d '{"inquiry_type":"Planner","email":"you@example.com","first_name":"Test"}'
```

Then check GHL: the contact should carry `audience-planner` and there should be
**no opportunity**. Per the spec that is the single best check that the exact
string handling is right — a planner leaking into the Weddings pipeline is what
the lowercase bug used to cause.
