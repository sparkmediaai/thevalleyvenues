"""
Bring the client's WordPress blog and reviews across, so the cutover does not
404 a year of writing.

    python _tools/blog_import.py            # fetch, clean, cut the pictures
    python _tools/blog_import.py --posts 3  # a few, while iterating

Their site is Elementor on WordPress. The body of a post lives in
`.elementor-widget-theme-post-content`; everything around it is chrome. What
comes out of there is sound HTML underneath the theme's classes, so this keeps
the structure -- headings, paragraphs, lists, links, images -- and throws away
every class, id, inline style and data attribute. What lands in the repo is the
writing, in this site's own markup.

Pictures are downloaded and cut to webp like the rest of the site's imagery,
because hotlinking their WordPress uploads would leave the new site depending
on the old host, which is the thing the cutover is meant to end.

URLs do not change: /blog/<slug>/ on the old site is /blog/<slug>/ on this one.
That is the whole point of the exercise.

Output:
    assets/blog.json        every post: slug, title, date, standfirst, body
    assets/blog/*.webp      the pictures, cut
Then _build/build.py writes the pages from that.
"""
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "blog")
OUT = os.path.join(ROOT, "assets", "blog.json")
SITE = "https://thevalleyvenues.com"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Where their old pages live on this site. Any link in a post that points at
# one of these is rewritten, so nothing sends a reader back to the old site.
LINKMAP = {
    "/wedding-pricing/": "/pricing/",
    "/lodging/": "/stay/",
    "/wedding-gallery/": "/gallery/",
    "/micro-weddings/": "/the-estate/lost-in-the-woods/",
    "/in-house-catering/": "/weddings/whats-included/",
    "/davis-hall/": "/the-estate/davis-hall/",
    "/the-valley/": "/the-estate/the-valley/",
    "/lookout-deck/": "/the-estate/lookout-deck/",
    "/magnolia-house/": "/the-estate/magnolia-house/",
    "/magnolia-house-old/": "/the-estate/magnolia-house/",
    "/reviews/": "/reviews/",
    "/contact-us/": "/inquire/",
    "/contact-form/": "/inquire/",
    "/newsletter/": "/inquire/",
    "/weddings/": "/weddings/",
    "/about/": "/about/",
    "/home": "/",
    "/home/": "/",
    "/blog": "/blog/",
}

