"""
Cut the site's images from the sorted library.

Each slot on the site has a job — a full-bleed hero, a section beside text, a
card in a row — and a job implies a width and an aspect. Rather than resize by
hand every time a choice changes, the slots are listed here and rebuilt from
the originals in one pass.

    python _tools/place.py

Chosen from the contact sheets in _triage/picks. Nothing is invented: if an
original is smaller than the slot asks for, the slot gets what exists.
"""
import os
from PIL import Image, ImageStat, ImageEnhance

LIB = r"D:/DevStuff/VV Images/Sorted"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")

# (destination, category folder, filename, width, height, vertical bias)
SLOTS = [
    # --- the home page --------------------------------------------------

    # --- the estate -----------------------------------------------------
    ("estate",         "01 Mountain & landscape", "ValleyVenuesStyledShoot-062.jpg", 2200, 1100, 0.52),
    ("magnolia-house", "03 Magnolia House",       "ValleyVenuesStyledShoot-106.jpg", 1600, 1200, 0.50),
    ("the-valley",     "02 The Valley",           "WeddingDay-781.jpg",             1600, 1200, 0.50),
    ("lookout-deck",   "04 Lookout Deck",         "WeddingDay-1419.jpg",            1600, 1200, 0.48),
    # Interiors only, dressed, drapery and chandeliers lit — the direction is
    # explicit that Davis Hall is earned rather than led with.
    ("davis-hall",     "05 Davis Hall",           "WeddingDay-1272.jpg",            1600, 1200, 0.50),

    # --- weddings -------------------------------------------------------
    ("weddings",       "02 The Valley",           "SneakPeek-10.jpg",               2000, 1000, 0.52),
    # The conservatory is the answer to "what happens if it rains", so it
    # carries the page that answers it.
    ("included",       "03 Magnolia House",       "ValleyVenueSSSneakPeaks-46.jpg", 2000, 1000, 0.50),
    ("real-weddings",  "09 People & candid",      "0B6A1619.jpg",                   2000, 1000, 0.45),
    ("single-day",     "02 The Valley",           "ValleyVenueSSSneakPeaks-17.jpg", 2000, 1000, 0.50),

    # --- stay, planners, about -------------------------------------------
    # Only 1600px exists for the cottages; the slot takes what there is.
    ("stay",           "06 Lodging & cottages",   "Valley-Venues-Wedding-Day-1-9.jpg", 1600, 800, 0.46),
    ("planners",       "01 Mountain & landscape", "ValleyVenuesStyledShoot-061.jpg", 2000, 1000, 0.52),
    ("vendors",        "08 Details & decor",      "WeddingDay-20.jpg",              2000, 1000, 0.50),
    ("about",          "03 Magnolia House",       "ValleyVenuesStyledShoot-124.jpg", 2000, 1000, 0.46),
# --- the hero, read as a clock ---------------------------------------
    # Five frames from one property across one day. The estate's whole claim is
    # that it belongs to one family for the length of a weekend, so the hero
    # moves through hours rather than through venues. Order matters here.
    ("hero-1", "03 Magnolia House",        "ValleyVenuesStyledShoot-106.jpg", 2200, 1100, 0.50),
    # Chosen for its shadow, not just its subject. A hero that carries type needs
    # somewhere dark for the type to sit: this frame is 73% shadow in the text
    # column against the 19% of the bedroom shot that was here, which turned to
    # mush the moment a scrim went over it.
    ("hero-2", "10 Getting ready",         "WeddingDay-136.jpg",              2200, 1100, 0.46),
    ("hero-3", "02 The Valley",            "WeddingDay-648.jpg",              2200, 1100, 0.50),
    ("hero-4", "01 Mountain & landscape",  "WeddingDay-1096.jpg",             2200, 1100, 0.42),
    ("hero-5", "03 Magnolia House",        "ValleyVenueSSSneakPeaks-46.jpg",  2200, 1100, 0.50),

    # --- the weekend, one frame per movement ------------------------------
    ("wk-fri",  "10 Getting ready",        "WeddingDay-116.jpg",              1200, 900, 0.50),
    ("wk-dawn", "10 Getting ready",        "ValleyVenuesStyledShoot-042.jpg", 1200, 900, 0.46),
    ("wk-gold", "04 Lookout Deck",         "WeddingDay-1419.jpg",             1200, 900, 0.46),
    # The copy here is about three mornings and breakfast, so the frame has to be
    # daylight. The sparkler shot that was here reads as the night before, and it
    # is also nearly the same photograph as the closing band further down.
    ("wk-sun",  "06 Lodging & cottages",   "Valley-Venues-Wedding-Day-10-16.jpg", 1200, 900, 0.50),

    # --- the close, held back until last ----------------------------------
    ("close-woods", "06 Lodging & cottages", "Valley-Venues-Wedding-Day-15-11.jpg", 1600, 900, 0.44),
# --- the stakes: a cluster beside the words --------------------------
    # The library is 61% portrait and almost none of it was being used. This
    # section is about people being in one place, so it gets people.
    ("note-1", "09 People & candid",     "0B6A1658.jpg",  900, 1200, 0.42),
    ("note-2", "10 Getting ready",       "1B0A3346.jpg",  900, 1200, 0.46),
    ("note-3", "09 People & candid",     "0B6A0960.jpg",  900, 1200, 0.40),

    # --- a full-bleed breath, tall enough to move behind its frame -------
    ("band-estate", r"C:/Users/dave.mccormick/Downloads/drive-download-20260828T222918Z-1-001",
     "DJI_0679.jpg", 1600, 900, 0.50),
    # ================= the other ten pages ==============================
    # Everything below was cut in one pass after the home page, from category
    # contact sheets rather than from shoot sheets -- once the library is
    # sorted the question is no longer "what is this shoot" but "what in this
    # category can carry a page". See catsheet.py.

    # --- weddings ---------------------------------------------------------
    ("w-weekend",   "02 The Valley",           "WeddingDay-862.jpg",                 1200, 900, 0.48),
    ("w-premium",   "08 Details & decor",      "Valley-Venues-Wedding-Day-9-12.jpg", 1200, 900, 0.46),
    ("w-single",    "02 The Valley",           "ValleyVenuesStyledShoot-010.jpg",    1200, 900, 0.50),
    # An empty meadow with an arch in it and nothing else. The quietest frame
    # in the library, which is what a band with type over it needs.
    ("band-vows",   "01 Mountain & landscape", "WeddingDay-1145.jpg",                1800, 900, 0.50),

    # --- what's included --------------------------------------------------
    ("inc-decor",   "08 Details & decor",      "Valley-Venues-Wedding-Day-6-4.jpg",  1200, 900, 0.50),
    # The conservatory from outside, glass on three sides. The page answers
    # "what happens if it rains" and this is the answer, photographed.
    ("inc-rain",    "01 Mountain & landscape", "ValleyVenuesStyledShoot-068.jpg",    1200, 900, 0.50),
    ("inc-team",    "05 Davis Hall",           "WeddingDay-1388.jpg",                1200, 900, 0.46),
    ("inc-food",    "11 Food & catering",      "Valley-Venues-Wedding-Day-7-15.jpg", 1200, 900, 0.50),
    ("inc-sleep",   "01 Mountain & landscape", "ValleyVenuesStyledShoot-064.jpg",    1200, 900, 0.52),
    ("inc-yours",   "08 Details & decor",      "WeddingDay-10.jpg",                  1200, 900, 0.50),

    # --- real weddings, a gallery of what exists --------------------------
    # g-1 and g-5 are the two frames the gallery gives double width to, so they
    # are cut wide here rather than cropped wide by object-fit later. A 4:3
    # frame reduced to 11:4 in the browser crops from the centre, which took
    # the top of the officiant's head off.
    ("g-1", "02 The Valley",      "WeddingDay-848.jpg",                 1400, 510, 0.25),
    ("g-2", "09 People & candid", "WeddingDay-520.jpg",                 1000, 750, 0.46),
    ("g-3", "05 Davis Hall",      "WeddingDay-1237.jpg",                1000, 750, 0.46),
    ("g-4", "09 People & candid", "WeddingDay-561.jpg",                 1000, 750, 0.44),
    ("g-5", "09 People & candid", "WeddingDay-1620.jpg",                1400, 510, 0.22),
    ("g-6", "08 Details & decor", "Valley-Venues-Wedding-Day-3-4(1).jpg", 1000, 750, 0.50),
    ("g-7", "09 People & candid", "WeddingDay-403.jpg",                 1000, 750, 0.44),
    ("g-8", "02 The Valley",      "WeddingDay-886.jpg",                 1000, 750, 0.48),

    # --- single day -------------------------------------------------------
    ("sd-fire",     "08 Details & decor",      "Valley-Venues-Wedding-Day-9-14.jpg", 1200, 900, 0.50),

    # --- stay -------------------------------------------------------------
    # Overlook Village from across the lawn. The cottages had only ever
    # appeared on this site one at a time, which undersells eight of them.
    ("stay-village","01 Mountain & landscape", "ValleyVenuesStyledShoot-066.jpg",    1600, 900, 0.52),
    ("stay-inside", "06 Lodging & cottages",   "Valley-Venues-Wedding-Day-17-9.jpg", 1200, 900, 0.50),
    ("band-return", "01 Mountain & landscape", "WeddingDay-1130.jpg",                1800, 900, 0.44),

    # --- the estate -------------------------------------------------------
    ("band-ground", "01 Mountain & landscape", "SneakPeek-65.jpg",                   1800, 900, 0.50),

    # --- planners and vendors ---------------------------------------------
    ("pl-deck",     "09 People & candid",      "WeddingDay-1484.jpg",                1800, 900, 0.46),
    ("vend-table",  "05 Davis Hall",           "WeddingDay-1194.jpg",                1200, 900, 0.50),

    # --- about ------------------------------------------------------------
    # Not the swan centrepiece that was here. The page is about what a person
    # feels standing in a room, and a close-up of a table ornament is the one
    # thing on the estate that answers a different question.
    ("ab-toast",    "08 Details & decor",      "Valley-Venues-Wedding-Day-6-12.jpg", 1200, 900, 0.46),
    ("band-family", "01 Mountain & landscape", "WeddingDay-1076.jpg",                1800, 900, 0.42),

    # --- book a tour ------------------------------------------------------
    ("tour",        "01 Mountain & landscape", "WeddingDay-1100.jpg",                2000, 1000, 0.44),
    # --- one dark close per page ------------------------------------------
    # Every page now ends the way the home page does: a full-bleed frame, the
    # last thing the page has to say, and the invitation. They are chosen dark
    # or low-key on purpose -- the scrim over them is heavy, and a bright frame
    # under it just looks like a bright frame that has been ruined.
    ("close-weddings", "03 Magnolia House",     "ValleyVenuesStyledShoot-269.jpg",    1800, 1000, 0.50),
    ("close-included", "03 Magnolia House",     "ValleyVenuesStyledShoot-289.jpg",    1800, 1000, 0.50),
    ("close-real",     "09 People & candid",    "WeddingDay-1555.jpg",                1800, 1000, 0.45),
    ("close-single",   "10 Getting ready",      "ValleyVenuesStyledShoot-006.jpg",    1800, 1000, 0.50),
    ("close-stay",     "06 Lodging & cottages", "Valley-Venues-Wedding-Day-15-12.jpg",1800, 1000, 0.50),
    ("close-estate",   "10 Getting ready",      "Valley-Venues-Wedding-Day-22-2.jpg", 1800, 1000, 0.42),
    ("close-planners", "04 Lookout Deck",       "WeddingDay-1426.jpg",                1800, 1000, 0.42),
    ("close-vendors",  "03 Magnolia House",     "ValleyVenuesStyledShoot-213.jpg",    1800, 1000, 0.50),
    ("close-about",    "10 Getting ready",      "WeddingDay-186.jpg",                 1800, 1000, 0.40),
    ("close-tour",     "03 Magnolia House",     "ValleyVenuesStyledShoot-121.jpg",    1800, 1000, 0.50),

    # --- a few more inside the pages --------------------------------------
    ("inc-glass",  "03 Magnolia House", "ValleyVenuesStyledShoot-240.jpg", 1600, 1200, 0.50),
    # The meadow from above with the arch small in the middle of it. Almost
    # nothing in the frame, which is what a band carrying one line wants.
    # --- weddings: the hours nobody schedules ---------------------------
    # A cluster is three 3:4 frames, so all three are cut portrait.
    ("w-night",        "10 Getting ready",        "WeddingDay-105.jpg",              900, 1200, 0.45),
    ("w-morning",      "10 Getting ready",        "WeddingDay-37.jpg",               900, 1200, 0.40),
    ("w-after",        "06 Lodging & cottages",   "Valley-Venues-Wedding-Day-1-10.jpg", 900, 1200, 0.50),
    # Beside the figure: what the figure actually buys.
    ("w-alone",        "01 Mountain & landscape", "ValleyVenuesStyledShoot-063.jpg", 1400, 1050, 0.50),
    ("band-quiet", "10 Getting ready",  "ValleyVenuesStyledShoot-056.jpg", 1800,  900, 0.50),
]

