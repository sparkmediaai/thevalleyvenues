"""
Cut a film for the top of a place page.

    python _tools/place_film.py <source.mov> <name>

Writes assets/video/<name>.webm, <name>.mp4, <name>-sm.mp4 and a poster, at
the same settings the home page's hero uses: no audio, 1600px on the long edge
for the desktop files, a 720px one cropped to 4:3 for phones, and a poster that
carries the frame until the video arrives.

A page hero plays muted and looped, so the audio track is dropped rather than
silenced -- it is weight nobody can hear.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "video")


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__.strip())
    src, name = sys.argv[1], sys.argv[2]
    if not os.path.exists(src):
        raise SystemExit("no such file: %s" % src)
    ff = ffmpeg()
    os.makedirs(OUT, exist_ok=True)

    jobs = [
        ("%s.mp4" % name,
         ["-vf", "scale=1600:-2", "-c:v", "libx264", "-crf", "30", "-preset", "slow",
          "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]),
        ("%s.webm" % name,
         ["-vf", "scale=1600:-2", "-c:v", "libvpx-vp9", "-crf", "47", "-b:v", "0",
          "-row-mt", "1", "-pix_fmt", "yuv420p"]),
        ("%s-sm.mp4" % name,
         ["-vf", "crop=ih*4/3:ih,scale=720:540", "-c:v", "libx264", "-crf", "28",
          "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
          "-movflags", "+faststart"]),
    ]
    for out_name, opts in jobs:
        path = os.path.join(OUT, out_name)
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-an"]
                       + opts + [path], check=True)
        print("  %-28s %5d KB" % (out_name, os.path.getsize(path) // 1024))

    # the poster: one frame, through Pillow so it lands as webp like the rest
    from PIL import Image
    tmp = os.path.join(OUT, "_poster.png")
    subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-frames:v", "1", "-vf", "scale=1600:-2", "-pix_fmt", "rgb24", tmp],
                   check=True)
    im = Image.open(tmp).convert("RGB")
    poster = os.path.join(OUT, "%s-poster.webp" % name)
    im.save(poster, quality=82, method=5)
    im.resize((720, round(im.height * 720.0 / im.width)), Image.LANCZOS).save(
        os.path.join(OUT, "%s-poster-sm.webp" % name), quality=80, method=5)
    os.remove(tmp)
    print("  %-28s %5d KB" % (os.path.basename(poster), os.path.getsize(poster) // 1024))


if __name__ == "__main__":
    main()