KEEP_TAGS = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "em", "b", "i",
             "a", "blockquote", "br", "figure", "figcaption", "img"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,image/webp,*/*",
        "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def sitemap(which):
    xml = get("%s/%s-sitemap.xml" % (SITE, which))
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def cut_image(url, name):
    """Download once, cut to the site's width, save as webp."""
    path = os.path.join(IMG, name + ".webp")
    if os.path.exists(path):
        return name + ".webp"
    # Their pictures are served through Jetpack's CDN, which 404s for some of
    # the older uploads. The origin still has every one of them, so try that
    # first and keep the CDN as the fallback.
    plain = url.split("?")[0]
    tries = [plain.replace("https://i0.wp.com/", "https://"), plain, url]
    im = None
    for candidate in dict.fromkeys(tries):
        try:
            im = Image.open(io.BytesIO(get(candidate, binary=True))).convert("RGB")
            break
        except Exception:
            continue
    if im is None:
        print("    image failed: %s" % plain.split("/")[-1])
        return None
    if im.width > 1400:
        im = im.resize((1400, round(im.height * 1400.0 / im.width)), Image.LANCZOS)
    im.save(path, quality=80, method=5)
    return name + ".webp"


def clean(node, slug, images):
    """Their markup, reduced to this site's: structure kept, styling dropped."""
    for bad in node.select("script, style, noscript, iframe, form, button, svg"):
        bad.decompose()
    # Elementor wraps everything several times; unwrap anything that is not
    # one of the tags worth keeping.
    for el in node.find_all(True):
        if el.name == "img":
            src = el.get("data-src") or el.get("src") or ""
            if not src or src.startswith("data:"):
                el.decompose()
                continue
            src = urllib.parse.urljoin(SITE, src.split("?")[0])
            name = "%s-%d" % (slug[:40], len(images) + 1)
            saved = cut_image(src, name)
            if not saved:
                el.decompose()
                continue
            images.append(saved)
            alt = (el.get("alt") or "").strip()
            el.attrs = {"src": "/assets/blog/" + saved, "alt": alt,
                        "loading": "lazy", "decoding": "async"}
            continue
        if el.name == "a":
            href = el.get("href", "")
            if href.startswith(SITE):
                href = href[len(SITE):] or "/"
            # their links are inconsistent about the trailing slash, and some
            # carry a fragment that will not exist on the page it now points at
            path, hashmark, frag = href.partition("#")
            key = path if path.endswith("/") else path + "/"
            moved = LINKMAP.get(path) or LINKMAP.get(key)
            if moved:
                href = moved                      # the anchor went with the old page
            elif path:
                href = path + hashmark + frag
            el.attrs = {"href": href} if href else {}
            continue
        if el.name in KEEP_TAGS:
            el.attrs = {}
        else:
            el.unwrap()
    html = str(node)
    html = re.sub(r"</?(div|span|section|article|header|footer|main)[^>]*>", "", html)
    html = re.sub(r"<p>\s*(&nbsp;)?\s*</p>", "", html)
    html = re.sub(r"\n{2,}", "\n", html)
    return html.strip()


def post(url):
    slug = [p for p in url.split("/") if p][-1]
    soup = BeautifulSoup(get(url), "html.parser")

    def meta(attr, val):
        el = soup.find("meta", {attr: val})
        return (el.get("content") or "").strip() if el else ""

    body = soup.select_one(".elementor-widget-theme-post-content")
    if not body:
        print("    no body found")
        return None
    images = []
    title = (soup.h1.get_text(" ", strip=True) if soup.h1 else meta("property", "og:title"))
    title = re.sub(r"\s*[-|]\s*The Valley Venues\s*$", "", title)
    cover_url = meta("property", "og:image")
    cover = cut_image(cover_url, slug[:40] + "-cover") if cover_url else None
    return dict(
        slug=slug,
        url="/blog/%s/" % slug,
        title=title,
        date=meta("property", "article:published_time")[:10],
        standfirst=meta("name", "description"),
        cover=cover,
        body=clean(body, slug, images),
    )


def reviews():
    """Their reviews page, as quotations rather than as a page of markup."""
    soup = BeautifulSoup(get(SITE + "/reviews/"), "html.parser")
    out, seen = [], set()
    for el in soup.select("p, h2, h3, h4, blockquote"):
        t = el.get_text(" ", strip=True)
        if len(t) < 60 or len(t) > 900 or t in seen:
            continue
        low = t.lower()
        if any(w in low for w in ("cookie", "copyright", "all rights", "privacy",
                                  "subscribe", "newsletter")):
            continue
        seen.add(t)
        out.append(t)
    return out


def main():
    os.makedirs(IMG, exist_ok=True)
    limit = None
    if "--posts" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--posts") + 1])

    urls = [u for u in sitemap("post") if "/blog/" in u and u.rstrip("/") != SITE + "/blog"]
    print("%d posts on their sitemap" % len(urls))
    posts = []
    for i, u in enumerate(urls[:limit] if limit else urls, 1):
        print("%2d/%d  %s" % (i, len(urls), u.split("/blog/")[-1][:58]))
        try:
            p = post(u)
        except Exception as exc:
            print("    failed: %s" % exc)
            continue
        if p:
            posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)

    quotes = []
    try:
        quotes = reviews()
        print("reviews: %d quotations" % len(quotes))
    except Exception as exc:
        print("reviews failed: %s" % exc)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dict(posts=posts, reviews=quotes), f, indent=1, ensure_ascii=False)
    kb = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG)) // 1024
    print("\n%d posts, %d pictures, %d KB" % (len(posts), len(os.listdir(IMG)), kb))


if __name__ == "__main__":
    main()