TARGET = 0.55          # the set is nudged toward one mean so the pages agree


# A slot's "category" is normally a folder inside the sorted library, but it can
# also be an absolute path — some frames came straight from the client rather
# than through the sort, and there is no reason to launder them through it.
def find(cat, name):
    if os.path.isabs(cat):
        p = os.path.join(cat, name)
        return p if os.path.exists(p) else None
    for orient in ("landscape", "portrait", "square"):
        p = os.path.join(LIB, cat, orient, name)
        if os.path.exists(p):
            return p
    return None


import sys
# `python _tools/place.py w-night w-alone` cuts only those. Without it every
# slot is rebuilt, which is right after a library change and wasteful otherwise.
only = set(sys.argv[1:])
total = 0
for dest, cat, name, W, H, bias in SLOTS:
    if only and dest not in only:
        continue
    src = find(cat, name)
    if not src:
        print("MISSING  %-16s %s / %s" % (dest, cat, name))
        continue
    im = Image.open(src)
    im.draft("RGB", (W * 2, H * 2))
    im = im.convert("RGB")
    if im.width < W:                      # never invent pixels
        H = int(H * im.width / float(W))
        W = im.width
    r = max(W / float(im.width), H / float(im.height))
    im = im.resize((max(W, int(im.width * r)), max(H, int(im.height * r))), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * bias)
    im = im.crop((x, y, x + W, y + H))

    lum = ImageStat.Stat(im.convert("L")).mean[0] / 255.0
    if lum < 0.46 or lum > 0.66:
        im = ImageEnhance.Brightness(im).enhance(max(0.85, min(1.25, TARGET / lum)))

    path = os.path.join(OUT, dest + ".webp")
    im.save(path, quality=82, method=5)
    kb = os.path.getsize(path) // 1024
    total += kb
    print("%-16s %4dx%-4d %4dKB   %s" % (dest, W, H, kb, name))

print("\n%d slots, %d KB total" % (len(SLOTS), total))
