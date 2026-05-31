#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sort_takeout.py

Leser en Google Takeout-eksport, matcher bilder mot kjente festivaldatoer,
komprimerer og kopierer til bilder/YEAR/web/.

Bruk:
    python sort_takeout.py <sti-til-takeout-mappe>

Eksempel:
    python sort_takeout.py "C:/Users/kristian/Downloads/Takeout/Google Photos"
"""

import sys
import os
import json
import shutil
import math
import datetime
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow ikke installert. Kjoer: pip install Pillow")

# ---------------------------------------------------------------------------
# Festivaldatoer — fredag og lørdag utvides automatisk til to dager
# ---------------------------------------------------------------------------
def _build_festivals():
    start_dates = {
        2011: datetime.date(2011, 3, 10),
        2017: datetime.date(2017, 5, 24),
        2018: datetime.date(2018, 5, 26),
        2019: datetime.date(2019, 5, 25),
        2020: datetime.date(2020, 5, 15),
        2021: datetime.date(2021, 5, 22),
        2024: datetime.date(2024, 5, 24),
        2025: datetime.date(2025, 5, 23),
        2026: datetime.date(2026, 5, 29),
    }
    result = {}
    for year, start in start_dates.items():
        dates = [start]
        if start.weekday() in (4, 5):  # 4=fredag, 5=lørdag
            dates.append(start + datetime.timedelta(days=1))
        result[year] = dates
    return result

FESTIVALS = _build_festivals()

# Borrevannet koordinater
LAT = 59.4119
LON = 10.4677
MAX_DIST_KM = 10.0  # bilder innenfor 10 km inkluderes

# Bildeparametere
MAX_PX = 1920
JPEG_QUALITY = 85

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}

# ---------------------------------------------------------------------------
# Hjelpe-funksjoner
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def find_sidecar(img_path: Path):
    """Finner JSON-sidecar for et bilde (Takeout-format)."""
    candidates = [
        img_path.parent / (img_path.name + ".json"),
        img_path.parent / (img_path.stem + ".json"),
        # Takeout trunkerer lange filnavn til 46 tegn i JSON-navnet
        img_path.parent / (img_path.name[:46] + ".json"),
        img_path.parent / (img_path.stem[:46] + ".json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def photo_date_from_sidecar(sidecar: Path):
    """Returnerer datetime.date fra Takeout JSON-sidecar."""
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        ts = int(data.get("photoTakenTime", {}).get("timestamp", 0))
        if ts:
            return datetime.datetime.utcfromtimestamp(ts).date()
    except Exception:
        pass
    return None


def photo_gps_from_sidecar(sidecar: Path):
    """Returnerer (lat, lon) fra sidecar, eller None."""
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        geo = data.get("geoData") or data.get("geoDataExif") or {}
        lat = geo.get("latitude", 0.0)
        lon = geo.get("longitude", 0.0)
        if lat != 0.0 or lon != 0.0:
            return (lat, lon)
    except Exception:
        pass
    return None


def photo_date_from_exif(img_path: Path):
    """Fallback: les dato fra EXIF."""
    try:
        img = Image.open(img_path)
        exif = img._getexif() or {}
        # Tag 36867 = DateTimeOriginal
        raw = exif.get(36867) or exif.get(306)
        if raw:
            return datetime.datetime.strptime(raw[:10], "%Y:%m:%d").date()
    except Exception:
        pass
    return None


def match_festival(date: datetime.date):
    """Returnerer festivalar (int) hvis datoen matcher, ellers None."""
    for year, dates in FESTIVALS.items():
        if date in dates:
            return year
    return None


def compress_image(src: Path, dst: Path):
    """Komprimerer og resizer bildet til maks MAX_PX px bredde/hoyde."""
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)  # korriger EXIF-rotasjon

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > MAX_PX:
        scale = MAX_PX / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)


def safe_name(name: str, index: int):
    """Lager et sikkert filnavn fra originalt navn."""
    stem = Path(name).stem.lower()
    # erstatt mellomrom og spesialtegn med bindestrek
    safe = ""
    for c in stem:
        if c.isalnum() or c in "-_":
            safe += c
        else:
            safe += "-"
    # fjern doble bindestreker
    while "--" in safe:
        safe = safe.replace("--", "-")
    safe = safe.strip("-")
    if not safe:
        safe = f"bilde-{index:03d}"
    return safe + ".jpg"


# ---------------------------------------------------------------------------
# Hoved-logikk
# ---------------------------------------------------------------------------

def scan_takeout(takeout_root: Path):
    """Scanner Takeout-mappen rekursivt etter alle bilder."""
    images = []
    for p in takeout_root.rglob("*"):
        if p.suffix.lower() in IMAGE_EXTS and p.is_file():
            images.append(p)
    return images


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    takeout_root = Path(sys.argv[1])
    if not takeout_root.exists():
        sys.exit(f"Finner ikke: {takeout_root}")

    out_root = Path(__file__).parent / "bilder"

    print(f"Skanner {takeout_root} ...")
    images = scan_takeout(takeout_root)
    print(f"Fant {len(images)} bilder/videoer")

    # Kategoriser bilder
    matched   = {}   # year -> list of (src_path, date, gps_or_None)
    no_date   = []
    no_match  = []
    too_far   = []

    for img in images:
        if img.suffix.lower() in {".heic", ".heif"}:
            # HEIC krever tilleggspakke - hopp over
            continue

        sidecar = find_sidecar(img)
        date = None
        gps  = None

        if sidecar:
            date = photo_date_from_sidecar(sidecar)
            gps  = photo_gps_from_sidecar(sidecar)

        if date is None:
            date = photo_date_from_exif(img)

        if date is None:
            no_date.append(img)
            continue

        year = match_festival(date)
        if year is None:
            no_match.append((img, date))
            continue

        # GPS-sjekk: hvis GPS finnes og bildet er langt fra Borrevannet, hopp over
        if gps:
            dist = haversine_km(gps[0], gps[1], LAT, LON)
            if dist > MAX_DIST_KM:
                too_far.append((img, date, dist))
                continue

        matched.setdefault(year, []).append((img, date, gps))

    # ---------------------------------------------------------------------------
    # Kopier og komprimer
    # ---------------------------------------------------------------------------
    print()
    copied_total = 0

    for year in sorted(matched.keys(), reverse=True):
        items = matched[year]
        year_dir = out_root / str(year) / "web"
        year_dir.mkdir(parents=True, exist_ok=True)

        # Tell eksisterende filer for aa unngaa navnekollisjon
        existing = {p.name for p in year_dir.glob("*.jpg")}
        new_count = 0

        for idx, (src, date, gps) in enumerate(items, start=1):
            dst_name = safe_name(src.name, idx)
            # Unngaa aa overskrive eksisterende bilder
            if dst_name in existing:
                base = Path(dst_name).stem
                dst_name = f"{base}-{idx:03d}.jpg"

            dst = year_dir / dst_name

            try:
                compress_image(src, dst)
                existing.add(dst_name)
                new_count += 1
            except Exception as e:
                print(f"  FEIL {src.name}: {e}")

        print(f"  {year}: {new_count} bilder -> {year_dir}")
        copied_total += new_count

    # ---------------------------------------------------------------------------
    # Rapport
    # ---------------------------------------------------------------------------
    print()
    print(f"Ferdig. Kopierte {copied_total} bilder totalt.")

    if no_date:
        print(f"\n  {len(no_date)} bilder uten lesbar dato (sjekk manuelt):")
        for p in no_date[:10]:
            print(f"    {p.name}")
        if len(no_date) > 10:
            print(f"    ... og {len(no_date)-10} til")

    if too_far:
        print(f"\n  {len(too_far)} bilder for langt fra Borrevannet (>{MAX_DIST_KM} km):")
        for p, d, dist in too_far[:5]:
            print(f"    {p.name}  ({d}, {dist:.0f} km unna)")
        if len(too_far) > 5:
            print(f"    ... og {len(too_far)-5} til")

    if no_match:
        print(f"\n  {len(no_match)} bilder matchet ingen festivaldato:")
        # Grupper paa dato for oversikt
        by_date = {}
        for p, d in no_match:
            by_date.setdefault(d, 0)
            by_date[d] += 1
        for d in sorted(by_date.keys()):
            print(f"    {d}: {by_date[d]} bilder")

    # ---------------------------------------------------------------------------
    # Generer HTML-snippets
    # ---------------------------------------------------------------------------
    snippets_dir = Path(__file__).parent / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    for year, items in matched.items():
        year_dir = out_root / str(year) / "web"
        lines = ["<div class=\"photo-grid\">", ""]
        for dst_name in sorted(year_dir.glob("*.jpg"), key=lambda p: p.name):
            rel = f"bilder/{year}/web/{dst_name.name}"
            alt = dst_name.stem.replace("-", " ").capitalize()
            lines.append(f'  <figure>')
            lines.append(f'    <a href="{rel}" target="_blank"><img src="{rel}" alt="{alt}" loading="lazy"></a>')
            lines.append(f'    <figcaption>{alt}</figcaption>')
            lines.append(f'  </figure>')
            lines.append("")
        lines.append("</div>")
        snippet_path = snippets_dir / f"gallery-{year}.html"
        snippet_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  HTML-snippet: {snippet_path.name}")


if __name__ == "__main__":
    main()
