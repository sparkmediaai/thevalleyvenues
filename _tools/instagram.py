"""
Pull the estate's latest Instagram posts into the site.

    python _tools/instagram.py          # fetch, cut the frames, write the feed
    python _tools/instagram.py refresh  # print a renewed long-lived token

Why at build time rather than in the browser: an embed widget would drop
someone else's script, fonts and cookies onto every page that carries it, cost
a second of load, and bring its own styling to argue with. This fetches the
posts on a schedule, saves the pictures into the repo like any other
photograph, and the page renders them in the site's own type and colour. If
the feed is missing or stale the section simply does not appear.

What it needs, from the environment (never from the repo -- this is public):

    IG_TOKEN     a long-lived access token for the account
    IG_USER_ID   optional; "me" works for a token issued to the account itself
    IG_API_BASE  optional; graph.instagram.com by default, or
                 https://graph.facebook.com/v23.0 for a Page-linked token

Scraping is not an option here: Instagram's grid is behind a login for
visitors, and pulling it anyway would breach their terms and break often.
"""
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_IMG = os.path.join(ROOT, "assets", "img", "ig")
OUT_JSON = os.path.join(ROOT, "assets", "instagram.json")

BASE = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v23.0")
USER = os.environ.get("IG_USER_ID", "me")
TOKEN = os.environ.get("IG_TOKEN", "")

WANT = 8            # how many make it onto the page
FETCH = 16          # how many to ask for, so videos and duds can be skipped
SIZE = 900          # the square each frame is cut to

FIELDS = "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp"


def get(url):
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def caption(text):
    """The first thing they said, without the hashtag wall underneath it."""
    if not text:
        return ""
    text = text.split("#")[0]
    text = re.sub(r"\s+", " ", text).strip(" -–—·|")
    text = re.sub(r"[\r\n]+", " ", text)
    if len(text) > 150:
        cut = text[:150].rsplit(" ", 1)[0]
        text = cut + "…"
    return text.strip()


def square(data, path):
    """Centre-cut to a square, the way the rest of the site's frames are cut."""
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    side = min(im.width, im.height)
    x = (im.width - side) // 2
    y = int((im.height - side) * 0.42)      # faces sit above centre
    im = im.crop((x, y, x + side, y + side))
    if im.width > SIZE:
        im = im.resize((SIZE, SIZE), Image.LANCZOS)
    im.save(path, quality=80, method=5)
    return os.path.getsize(path)


def refresh():
    if not TOKEN:
        sys.exit("no IG_TOKEN to refresh")
    url = ("https://graph.instagram.com/refresh_access_token"
           "?grant_type=ig_refresh_token&access_token=" + urllib.parse.quote(TOKEN))
    out = get(url)
    print(out.get("access_token", ""))
    print("expires in %d days" % (out.get("expires_in", 0) // 86400), file=sys.stderr)


def main():
    if not TOKEN:
        # Not an error: the site builds and deploys without a feed, and the
        # section hides itself. This is the state before the token exists.
        print("instagram: no IG_TOKEN set, leaving the feed as it is")
        return
    url = "%s/%s/media?fields=%s&limit=%d&access_token=%s" % (
        BASE.rstrip("/"), USER, FIELDS, FETCH, urllib.parse.quote(TOKEN))
    data = get(url).get("data", [])
    os.makedirs(OUT_IMG, exist_ok=True)

    posts, n = [], 0
    for item in data:
        if len(posts) >= WANT:
            break
        src = item.get("thumbnail_url") if item.get("media_type") == "VIDEO" else item.get("media_url")
        if not src:
            continue
        n += 1
        name = "ig-%d.webp" % len(posts)
        try:
            with urllib.request.urlopen(src, timeout=60) as r:
                kb = square(r.read(), os.path.join(OUT_IMG, name)) // 1024
        except Exception as exc:                       # a single bad frame is not fatal
            print("instagram: skipped %s (%s)" % (item.get("id"), exc))
            continue
        posts.append(dict(img=name, permalink=item.get("permalink", ""),
                          caption=caption(item.get("caption")),
                          timestamp=item.get("timestamp", ""),
                          video=item.get("media_type") == "VIDEO"))
        print("  %-10s %4dKB  %s" % (name, kb, posts[-1]["caption"][:48]))

    # Frames from a previous, longer run would otherwise linger.
    for f in os.listdir(OUT_IMG):
        if f.startswith("ig-") and f not in [p["img"] for p in posts]:
            os.remove(os.path.join(OUT_IMG, f))

    feed = dict(fetched=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                profile="https://www.instagram.com/thevalleyvenues/",
                handle="thevalleyvenues", posts=posts)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=1)
    print("instagram: %d posts" % len(posts))


if __name__ == "__main__":
    refresh() if len(sys.argv) > 1 and sys.argv[1] == "refresh" else main()
