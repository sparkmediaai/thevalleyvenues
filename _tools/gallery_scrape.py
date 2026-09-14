"""
The wedding gallery from the estate's current site, brought across.

    python _tools/gallery_scrape.py            # download originals, then build
    python _tools/gallery_scrape.py --build    # rebuild web sizes only

The current gallery at thevalleyvenues.com/wedding-gallery/ is an Elementor
gallery of 156 photographs in thirteen tabs, one per photographer. Both halves
of that matter: the photographs are the best selling the estate has, and every
one of them belongs to a named photographer, so the credit travels with the
picture.

Originals go to the photo library on D:, which never enters the repo. What the
site serves is built from them: a 1600px and a 640px WebP of each, plus
assets/gallery.json, which the gallery page reads.
"""
import concurrent.futures as cf
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "https://thevalleyvenues.com/wedding-gallery/"
LIBRARY = r"D:\DevStuff\VV Images\Gallery (from current site)"
WEB = os.path.join(ROOT, "assets", "gallery")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch(url, timeout=90):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def original(url):
    """Photon CDN URL -> the file WordPress actually holds."""
    url = html.unescape(url)
    p = urllib.parse.urlparse(url)
    if p.netloc.endswith("wp.com"):
        return "https://" + p.path.lstrip("/")
    return url.split("?")[0]


def scrape():
    src = fetch(PAGE).decode("utf-8", "replace")
    tabs = {i: html.unescape(re.sub("<[^>]+>", "", t)).strip() for i, t in re.findall(
        r'<a[^>]*class="[^"]*elementor-gallery-title[^"]*"[^>]*data-gallery-index="(\d+)"[^>]*>(.*?)</a>', src, re.S)}
    items, seen = [], set()
    for tag in re.findall(r'<a[^>]*class="[^"]*e-gallery-item[^"]*"[^>]*>', src):
        href = re.search(r'href="([^"]+)"', tag)
        if not href:
            continue
        url = original(href.group(1))
        if url in seen:
            continue
        seen.add(url)
        tag_ids = (re.search(r'data-e-gallery-tags="([^"]*)"', tag) or [None, ""])[1]
        credit = ", ".join(tabs.get(t.strip(), "") for t in tag_ids.split(",") if t.strip())
        items.append(dict(url=url, credit=credit))
    return items


def download(items):
    os.makedirs(LIBRARY, exist_ok=True)

    def one(it):
        name = os.path.basename(urllib.parse.urlparse(it["url"]).path)
        path = os.path.join(LIBRARY, name)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            data = fetch(it["url"])
            with open(path, "wb") as f:
                f.write(data)
        it["file"] = name
        return it

    with cf.ThreadPoolExecutor(8) as pool:
        done = list(pool.map(one, items))
    with open(os.path.join(LIBRARY, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(done, f, indent=1)
    return done


# Where each photograph was taken, read off the pictures by eye, in the order the
# current gallery shows them. A frame can belong to more than one place. The
# names are the site's own: The Valley is the meadow; the deck is Lookout Deck.
PLACES = [
    ("magnolia", "Magnolia House"),
    ("valley", "The Valley"),
    ("deck", "Lookout Deck"),
    ("grounds", "The Grounds"),
    ("ready", "Getting Ready"),
    ("details", "The Details"),
    ("evening", "After Dark"),
]
TAGS = {
    "magnolia": [2, 29, 30, 33, 34, 36, 37, 38, 39, 40, 41, 74, 77, 78, 79, 120, 121, 123, 124,
                 125, 126, 127, 128, 132, 143, 145, 146, 147, 148],
    "valley": [1, 3, 5, 6, 26, 27, 28, 31, 32, 54, 55, 57, 58, 59, 61, 66, 67, 70, 71, 99, 100,
               106, 108, 114, 115, 116, 117, 118, 119, 120, 133, 134, 135, 136, 137, 138, 139,
               140, 141, 142, 155],
    "deck": [4, 10, 12, 13, 14, 15, 62, 63, 64, 69, 82, 88, 89, 90, 96, 97, 98, 101, 102, 103,
             105, 107, 144, 149, 150],
    "grounds": [0, 7, 8, 9, 19, 20, 21, 23, 42, 43, 44, 45, 46, 47, 65, 68, 76, 80, 81, 84, 85,
                91, 94, 95, 109, 111, 122],
    "ready": [16, 17, 18, 22, 35, 48, 49, 50, 51, 52, 53, 86, 92, 154],
    "details": [10, 24, 25, 56, 60, 72, 73, 75, 83, 87, 93, 104, 110, 112, 113, 127, 153],
    "evening": [11, 24, 25, 129, 130, 131, 151, 152],
}


def slug(name):
    base = os.path.splitext(name)[0].lower()
    base = re.sub(r"-scaled$", "", base)
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def build():
    with open(os.path.join(LIBRARY, "manifest.json"), encoding="utf-8") as f:
        items = json.load(f)
    os.makedirs(WEB, exist_ok=True)
    out, used = [], set()
    where = {}
    for key, idx in TAGS.items():
        for i in idx:
            where.setdefault(i, []).append(key)
    for n, it in enumerate(items):
        s = slug(it["file"])
        while s in used:
            s += "-b"
        used.add(s)
        im = ImageOps.exif_transpose(Image.open(os.path.join(LIBRARY, it["file"]))).convert("RGB")
        w, h = im.size
        for suffix, edge, q in (("", 1600, 80), ("-sm", 640, 74)):
            path = os.path.join(WEB, "%s%s.webp" % (s, suffix))
            if not os.path.exists(path):
                c = im.copy()
                c.thumbnail((edge, edge), Image.LANCZOS)
                c.save(path, quality=q, method=6)
        small = im.copy()
        small.thumbnail((640, 640))
        # the mean colour of the frame, painted while the thumbnail loads
        tone = small.resize((1, 1), Image.BOX).getpixel((0, 0))
        tags = [k for k, _ in PLACES if k in where.get(n, [])] or ["grounds"]
        out.append(dict(id=s, w=w, h=h, credit=it["credit"], tone="#%02x%02x%02x" % tone, tags=tags))
    with open(os.path.join(ROOT, "assets", "gallery.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    total = sum(os.path.getsize(os.path.join(WEB, x)) for x in os.listdir(WEB))
    print("%d photographs, %.1f MB of web images" % (len(out), total / 1048576.0))
    credits = {}
    for o in out:
        credits[o["credit"]] = credits.get(o["credit"], 0) + 1
    for k, v in sorted(credits.items(), key=lambda kv: -kv[1]):
        print("  %3d  %s" % (v, k or "(no credit)"))


def main():
    if "--build" not in sys.argv:
        items = scrape()
        print("found %d photographs" % len(items))
        download(items)
    build()


if __name__ == "__main__":
    main()
