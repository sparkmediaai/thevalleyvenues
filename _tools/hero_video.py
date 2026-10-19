"""
The home page hero loop, cut from the sizzle reel.

    python _tools/hero_video.py "D:/DevStuff/VV Images/VVSizzleShorter.mp4"

The reel is 83 seconds of two-second cuts, letterboxed, with light-leak flashes
and seven seconds of black at the end. A background wants the opposite: slow,
clean, and a loop you cannot see the seam of. So this takes nine shots, mostly
the spaces and a little of the couple, crossfades them, and ends by fading back
into the first shot so the loop point is invisible.

The master never enters the repo. Only the web encodes land in assets/video/.
Needs ffmpeg; the imageio-ffmpeg package supplies one if none is installed.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "video")

# The opening of the Magnolia House, filmed in 4K by Barlow Film Co. These are
# whole two-second clips rather than ranges, and they need scaling into the
# reel's letterboxed frame rather than cropping out of it.
OPENING = r"D:/DevStuff/VV Images/Magnolia house opening/BROLL/HORIZONTAL"
WIDE = "scale=1920:1080,crop=1920:916:0:82"

# (start, end) in the reel, each held clear of the cut on either side. A shot
# may carry a third item -- its own source file -- and a fourth, its own filter.
SHOTS = [
    (4.4, 7.7),     # the meadow set for a ceremony, from the air
    (14.35, 16.15), # the estate from above
    (16.45, 18.35), # Magnolia House, the front
    (18.65, 20.65), # the glass roof of the conservatory
    (23.0, 26.2),   # the valley and the ridge
    (29.0, 32.3),   # the ceremony from directly overhead
    (49.4, 52.6),   # the couple on the Magnolia House steps
    (53.6, 55.4),   # walking, the mountain behind
    (62.0, 63.55),  # the sparkler dance
]

# Four from the opening, cut in among them: the estate rather than the party.
SHOTS = [
    SHOTS[0],                                                     # the meadow, from the air
    (0.15, 1.95, OPENING + "/barlowfilmco-magnoliahouse-broll-2026_00000527.mov", WIDE),
    SHOTS[1],                                                     # the estate from above
    (0.15, 1.95, OPENING + "/barlowfilmco-magnoliahouse-broll-2026_00000126.mov", WIDE),
    SHOTS[4],                                                     # the valley and the ridge
    (0.15, 1.95, OPENING + "/barlowfilmco-magnoliahouse-broll-2026_00051197.mov", WIDE),
    SHOTS[5],                                                     # the ceremony from overhead
    (0.15, 1.95, OPENING + "/barlowfilmco-magnoliahouse-broll-2026_00000093.mov", WIDE),
    SHOTS[6],                                                     # the couple on the steps
    SHOTS[7],                                                     # walking, the mountain behind
    SHOTS[8],                                                     # the sparkler dance
]
# The indices the lift and the tighter crop applied to have moved with them.
LIFT = {4: "eq=gamma=1.12"}
TIGHT = {8: "crop=1760:840:80:80,scale=1920:916"}
# The valley aerial is the one shot noticeably darker than the rest. It is lifted
# to sit with its neighbours, not graded: the brief is that nothing is darkened.
LIFT = {4: "eq=gamma=1.12"}
FADE = 0.5
# The reel's letterbox. cropdetect reports the picture from y=72 to 1003, but a
# few shots start their image as low as y=76 with a soft dark edge above it, so
# a few pixels more come off each side: a black line along the top of the film
# is exactly what a 72px crop left.
CROP = "crop=1920:916:0:80"
# The Magnolia House steps shot carries its own graded bar along the bottom as
# the camera rises, so it is cut in a little tighter and scaled back up.
TIGHT = {6: "crop=1760:840:80:80,scale=1920:916"}


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def build_master(src, path):
    ff = ffmpeg()
    args = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    shots = SHOTS + [SHOTS[0]]              # the first shot again, to fade back into
    for shot in shots:
        a, b = shot[0], shot[1]
        args += ["-ss", "%.3f" % a, "-t", "%.3f" % (b - a), "-i", shot[2] if len(shot) > 2 else src]
    f = []
    for i, shot in enumerate(shots):
        own = shot[3] if len(shot) > 3 else None
        chain = [own or TIGHT.get(i, CROP), "fps=30", "format=yuv420p", "setsar=1"]
        if own is None and i in LIFT:
            chain.insert(1, LIFT[i])
        f.append("[%d:v]%s,settb=AVTB[v%d]" % (i, ",".join(chain), i))
    prev, t = "v0", 0.0
    for i in range(1, len(shots)):
        t += (shots[i - 1][1] - shots[i - 1][0]) - FADE
        out = "x%d" % i
        f.append("[%s][v%d]xfade=transition=fade:duration=%.2f:offset=%.3f[%s]" % (prev, i, FADE, t, out))
        prev = out
    # Start FADE in, end FADE into the repeated first shot: both edges then show
    # the same frame of the meadow, and the loop has no seam.
    end = t + FADE
    f.append("[%s]trim=start=%.3f:end=%.3f,setpts=PTS-STARTPTS[out]" % (prev, FADE, end))
    args += ["-filter_complex", ";".join(f), "-map", "[out]", "-an",
             "-c:v", "libx264", "-crf", "14", "-preset", "slow", path]
    subprocess.run(args, check=True)
    return end - FADE


def encode(master):
    ff = ffmpeg()
    os.makedirs(OUT, exist_ok=True)
    jobs = [
        # desktop
        ("hero.mp4", ["-vf", "scale=1600:-2", "-c:v", "libx264", "-crf", "30", "-preset", "slow",
                      "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]),
        ("hero.webm", ["-vf", "scale=1600:-2", "-c:v", "libvpx-vp9", "-crf", "47", "-b:v", "0",
                       "-row-mt", "1", "-deadline", "good", "-cpu-used", "2"]),
        # phones see the hero at 4:3, so they get the middle of the frame and no more
        ("hero-sm.mp4", ["-vf", "crop=ih*4/3:ih,scale=720:540", "-c:v", "libx264", "-crf", "28",
                         "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]),
    ]
    for name, opts in jobs:
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", master, "-an"] + opts
                       + [os.path.join(OUT, name)], check=True)
    # posters: the first frame, which is also the frame the loop returns to
    for name, vf in (("hero-poster.png", "scale=1600:-2"), ("hero-poster-sm.png", "crop=ih*4/3:ih,scale=720:540")):
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", master, "-vf", vf,
                        "-frames:v", "1", os.path.join(OUT, name)], check=True)
    from PIL import Image
    for name in ("hero-poster", "hero-poster-sm"):
        png = os.path.join(OUT, name + ".png")
        Image.open(png).save(os.path.join(OUT, name + ".webp"), quality=82)
        os.remove(png)


def main():
    src = sys.argv[1]
    tmp = os.path.join(os.environ.get("TEMP", "."), "vv-hero-master.mp4")
    length = build_master(src, tmp)
    encode(tmp)
    print("loop %.1fs" % length)
    for f in sorted(os.listdir(OUT)):
        print("  assets/video/%-20s %6.0f KB" % (f, os.path.getsize(os.path.join(OUT, f)) / 1024.0))


if __name__ == "__main__":
    main()
