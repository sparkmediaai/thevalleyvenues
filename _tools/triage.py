"""
Sort a large, uncategorised photography library into what is usable and what is not.

The problem with 2,400 images is not that they are unsorted. It is that most of
them are not candidates: burst frames three-quarters identical to the one beside
them, focus misses, test frames, and work from before the property changed. Look
at them one by one and you spend a day to find two hundred.

So this makes two passes. This script is the first, and it needs no judgement:

  Too small        Under 800px on the long edge is not usable anywhere. Above that,
                   size is not pass/fail but a ceiling: what the frame can be used
                   for. A 1024px file is no good as a hero and perfectly good in a
                   card, and throwing it away would be wrong.
  Soft             Variance of edge energy on a fixed-size crop, so a 6000px file
                   and a 1200px file are scored on the same footing.
  Blown or crushed Clipped highlights or dead shadows past a threshold.
  Duplicate        A perceptual hash groups near-identical frames; the sharpest of
                   each burst survives and the rest are set aside, not deleted.
  Stale            EXIF capture date older than a cutoff. The brand direction is
                   explicit that work predating the rebuild no longer describes
                   the property.

What survives gets a thumbnail, a score, and a shoot number derived from EXIF
timestamps — frames taken within six hours of each other are one session, which
is usually also one location and one light. Then review.html does the second
pass, which does need judgement, at about a second an image.

    python _tools/triage.py "D:/path/to/photos" --out "D:/triage"

Nothing is moved, renamed or deleted. The originals are read and closed.
"""
import argparse, json, os, sys
from datetime import datetime, timedelta

try:
    from PIL import Image, ImageFilter, ImageStat, ExifTags
except ImportError:
    sys.exit("Pillow is required:  pip install pillow")

Image.MAX_IMAGE_PIXELS = None

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic", ".heif")

# The categories the site actually has slots for, from the sitemap. Kept short:
# a tagging pass slows down badly past a dozen choices.
CATEGORIES = [
    "Mountain & landscape", "The Valley", "Magnolia House", "Lookout Deck",
    "Davis Hall", "Lodging & cottages", "Arrival & the drive", "Details & decor",
    "People & candid", "Getting ready", "Food & catering", "Winter & off-season",
]

MIN_LONG_EDGE = 800         # below this it is not usable anywhere
# What a given size can actually carry on the page, largest first.
USE_TIERS = [(2400, "hero"), (1600, "section"), (1000, "card"), (MIN_LONG_EDGE, "thumb")]
DUP_DISTANCE = 6            # hamming distance on a 64-bit hash
SHOOT_GAP_HOURS = 6
THUMB = 400


# ----------------------------------------------------------------- measuring
def dhash(im):
    """64-bit difference hash. Near-identical frames land within a few bits."""
    g = im.convert("L").resize((9, 8), Image.LANCZOS)
    px = g.load()
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (1 if px[x, y] > px[x + 1, y] else 0)
    return bits


