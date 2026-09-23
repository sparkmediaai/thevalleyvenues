# The Valley Venues

Prototype site for The Valley Venues — a 74-acre private wedding and events
estate at 1860 Pope Creek Rd, Wildwood, Georgia, fifteen minutes from
Chattanooga beneath Lookout Mountain. Built by SparkMedia.

**Live:** https://thevalley.sparkmedia.ai
**Working notes:** add `?notes` to any page — e.g. `/about/?notes`

Every page carries `noindex,nofollow`. That comes off when the client signs
off, not before: a prototype indexed on a real domain competes with their live
site in search results.

## The Instagram strip

The home page can carry the estate's own latest posts, above the closing call
to action. They are pulled once a day by `.github/workflows/instagram.yml`,
which runs `_tools/instagram.py`: the pictures are cut to a square and saved
into the repo like any other photograph, and the page renders them in the
site's own type. No embed script, no third-party cookies, nothing to slow a
page down.

It is dormant until the account is connected. With no feed file the section
does not render at all, and it hides itself again if the newest post is more
than seventy-five days old -- a quiet feed reads worse than none.

To turn it on, set these as repository secrets (Settings -> Secrets and
variables -> Actions):

| Secret        | What it is                                                        |
| ------------- | ----------------------------------------------------------------- |
| `IG_TOKEN`    | A long-lived access token for @thevalleyvenues                     |
| `IG_USER_ID`  | Optional. `me` works for a token issued to the account itself      |
| `IG_API_BASE` | Optional. Set to `https://graph.facebook.com/v23.0` for a Page token |

Getting the token is a job on the client's side: their Instagram has to be a
Business or Creator account, a Meta app needs creating, and the token issued
from it. A token from Meta Business Manager's system user does not expire; a
plain long-lived token lasts sixty days and is renewed with
`python _tools/instagram.py refresh`.

## Pages are generated, not written

Twelve pages share one header, one footer and one set of stylesheets. Writing
them by hand would mean changing the navigation in twelve places the first time
it moves, and it will move — the structure is a proposal, not a decision. So
the pages are data and the shell is code.

```
python _build/build.py
```

That reads the page table at the bottom of `_build/build.py` and writes the
HTML. Nothing else writes HTML; if you edit `index.html` directly the next
build discards it.

`_build/build.py` also holds the only two facts about where the site lives:

```python
URL_ROOT = "/"                                 # what internal links point at
BASE = "https://thevalley.sparkmedia.ai/"      # absolute origin, for og: tags
```

Pointing thevalleyvenues.com here is one command:

```
python _build/set_domain.py thevalleyvenues.com
```

which changes `BASE` and `CNAME` together, rebuilds and link-checks. Getting
one and not the other gives you a site that works but previews under its old
name in every message anybody pastes it into. Nothing in any stylesheet knows
the site's address.

## The other generators

| | |
|---|---|
| `_build/make_plan.py` | Draws `assets/plan.svg` — the contour plan on The Estate page — by walking marching squares through `terrain/terrain.png`. Also cuts `assets/favicon.svg` from the three closed contours around the estate's high ground. |
| `_build/make_social.py` | `assets/og.jpg` (the social preview card) and `assets/icon-180.png`. |
| `_tools/place.py` | Cuts every photograph on the site from the sorted library. Each slot on the site has a job — a hero, a band, a card — and a job implies a width and an aspect, so the slots are listed in one table and rebuilt from the originals in one pass. |
| `_tools/catsheet.py` | A contact sheet for one category of the sorted library, for choosing frames. |
| `_tools/triage.py`, `sort.py`, `sheets.py` | The one-time pass that sorted 2,472 uncategorised images into the library. |
| `_tools/linkcheck.py` | Resolves every internal href, src, srcset and CSS url() against the filesystem. Run it after a build and always after moving the site. |
| `_build/set_domain.py` | Moves the site to a new hostname — changes `BASE` and `CNAME` together, rebuilds, and link-checks. `python _build/set_domain.py thevalleyvenues.com` |

### The photograph library is not in this repo

`_tools/place.py` reads from `D:/DevStuff/VV Images/Sorted`, which is the
client's photography sorted into twelve categories by orientation. It is
several gigabytes and it is not ours to publish, so it stays off GitHub. Only
the cut, resized frames in `assets/img/` are committed.

If you do not have that drive, everything except `place.py` still runs — the
site builds fine from the images already committed.

## Local preview

```
python -m http.server 8790
```

Then http://localhost:8790. The site is written for a domain root, so it will
not work served from a subdirectory.

## The inquiry forms

`/book-a-tour/` (couples) and `/planners/register/` (planners) post **straight
to the GoHighLevel webhook from the browser**. `FORM_ENDPOINT` in
`_build/build.py` holds that URL.

That was decided against the CRM spec's own advice, which says to post server
side. The consequence to keep in mind: the URL is the endpoint's only
authentication, GHL bills Inbound Webhook per execution, and this repo is
public — so the URL is not merely in page source, it is on GitHub, where
secret scrapers look first. **The honeypot in `assets/forms.js` is the only
thing between a scraper and the invoice; do not remove it.** `_worker/` holds
a written and tested Cloudflare worker that closes this, deployed nowhere, if
it is ever wanted.

Because there is no server, every rule the CRM depends on is enforced in
`assets/forms.js`: the exact option strings, `guest_count` as a number, phone
to E.164, `submitted_at` at submit. A value that is not on the allowlist is
dropped rather than sent — an empty CRM field is at least visible, a wrong one
is not. `node _worker/test.mjs` still exercises the same rule set.

The planner form also sends `planner_website` and `planner_social`. Those are
**new keys**, and GHL matches on key names it learned from one sample payload,
so the sample request has to be re-fetched in the workflow trigger or both
fields will arrive and go nowhere.

The couple form requires an experience type and either a date or a season,
because the CRM only starts Kobi's sequence when it has both — an inquiry
missing them is filed `not-yet-qualified` and sits unworked.

## What is still open

- The wordmark: "The Valley Venues" or "THE VALLEY".
- The published starting figure on `/weddings/`.
- Kobi's credentials, word for word, and a photograph of her — there is not one
  in the 2,472-image library, and it is the single most useful frame the next
  shoot could produce.
- Real weddings, credited, with the couples' permission. The gallery currently
  shows estate frames and says so.
- Place positions on the contour plan are read from aerial imagery rather than
  from a site plan, so the distances want confirming before anything is
  published that leans on them.
- `terrain/` is the interactive 3D model of the same survey. It works but it is
  not styled to match the rest of the site.
