"""
Move a triaged library into category folders.

Reads the data.json written by triage.py plus an assignment file, and files
every image under its category and orientation:

    Sorted/
      02 The Valley/landscape/...
      02 The Valley/portrait/...
      _rejected/duplicate/...
      _rejected/soft/...

Two deliberate choices about destruction. Rejects are moved to _rejected rather
than deleted, because "soft" and "near-duplicate" are judgements made by a
script and a person may disagree with a few of them; deleting that folder
afterwards is one action and entirely safe. And every move is written to
manifest.csv, so the whole operation can be reversed with --undo.

    python _tools/sort.py "D:/.../_triage" --assign assign.json
    python _tools/sort.py "D:/.../_triage" --undo

The assignment file maps each category to a list of rules. A rule is a shoot,
optionally narrowed to a range of positions within that shoot, or an explicit
list of filenames. A category can have several rules because a day comes back
to the same place more than once:

    {
      "The Valley":   [{"shoot": 4, "range": [511, 855]}],
      "Lookout Deck": [{"shoot": 4, "range": [179, 196]},
                       {"shoot": 4, "range": [1201, 1270]}],
      "Details & decor": [{"shoot": 1, "range": [1, 9]},
                          {"names": ["WeddingDay-221.jpg"]}]
    }

Positions are counted over the keepers of that shoot in capture order, which is
what the contact sheets are labelled with.
"""
import argparse, csv, json, os, shutil, sys


def load(triage_dir):
    with open(os.path.join(triage_dir, "data.json"), encoding="utf-8") as f:
        return json.load(f)


def orientation(r):
    if r.get("portrait"):
        return "portrait"
    ratio = (r["w"] / float(r["h"])) if r.get("h") else 1.0
    return "square" if 0.95 <= ratio <= 1.05 else "landscape"


def resolve(data, assign):
    """One category per image. An explicit filename always beats a range."""
    by_name, by_shoot = {}, {}
    for cat, rules in assign.items():
        if cat.startswith("_"):               # notes to the reader, not rules
            continue
        if isinstance(rules, dict):           # tolerate a single rule
            rules = [rules]
        for rule in rules:
            for n in rule.get("names", []):
                by_name[n] = cat
            shoot = rule.get("shoot")
            if shoot is not None:
                by_shoot.setdefault(shoot, []).append(
                    (cat, rule.get("range"), rule.get("green_below"), rule.get("green_above")))

    # Position within a shoot, counted over its keepers in capture order —
    # the same numbering the contact sheets carry.
    pos = {}
    per_shoot = {}
    for r in data["rows"]:
        if r.get("shoot") and r["verdict"] == "keep":
            per_shoot.setdefault(r["shoot"], []).append(r)
    for shoot, group in per_shoot.items():
        group.sort(key=lambda r: (r.get("shot") or "", r["name"]))
        for i, r in enumerate(group, 1):
            pos[r["name"]] = i

    out = {}
    for r in data["rows"]:
        if r["name"] in by_name:
            out[r["name"]] = by_name[r["name"]]
            continue
        # Rules are tried in the order they appear in the file, so a narrow
        # rule placed above a broad one wins. That is how the one genuinely
        # interleaved stretch is handled: while the reception room was being
        # set the photographer kept crossing between it and the meadow, and no
        # range can separate those. Greenness can — a white room full of linen
        # is not green and a meadow is.
        for cat, rng, gb, ga in by_shoot.get(r.get("shoot"), []):
            p = pos.get(r["name"])
            if rng is not None and not (p is not None and rng[0] <= p <= rng[1]):
                continue
            g = r.get("green")
            if gb is not None and (g is None or g >= gb):
                continue
            if ga is not None and (g is None or g <= ga):
                continue
            out[r["name"]] = cat
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("triage_dir")
    ap.add_argument("--assign", help="JSON mapping categories to shoots/names")
    ap.add_argument("--dest", default=None, help="default: <library>/Sorted")
    ap.add_argument("--undo", action="store_true", help="put everything back from manifest.csv")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    triage_dir = os.path.abspath(args.triage_dir)
    manifest = os.path.join(triage_dir, "manifest.csv")

    if args.undo:
        if not os.path.exists(manifest):
            sys.exit("no manifest.csv in %s" % triage_dir)
        moved = 0
        with open(manifest, encoding="utf-8", newline="") as f:
            rowsback = list(csv.DictReader(f))
        for row in reversed(rowsback):
            if os.path.exists(row["to"]) and not os.path.exists(row["from"]):
                os.makedirs(os.path.dirname(row["from"]), exist_ok=True)
                shutil.move(row["to"], row["from"])
                moved += 1
        print("put %d files back" % moved)
        return

    data = load(triage_dir)
    dest = os.path.abspath(args.dest or os.path.join(os.path.dirname(data["source"]), "Sorted"))
    assign = {}
    if args.assign:
        with open(args.assign, encoding="utf-8") as f:
            assign = json.load(f)
    cats = resolve(data, assign)

    order = {c: i + 1 for i, c in enumerate(data["categories"])}
    plan, unassigned = [], 0
    for r in data["rows"]:
        if not r.get("path") or not os.path.exists(r["path"]):
            continue
        if r["verdict"] != "keep":
            folder = os.path.join(dest, "_rejected", r["verdict"])
        else:
            cat = cats.get(r["name"])
            if not cat:
                unassigned += 1
                folder = os.path.join(dest, "_unsorted", "shoot %02d" % (r.get("shoot") or 0))
            else:
                folder = os.path.join(dest, "%02d %s" % (order.get(cat, 99), cat), orientation(r))
        plan.append((r["path"], os.path.join(folder, r["name"])))

    tally = {}
    for _, to in plan:
        key = os.path.relpath(os.path.dirname(to), dest)
        tally[key] = tally.get(key, 0) + 1
    for k in sorted(tally):
        print("  %-46s %4d" % (k, tally[k]))
    print("\n  %d files, %d still unsorted" % (len(plan), unassigned))
    if args.dry_run:
        print("\n  dry run — nothing moved")
        return

    rowsout = []
    for src, to in plan:
        os.makedirs(os.path.dirname(to), exist_ok=True)
        if os.path.exists(to):
            stem, ext = os.path.splitext(to)
            n = 2
            while os.path.exists("%s-%d%s" % (stem, n, ext)):
                n += 1
            to = "%s-%d%s" % (stem, n, ext)
        shutil.move(src, to)
        rowsout.append({"from": src, "to": to})

    with open(manifest, "w", encoding="utf-8", newline="") as f:
        wcsv = csv.DictWriter(f, fieldnames=["from", "to"])
        wcsv.writeheader()
        wcsv.writerows(rowsout)
    print("\n  moved %d files into %s" % (len(rowsout), dest))
    print("  manifest at %s  (reverse with --undo)" % manifest)


if __name__ == "__main__":
    main()