def popcount(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c


def measure(im):
    """Sharpness and exposure, both on a fixed-size crop so sizes compare."""
    g = im.convert("L")
    r = 512.0 / max(g.size)
    if r < 1:
        g = g.resize((max(1, int(g.width * r)), max(1, int(g.height * r))), Image.BILINEAR)
    w, h = g.size
    side = min(400, w, h)
    left, top = (w - side) // 2, (h - side) // 2
    crop = g.crop((left, top, left + side, top + side))

    edges = crop.filter(ImageFilter.FIND_EDGES)
    sharp = ImageStat.Stat(edges).stddev[0]

    st = ImageStat.Stat(crop)
    mean = st.mean[0] / 255.0
    hist = crop.histogram()
    total = float(sum(hist)) or 1.0
    blown = sum(hist[250:]) / total
    crushed = sum(hist[:6]) / total
    return sharp, mean, blown, crushed


def exif_of(im):
    out = {}
    try:
        raw = im.getexif()
    except Exception:
        return out
    if not raw:
        return out
    names = {v: k for k, v in ExifTags.TAGS.items()}
    for key in ("DateTimeOriginal", "DateTime", "Make", "Model", "ISOSpeedRatings",
                "FNumber", "FocalLength"):
        tag = names.get(key)
        if tag and tag in raw:
            out[key] = raw[tag]
    # DateTimeOriginal lives in the Exif IFD on most cameras
    try:
        sub = raw.get_ifd(0x8769)
        tag = names.get("DateTimeOriginal")
        if tag and tag in sub:
            out["DateTimeOriginal"] = sub[tag]
    except Exception:
        pass
    return out


def parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(s).strip()[:19], fmt)
        except ValueError:
            continue
    return None


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default=None,
                    help="where thumbnails and the review page are written "
                         "(default: <folder>/_triage). Keep this out of the repo.")
    ap.add_argument("--stale-before", default=None,
                    help="flag captures older than this, e.g. 2025-01-01")
    ap.add_argument("--limit", type=int, default=0, help="stop after N files (for a trial run)")
    args = ap.parse_args()

    src = os.path.abspath(args.folder)
    out = os.path.abspath(args.out or os.path.join(src, "_triage"))
    thumbs = os.path.join(out, "thumbs")
    os.makedirs(thumbs, exist_ok=True)
    stale_before = parse_dt(args.stale_before + " 00:00:00") if args.stale_before else None

    files = []
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if not d.startswith(("_triage", ".", "__"))]
        for f in sorted(filenames):
            if f.lower().endswith(EXTS) and not f.startswith("."):
                files.append(os.path.join(dirpath, f))
    if args.limit:
        files = files[:args.limit]
    print("%d images found under %s" % (len(files), src))
    if not files:
        return

    rows = []
    for i, path in enumerate(files, 1):
        if i % 100 == 0 or i == len(files):
            print("  %d/%d" % (i, len(files)))
        try:
            im = Image.open(path)
            w, h = im.size
            ex = exif_of(im)
            # Decode at reduced size where the format allows it. On 2,400 large
            # JPEGs this is the difference between minutes and most of an hour.
            im.draft("L", (640, 640))
            im = im.convert("RGB")
        except Exception as e:
            rows.append(dict(path=path, name=os.path.basename(path), verdict="unreadable",
                             why=str(e)[:80], w=0, h=0))
            continue

        sharp, mean, blown, crushed = measure(im)
        hsh = dhash(im)
        shot = parse_dt(ex.get("DateTimeOriginal") or ex.get("DateTime"))
        if shot is None:
            try:
                shot = datetime.fromtimestamp(os.path.getmtime(path))
            except Exception:
                shot = None

        long_edge = max(w, h)
        rows.append(dict(
            path=path, name=os.path.basename(path),
            rel=os.path.relpath(path, src).replace("\\", "/"),
            w=w, h=h, long_edge=long_edge,
            portrait=h > w,
            mp=round(w * h / 1e6, 1),
            use=next((name for edge, name in USE_TIERS if long_edge >= edge), "too small"),
            sharp=round(sharp, 2), mean=round(mean, 3),
            blown=round(blown, 4), crushed=round(crushed, 4),
            hash=hsh, shot=shot.isoformat() if shot else None,
            camera=(" ".join(str(ex.get(k, "")) for k in ("Make", "Model"))).strip(),
            verdict=None, why="", shoot=None, dup_of=None, cat=None,
        ))
        try:
            im.close()
        except Exception:
            pass

    ok = [r for r in rows if r["verdict"] != "unreadable"]

    # Soft is relative as well as absolute: a whole library shot at f/1.4 would
    # otherwise fail an absolute floor, and a crisp library would pass everything.
    sharps = sorted(r["sharp"] for r in ok)
    soft_cut = sharps[int(len(sharps) * 0.12)] if sharps else 0

    for r in ok:
        if r["long_edge"] < MIN_LONG_EDGE:
            r["verdict"], r["why"] = "too-small", "%dpx long edge" % r["long_edge"]
        elif r["sharp"] <= soft_cut and r["sharp"] < 18:
            r["verdict"], r["why"] = "soft", "edge energy %.1f" % r["sharp"]
        elif r["blown"] > 0.12:
            r["verdict"], r["why"] = "blown", "%.0f%% clipped" % (r["blown"] * 100)
        elif r["crushed"] > 0.30:
            r["verdict"], r["why"] = "dark", "%.0f%% black" % (r["crushed"] * 100)
        elif stale_before and r["shot"] and parse_dt(r["shot"].replace("T", " ")) < stale_before:
            r["verdict"], r["why"] = "stale", "shot %s" % r["shot"][:10]
        else:
            r["verdict"] = "keep"

    # Near-duplicates: keep the sharpest of each burst, set the rest aside.
    keepers = [r for r in ok if r["verdict"] == "keep"]
    keepers.sort(key=lambda r: -r["sharp"])
    survivors = []
    for r in keepers:
        twin = next((s for s in survivors if popcount(s["hash"] ^ r["hash"]) <= DUP_DISTANCE), None)
        if twin:
            r["verdict"], r["why"], r["dup_of"] = "duplicate", "near-match", twin["name"]
        else:
            survivors.append(r)

    # Shoots, from capture time. A gap of six hours is a different session, which
    # is usually a different location and a different light.
    dated = sorted([r for r in ok if r["shot"]], key=lambda r: r["shot"])
    n, last = 0, None
    for r in dated:
        t = parse_dt(r["shot"].replace("T", " "))
        if last is None or (t - last) > timedelta(hours=SHOOT_GAP_HOURS):
            n += 1
        r["shoot"], last = n, t

    # Thumbnails, for what survived only — 2,400 thumbnails is 40MB nobody needs.
    print("writing %d thumbnails" % len(survivors))
    for i, r in enumerate(survivors, 1):
        if i % 100 == 0:
            print("  %d/%d" % (i, len(survivors)))
        dest = os.path.join(thumbs, "%05d.webp" % i)
        try:
            im = Image.open(r["path"])
            im.draft("RGB", (THUMB * 2, THUMB * 2))
            im = im.convert("RGB")
            im.thumbnail((THUMB, THUMB), Image.LANCZOS)
            im.save(dest, quality=72, method=4)
            r["thumb"] = "thumbs/%05d.webp" % i
            im.close()
        except Exception:
            r["thumb"] = None

    for r in rows:
        r.pop("hash", None)
    payload = dict(
        source=src, generated=datetime.now().isoformat(timespec="seconds"),
        categories=CATEGORIES, tiers=[t[1] for t in USE_TIERS],
        rows=sorted(rows, key=lambda r: (r.get("shoot") or 999, r.get("name") or "")),
    )
    with open(os.path.join(out, "data.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "review.html"), encoding="utf-8") as f:
        review = f.read()
    with open(os.path.join(out, "review.html"), "w", encoding="utf-8") as f:
        f.write(review)

    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n  %-12s %s" % ("verdict", "count"))
    for k in sorted(tally, key=lambda k: -tally[k]):
        print("  %-12s %d" % (k, tally[k]))
    print("\n  %d to review" % len(survivors))
    for edge, name in USE_TIERS:
        n_tier = sum(1 for r in survivors if r["use"] == name)
        if n_tier:
            print("    %-8s %4d   (%dpx long edge and up)" % (name, n_tier, edge))
    print("\n  shoots detected: %d" % n)
    print("\n  open %s" % os.path.join(out, "review.html"))


if __name__ == "__main__":
    main()
