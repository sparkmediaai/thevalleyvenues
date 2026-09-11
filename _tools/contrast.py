"""
Measure every colour pairing the site actually uses.

    python _tools/contrast.py

The palette the client gave us is built on two colours that cannot carry text.
On the ivory page the brand olive measures 2.4:1 and the clay 2.9:1, where the
floor for body text is 4.5:1 and this site leans hardest on small letterspaced
caps. Rather than discard them, each keeps its given weight for rules, dots and
fills and has a darkened sibling in its own hue for anything that has to be
read -- --accent for the olive, --label for the clay.

This reads the values back out of assets/site.css, so the table can never drift
from the stylesheet: change a token and run it again.

Decorative rows are reported without a floor. A hairline or a 4px dot is not a
UI component and not a graphical object needed to understand the content, so
1.4.11 does not bite; they are listed so the number is at least known.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "assets", "site.css")
OPENING = os.path.join(ROOT, "assets", "opening.css")


def tokens():
    s = open(CSS, encoding="utf-8").read()
    block = s[s.index(":root{"):s.index("--display:")]
    raw = dict(re.findall(r"--([a-z0-9-]+)\s*:\s*([^;]+);", block))
    out = {}
    for k, v in raw.items():
        v = v.split("/*")[0].strip()
        seen = 0
        while v.startswith("var(--") and seen < 8:
            v = raw[v[6:v.index(")")]].split("/*")[0].strip()
            seen += 1
        if re.fullmatch(r"#[0-9a-fA-F]{6}", v):
            out[k] = v.upper()
    return out


def band():
    """The opening band names a token rather than a literal."""
    t = tokens()
    src = open(OPENING, encoding="utf-8").read()
    m = re.search(r"\.opening\{[^}]*background:var\(--([a-z0-9-]+)\)", src, re.S)
    return t.get(m.group(1)) if m else None


def lum(h):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    h = h.lstrip("#")
    r, g, b = (f(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main():
    t = tokens()
    t["band"] = band() or "#000000"
    t["white"] = "#FFFFFF"
    FLOOR = {"body": 4.5, "large": 3.0, "ui": 3.0, "deco": None}
    PAIRS = [
        # Deep olive is the only one of the seven that can carry text on a
        # light ground, so almost every row is the same ink on a different
        # surface. That is the palette, not a shortcut.
        ("body text on the page",        "ink",    "ground",   "body"),
        ("body text on a panel",         "ink",    "ground-2", "body"),
        ("body text on white",           "ink",    "paper",    "body"),
        ("a caption, the footer",        "ink",    "ground",   "body"),
        ("an eyebrow",                   "ink",    "ground",   "body"),
        ("what you type in a field",     "ink",    "paper",    "body"),
        # Soft on purpose: see the note in site.css. A visible label sits
        # above every field, so the placeholder conveys nothing alone.
        ("a field's placeholder",        "olive",  "paper",    "deco"),
        ("an outline button",            "accent", "ground",   "body"),
        ("an outline button on cream",   "accent", "ground-2", "body"),
        ("a solid button's label",       "ground", "accent",   "body"),
        ("the opening band",             "ink",    "band",     "body"),
        ("the band's own eyebrow",       "ink",    "band",     "body"),
        # Rules and marks. Soft on purpose, and none of them carries meaning
        # that the type beside it does not already carry.
        ("a hairline rule",              "line",      "ground", "deco"),
        ("a softer hairline",            "line-soft", "ground", "deco"),
        ("the dash before a denial",     "clay",      "ground-2", "deco"),
        ("the ivory page beside white",  "ground",    "paper",  "deco"),
    ]
    print("%-30s %-9s %-9s %8s" % ("pairing", "fore", "back", "ratio"))
    bad = 0
    for name, fg, bg, kind in PAIRS:
        if fg not in t or bg not in t:
            print("%-30s  no such token: %s" % (name, fg if fg not in t else bg))
            bad += 1
            continue
        r = ratio(t[fg], t[bg])
        floor = FLOOR[kind]
        if floor is None:
            note = "decorative"
        elif r >= floor:
            note = "pass"
        else:
            note = "FAIL (needs %.1f)" % floor
            bad += 1
        print("%-30s %-9s %-9s %6.2f:1  %s" % (name, t[fg], t[bg], r, note))
    print("\n%s" % ("%d failing" % bad if bad else "every pairing clears its floor"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
