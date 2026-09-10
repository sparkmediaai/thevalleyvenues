# The Valley Venues

Prototype site for The Valley Venues — a 74-acre private wedding and events
estate at 1860 Pope Creek Rd, Wildwood, Georgia, fifteen minutes from
Chattanooga beneath Lookout Mountain. Built by SparkMedia.

**Live:** https://thevalley.sparkmedia.ai
**Working notes:** add `?notes` to any page — e.g. `/about/?notes`

Every page carries `noindex,nofollow`. That comes off when the client signs
off, not before: a prototype indexed on a real domain competes with their live
site in search results.

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

`/book-a-tour/` (couples) and `/planners/register/` (planners) post to a
Cloudflare worker in `_worker/`, which forwards to GoHighLevel. They do **not**
post to GHL directly: the GHL webhook URL is its own authentication, GHL bills
per execution, and a URL in page source is a URL anyone can point a script at.

`FORM_ENDPOINT` in `_build/build.py` is the worker's address. While it is
empty the forms render and validate but tell the visitor to email instead —
they never fail silently.

Both forms follow the CRM spec exactly: snake_case keys it matches on by name,
dropdown values spelled the way it spells them, `guest_count` as a number, and
Yes/No as strings rather than booleans. `_worker/test.mjs` guards all of that.

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
