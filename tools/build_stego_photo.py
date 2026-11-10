#!/usr/bin/env python3
"""Officer-only reproducible build for the NYITSec synthetic steghide puzzle.

Run this on Ubuntu 24.04 with Python Pillow and the steghide package installed.
Artifacts are verified by extracting the hidden note before they are committed.
"""

from __future__ import annotations

from pathlib import Path
import math
import os
import random
import re
import shutil
import subprocess
import tarfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "level-2" / "steg-photo"
BUILD = ROOT / ".tmp-steg-build"
PASSPHRASE = "cookie-jar"
SOLUTION = "PHOTO-CRUMB-26"


def draw_evidence_photo(path: Path) -> None:
    """Create a synthetic cookie still-life, with enough texture for steghide."""
    rng = random.Random(20261110)
    width, height = 960, 640
    im = Image.new("RGB", (width, height))
    p = im.load()
    for y in range(height):
        grain = 7 * math.sin(y * .12) + 4 * math.sin(y * .028)
        for x in range(width):
            noise = rng.randint(-12, 12) + grain + 3 * math.sin(x * .02)
            p[x, y] = (
                max(0, min(255, int(94 + noise))),
                max(0, min(255, int(66 + noise * .76))),
                max(0, min(255, int(48 + noise * .59))),
            )

    d = ImageDraw.Draw(im)
    # Ceramic plate and a set of overlapping home-baked cookies.
    d.ellipse((122, 70, 862, 600), fill=(39, 33, 29))
    d.ellipse((136, 62, 842, 576), fill=(222, 211, 186), outline=(240, 227, 210), width=12)
    d.ellipse((181, 100, 800, 530), outline=(194, 181, 159), width=9)
    positions = [(335, 267), (510, 214), (645, 311), (414, 420), (581, 433), (255, 380)]
    for index, (cx, cy) in enumerate(positions):
        rr = random.Random(index * 45 + 391)
        radius = 97 + rr.randrange(-9, 10)
        d.ellipse((cx-radius+9, cy-radius+13, cx+radius+9, cy+radius+13), fill=(124, 96, 67))
        d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(204, 151, 87), outline=(161, 104, 52), width=8)
        for j in range(55):
            angle = rr.random() * math.tau
            rad = rr.random() ** 0.5 * (radius - 17)
            x = int(cx + rad * math.cos(angle))
            y = int(cy + rad * math.sin(angle))
            w = rr.randint(3, 9)
            d.ellipse((x-w,y-w,x+w,y+w), fill=rr.choice([(75,45,32),(88,48,30),(112,61,32),(139,90,49)]))
        for j in range(22):
            angle=rr.random()*math.tau
            rad=rr.random()*(radius-12)
            x=int(cx+rad*math.cos(angle))
            y=int(cy+rad*math.sin(angle))
            d.ellipse((x-2,y-1,x+3,y+2),fill=(232,190,121))
    # Food-scene JPEG, with no readable answer text in its visible pixels.
    im.save(path, "JPEG", quality=90, subsampling=0, optimize=True)


def runtime_bundle(output: Path) -> None:
    binpath = shutil.which("steghide")
    if not binpath:
        raise RuntimeError("Install the steghide package before building this challenge")
    bundle = BUILD / "runtime"
    libs = bundle / "lib"
    libs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binpath, bundle / "steghide")

    lines = subprocess.check_output(["ldd", binpath], text=True).splitlines()
    included = []
    for line in lines:
        match = re.search(r"(?:=>\s*)?(/[^ ]+)", line)
        if not match:
            continue
        library = Path(match.group(1))
        name = library.name
        if name.startswith(("libc.so", "libm.so", "ld-linux", "libpthread.so", "libdl.so", "libresolv.so")):
            continue
        shutil.copyfile(library, libs / name, follow_symlinks=True)
        included.append(name)

    if not any(s.startswith("libmcrypt") for s in included):
        raise RuntimeError("The steghide dynamic libmcrypt dependency was not bundled")
    if not any(s.startswith("libmhash") for s in included):
        raise RuntimeError("The steghide dynamic libmhash dependency was not bundled")

    with tarfile.open(output, "w:gz") as tar:
        tar.add(bundle / "steghide", arcname="steghide")
        for path in sorted(libs.iterdir()):
            tar.add(path, arcname=f"lib/{path.name}")


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    cover = BUILD / "cover.jpg"
    hidden = BUILD / "hidden-note.txt"
    embedded = OUTPUT / "evidence.jpg"

    draw_evidence_photo(cover)
    hidden.write_text(
        "NYITSec Evidence Review (synthetic)\n"
        "A normal-looking image can conceal a separate file.\n"
        f"Response code: {SOLUTION}\n",
        encoding="utf-8",
    )
    subprocess.run([
        "steghide", "embed", "-cf", str(cover), "-ef", str(hidden),
        "-sf", str(embedded), "-p", PASSPHRASE, "-f"
    ], check=True)

    recovered = BUILD / "recovered-note.txt"
    subprocess.run([
        "steghide", "extract", "-sf", str(embedded),
        "-xf", str(recovered), "-p", PASSPHRASE, "-f"
    ], check=True)
    if recovered.read_bytes() != hidden.read_bytes():
        raise AssertionError("Steghide extraction did not recover the correct bytes")

    bundle = OUTPUT / ".steghide-runtime.tar.gz"
    runtime_bundle(bundle)
    print(f"Generated verified stego JPEG: {embedded} ({embedded.stat().st_size} bytes)")
    print(f"Generated portable tool bundle: {bundle} ({bundle.stat().st_size} bytes)")
    print("Recovery check: OK")


if __name__ == "__main__":
    main()
