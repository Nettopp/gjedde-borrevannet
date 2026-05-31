#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Komprimerer bilder fra Temp YEAR/ mapper til bilder/YEAR/web/,
oppdaterer captions.json, og sletter kildefiler.

Filnavn-strategi:
  - Facebook-nummererte filer (starter med siffer): generisk navn + "Gjeddefestivalen YEAR."
  - Beskrivende filnavn: sanitert versjon av filnavnet som navn og tekst
Bildestørrelse: maks 1920px, JPEG 85%
Minimumsfilstørrelse: 10 KB (hopper over ikoner/thumbnails)
"""
import os, re, json, shutil
from pathlib import Path

import pillow_heif
pillow_heif.register_heif_opener()
from PIL import Image, ImageOps
try:
    import rawpy
    _RAWPY_OK = True
except ImportError:
    _RAWPY_OK = False

BASE   = Path(__file__).parent / "bilder"
OUT    = Path(__file__).parent

MAX_PX       = 1920
JPEG_QUALITY = 85
MIN_BYTES    = 10_000

NO_CHAR = str.maketrans(
    "æøåÆØÅéèêëàáâäüúùûöóòô",
    "aoaAOAeeeeaaaauuuuoooo"
)

def safe_name(stem: str) -> str:
    """Lager ASCII filnavn med bare bokstaver, siffer og bindestreker."""
    s = stem.translate(NO_CHAR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "bilde"

def is_facebook_name(stem: str) -> bool:
    """Returnerer True hvis filnavnet er auto-generert (Facebook-ID, kamera-navn med ledende _)."""
    if re.match(r"^\d+_", stem) or re.match(r"^[0-9a-f]{32}$", stem, re.I):
        return True
    if stem.startswith("_"):  # Kamera-autogenerert navn, f.eks. _DSC4762
        return True
    return False

def compress(src: Path, dst: Path):
    if src.suffix.lower() == ".nef":
        if not _RAWPY_OK:
            raise RuntimeError("rawpy ikke installert — kan ikke lese NEF")
        with rawpy.imread(str(src)) as raw:
            rgb = raw.postprocess(use_camera_wb=True, output_bps=8)
        from PIL import Image as _PIL
        img = _PIL.fromarray(rgb)
    else:
        img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_PX:
        scale = MAX_PX / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)

# Les eksisterende captions.json
caps_file = OUT / "captions.json"
all_caps = {}
if caps_file.exists():
    all_caps = json.loads(caps_file.read_text(encoding="utf-8"))

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".nef"}

temp_dirs = sorted(d for d in BASE.iterdir() if d.is_dir() and re.match(r"[Tt]emp \d{4}$", d.name))
total_processed = 0
total_deleted   = 0

for temp_dir in temp_dirs:
    m = re.match(r"[Tt]emp (\d{4})$", temp_dir.name)
    if not m:
        continue
    year = int(m.group(1))

    files = sorted(
        f for f in temp_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTS
        and f.stat().st_size >= MIN_BYTES
    )
    skipped = [f for f in temp_dir.iterdir()
               if f.is_file() and f.stat().st_size < MIN_BYTES]

    if not files:
        print(f"\n{temp_dir.name}: ingen bilder (>={MIN_BYTES//1000} KB) funnet")
        continue

    web_dir = BASE / str(year) / "web"
    web_dir.mkdir(parents=True, exist_ok=True)

    # Tell eksisterende filer for å starte nummerering etter disse
    existing = sorted(web_dir.glob("*.jpg"))
    counter  = len(existing) + 1
    fb_nums = [int(m.group(1)) for f in existing
               if (m := re.match(r'festivalbilde-(\d+)\.jpg$', f.name))]
    fb_counter = max(fb_nums, default=0) + 1

    year_caps = all_caps.get(str(year), {})
    print(f"\n{temp_dir.name} -> bilder/{year}/web/  ({len(files)} bilder)")

    new_entries = {}

    for src in files:
        stem = src.stem
        ext  = src.suffix.lower()

        if is_facebook_name(stem) or stem.lower() == "last ned":
            dst_stem    = f"festivalbilde-{fb_counter:03d}"
            caption     = f"Gjeddefestivalen {year}."
            fb_counter += 1
        else:
            dst_stem = safe_name(stem)
            caption  = stem[0].upper() + stem[1:] + ("." if not stem.endswith(".") else "")

        dst_name = dst_stem + ".jpg"

        # Unngå navnekollisjon
        if dst_name in year_caps or (web_dir / dst_name).exists():
            dst_name = f"{dst_stem}-{counter:03d}.jpg"
        counter += 1

        dst = web_dir / dst_name
        try:
            compress(src, dst)
            new_entries[dst_name] = caption
            print(f"  {src.name[:55]:55s} -> {dst_name}  [{caption[:50]}]")
            total_processed += 1
        except Exception as e:
            print(f"  FEIL {src.name}: {e}")

    # Oppdater captions for dette året
    year_caps.update(new_entries)
    all_caps[str(year)] = year_caps

    # Slett kildefiler (inkl. for-små filer)
    for src in files:
        src.unlink()
        total_deleted += 1
    for src in skipped:
        print(f"  (slettet for-lite thumbnail: {src.name})")
        src.unlink()
        total_deleted += 1

print(f"\nTotalt prosessert: {total_processed}  Slettet fra Temp-mapper: {total_deleted}")

# Skriv oppdatert captions.json
caps_file.write_text(json.dumps(all_caps, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"captions.json oppdatert.")
