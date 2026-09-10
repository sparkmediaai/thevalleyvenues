"""
A contact sheet for one category of the sorted library.

sheets.py reads the triage folder and lays a shoot out in the order it was
taken, which is the right view when you are deciding what a category *is*.
Once the library is sorted the question changes: you want to see everything in
one category at once and pick the two or three frames that will carry a page.

    python _tools/catsheet.py "05 Davis Hall" --orient landscape

Every cell is labelled with its filename, because the filename is what goes
into place.py afterwards.
"""
import argparse, os
from PIL import Image, ImageDraw

LIB = r"D:/DevStuff/VV Images/Sorted"
CELL_W, CELL_H, COLS = 320, 214, 5
LABEL = 20
PAPER = (24, 27, 22)
INK = (233, 231, 221)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("category")
    ap.add_argument("--orient", default="landscape")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    src = os.path.join(LIB, args.category, args.orient)
    names = sorted(f for f in os.listdir(src) if f.lower().endswith(".jpg"))
    # Evenly spread rather than truncated: the first 25 of 140 frames are one
    # corner of one reception, which tells you nothing about the category.
    if len(names) > args.max:
        step = len(names) / float(args.max)
        names = [names[int(i * step)] for i in range(args.max)]

    rows = (len(names) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, rows * (CELL_H + LABEL)), PAPER)
    d = ImageDraw.Draw(sheet)

    for i, name in enumerate(names):
        im = Image.open(os.path.join(src, name))
        im.draft("RGB", (CELL_W * 2, CELL_H * 2))
        im = im.convert("RGB")
        r = min((CELL_W - 8) / float(im.width), (CELL_H - 8) / float(im.height))
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        x = (i % COLS) * CELL_W + (CELL_W - im.width) // 2
        y = (i // COLS) * (CELL_H + LABEL) + (CELL_H - im.height) // 2
        sheet.paste(im, (x, y))
        d.text(((i % COLS) * CELL_W + 6,
                (i // COLS) * (CELL_H + LABEL) + CELL_H + 3),
               name[:40], fill=INK)

    out = args.out or os.path.join(
        os.environ.get("TEMP", "."),
        "cat-%s-%s.png" % (args.category.split()[0], args.orient))
    sheet.save(out)
    print("%s  %d frames of %d" % (out, len(names), len(os.listdir(src))))


if __name__ == "__main__":
    main()
