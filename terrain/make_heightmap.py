"""
Turn the USGS 1m DEM of the estate into a compact heightmap the browser can read.

Output is an 8-bit greyscale PNG: the browser decodes it, reads the pixels off a
canvas, and rebuilds the terrain. ~20KB for the whole property, versus hundreds
of KB for the same grid as JSON.

Source box (WGS84), 1860 Pope Creek Rd, Wildwood GA:
    west  -85.40990   east  -85.40110
    south  34.95684   north  34.96404
"""
import os, json
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = r"C:/Users/DAVE~1.MCC/AppData/Local/Temp/claude/C--Users-dave-mccormick-Something/9113fdc1-8166-47e1-8097-b0e3ebb5a721/scratchpad/usgs/close.tif"
N    = 256                     # grid resolution the page renders

BBOX = {"west": -85.40990, "east": -85.40110, "south": 34.95684, "north": 34.96404}

im = Image.open(SRC)
im = im.resize((N, N), Image.LANCZOS)
px = list(im.getdata())
lo, hi = min(px), max(px)
rng = hi - lo

out = Image.new("L", (N, N))
out.putdata([int(round((v - lo) / rng * 255)) for v in px])
out.save(os.path.join(HERE, "terrain.png"), optimize=True)

meta = {
    "grid": N,
    "minElev": round(lo, 2),
    "maxElev": round(hi, 2),
    "relief": round(rng, 2),
    "bbox": BBOX,
    "metresWide": 800,
    "source": "USGS 3DEP 1m DEM via nationalmap.gov, sampled 2026-08",
}
json.dump(meta, open(os.path.join(HERE, "terrain.json"), "w"), indent=2)

print("terrain.png %dx%d  %d KB" % (N, N, os.path.getsize(os.path.join(HERE, "terrain.png")) // 1024))
print("elevation %.1f - %.1f m  (relief %.1f m)" % (lo, hi, rng))
