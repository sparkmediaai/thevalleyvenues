"""
Contact sheets from a triaged library, in the order the frames were taken.

A wedding day runs in sequence — getting ready, the drive, the ceremony, the
deck at golden hour, the reception after dark — and the frames are already in
that order. So the fastest way to categorise 1,700 images is not to look at
1,700 images. It is to look at every twentieth one, find where the day turns,
and then work within those windows.

    python _tools/sheets.py "D:/.../_triage" --shoot 4 --stride 20
    python _tools/sheets.py "D:/.../_triage" --shoot 4 --from 400 --to 560

Each cell is labelled with its position in the shoot and the time it was taken,
so a sheet can be read back as "frames 380 to 520 are the ceremony".
"""
import argparse, json, os
from PIL import Image, ImageDraw

CELL_W, CELL_H, COLS, ROWS = 300, 200, 5, 4
LABEL = 18
PAPER = (24, 27, 22)
INK = (233, 231, 221)
DIM = (150, 158, 140)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("triage_dir")
    ap.add_argument("--shoot", type=int, required=True)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--from", dest="lo", type=int, default=1)
    ap.add_argument("--to", dest="hi", type=int, default=10 ** 9)
    ap.add_argument("--tag", default="", help="suffix for the output filenames")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    td = os.path.abspath(args.triage_dir)
    data = json.load(open(os.path.join(td, "data.json"), encoding="utf-8"))
    out = os.path.abspath(args.out or os.path.join(td, "sheets"))
    os.makedirs(out, exist_ok=True)

    rows = [r for r in data["rows"]
            if r.get("shoot") == args.shoot and r["verdict"] == "keep" and r.get("thumb")]
    rows.sort(key=lambda r: (r.get("shot") or "", r["name"]))
    for i, r in enumerate(rows, 1):
        r["pos"] = i
    sel = [r for r in rows if args.lo <= r["pos"] <= args.hi][::args.stride]
    print("shoot %d: %d keepers, %d on these sheets" % (args.shoot, len(rows), len(sel)))

    per = COLS * ROWS
    made = []
    for page in range((len(sel) + per - 1) // per):
        chunk = sel[page * per:(page + 1) * per]
        rws = (len(chunk) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * CELL_W, rws * (CELL_H + LABEL)), PAPER)
        d = ImageDraw.Draw(sheet)
        for i, r in enumerate(chunk):
            try:
                im = Image.open(os.path.join(td, r["thumb"])).convert("RGB")
            except Exception:
                continue
            ratio = max(CELL_W / im.width, CELL_H / im.height)
            im = im.resize((max(1, int(im.width * ratio)), max(1, int(im.height * ratio))),
                           Image.LANCZOS)
            im = im.crop(((im.width - CELL_W) // 2, (im.height - CELL_H) // 2,
                          (im.width - CELL_W) // 2 + CELL_W,
                          (im.height - CELL_H) // 2 + CELL_H))
            x, y = (i % COLS) * CELL_W, (i // COLS) * (CELL_H + LABEL)
            sheet.paste(im, (x, y))
            when = (r.get("shot") or "")[11:16]
            d.text((x + 4, y + CELL_H + 3),
                   "%d  %s  %s" % (r["pos"], when, "P" if r.get("portrait") else "L"),
                   fill=INK)
            d.text((x + CELL_W - 60, y + CELL_H + 3), r["use"], fill=DIM)
        name = "shoot%02d%s-%02d.png" % (args.shoot, ("-" + args.tag) if args.tag else "", page + 1)
        sheet.save(os.path.join(out, name))
        made.append(name)
        print("  %s  %d frames" % (name, len(chunk)))
    print("\n%s" % out)


if __name__ == "__main__":
    main()
