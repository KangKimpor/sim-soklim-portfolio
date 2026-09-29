#!/usr/bin/env python3
"""Resize and re-encode the site's photos for the web.

Usage:
    python tools/optimize_images.py [slug ...]

Gallery photos land in images/projects/<slug>/ straight from a camera or phone:
4-8 MB each, up to 4000x3000 px, so one gallery used to weigh 96 MB. This tool
resizes each photo to fit 1600 px on the long edge (roughly what the card and
the lightbox display, with a little headroom) and encodes it as WebP at
quality 76, then removes the oversized source. Files typically come out
15-30x smaller with no visible difference at the sizes the site shows. Pass
one or more slugs to limit the run.

The same pass rebuilds images/hero.webp from images/hero.jpg (2400 px wide,
quality 82) plus the 1200x630 social card images/og-hero.jpg that the og:image
and twitter:image tags point at.

Finally it rewrites js/gallery-manifest.js from the folders on disk, which is
what js/script.js uses to build the gallery and lightbox URLs.

Oversized sources stay in git history, so a conversion can always be undone.
Requires Pillow (already used by tools/cutout.py).
"""
import json
import os
import sys

from PIL import Image, ImageOps

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_ROOT = os.path.join(REPO_ROOT, "images", "projects")
MANIFEST = os.path.join(REPO_ROOT, "js", "gallery-manifest.js")
HERO_SRC = os.path.join(REPO_ROOT, "images", "hero.jpg")
HERO_DST = os.path.join(REPO_ROOT, "images", "hero.webp")
OG_DST = os.path.join(REPO_ROOT, "images", "og-hero.jpg")

GALLERY_MAX = 1600          # px on the long edge
GALLERY_QUALITY = 76
HERO_MAX = 2400
HERO_QUALITY = 82
OG_CARD = (1200, 630)       # 1.91:1, the size social cards expect
SOURCE_EXT = (".jpg", ".jpeg", ".png")


def kb(size):
    return size / 1024.0


def fit(img, max_edge):
    """Scale down so the long edge is at most max_edge px. Never upscale."""
    width, height = img.size
    longest = max(width, height)
    if longest <= max_edge:
        return img
    scale = max_edge / float(longest)
    size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))
    return img.resize(size, Image.LANCZOS)


def load(src):
    """Open a photo upright, as RGB or RGBA, keeping its colour profile.

    exif_transpose matters: phone and camera photos carry an orientation tag
    that browsers apply to JPEG but that would be lost on re-encode, which
    would leave rotated photos in the galleries.
    """
    raw = Image.open(src)
    icc = raw.info.get("icc_profile")
    img = ImageOps.exif_transpose(raw)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    return img, icc


def encode(src, dst, fmt="WEBP", max_edge=GALLERY_MAX, quality=GALLERY_QUALITY, crop=None):
    """Resize src and write it to dst. Returns (size, bytes_before, bytes_after)."""
    img, icc = load(src)
    img = ImageOps.fit(img, crop, Image.LANCZOS, centering=(0.5, 0.4)) if crop else fit(img, max_edge)
    options = {"quality": quality}
    if fmt == "WEBP":
        options["method"] = 6
    if fmt == "JPEG":
        options["optimize"] = True
        options["progressive"] = True
        if img.mode != "RGB":
            img = img.convert("RGB")
    if icc:
        options["icc_profile"] = icc
    img.save(dst, fmt, **options)
    return img.size, os.path.getsize(src), os.path.getsize(dst)


def optimize_galleries(only=None, log=print):
    """Convert every gallery photo in place to a web-sized WebP."""
    before_total = after_total = converted = kept = 0
    for slug in sorted(os.listdir(GALLERY_ROOT)):
        folder = os.path.join(GALLERY_ROOT, slug)
        if not os.path.isdir(folder) or (only and slug not in only):
            continue
        slug_before = slug_after = 0
        for name in sorted(os.listdir(folder)):
            stem, ext = os.path.splitext(name)
            if ext.lower() not in SOURCE_EXT:
                continue
            src = os.path.join(folder, name)
            dst = os.path.join(folder, stem + ".webp")
            size, before, after = encode(src, dst)
            if after < before:
                os.remove(src)
                slug_before += before
                slug_after += after
                converted += 1
                log("  %s %s -> %dx%d webp  %.0f KB -> %.0f KB"
                    % (slug, name, size[0], size[1], kb(before), kb(after)))
            else:
                os.remove(dst)
                kept += 1
                log("  %s %s kept (WebP was not smaller)" % (slug, name))
        if slug_before:
            before_total += slug_before
            after_total += slug_after
            log("%s: %.1f MB -> %.1f MB" % (slug, slug_before / 1048576.0, slug_after / 1048576.0))
    log("galleries: %d photos converted, %d left as-is, %.1f MB -> %.1f MB (%.0f%% smaller)"
        % (converted, kept, before_total / 1048576.0, after_total / 1048576.0,
           (1 - after_total / float(before_total or 1)) * 100))


def optimize_hero(log=print):
    """Build the hero WebP and the social card from images/hero.jpg."""
    if not os.path.isfile(HERO_SRC):
        log("hero: images/hero.jpg not found, nothing to convert")
        return
    size, _, after = encode(HERO_SRC, OG_DST, fmt="JPEG", quality=85, crop=OG_CARD)
    log("social card: images/og-hero.jpg %dx%d %.0f KB" % (size[0], size[1], kb(after)))
    size, before, after = encode(HERO_SRC, HERO_DST, quality=HERO_QUALITY, max_edge=HERO_MAX)
    log("hero: images/hero.webp %dx%d %.0f KB -> %.0f KB" % (size[0], size[1], kb(before), kb(after)))
    os.remove(HERO_SRC)


def write_manifest(log=print):
    """Regenerate js/gallery-manifest.js from the folders on disk."""
    data = {}
    for slug in sorted(os.listdir(GALLERY_ROOT)):
        folder = os.path.join(GALLERY_ROOT, slug)
        if not os.path.isdir(folder):
            continue
        files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".webp"))
        if files:
            data[slug] = files
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("/* Generated by tools/optimize_images.py - do not edit by hand.\n")
        fh.write("   Exact gallery filenames per project (WebP, web sizes). */\n")
        fh.write("window.GALLERY_FILES = ")
        fh.write(json.dumps(data, indent=2))
        fh.write(";\n")
    log("manifest: %d galleries -> %s" % (len(data), MANIFEST))


def main():
    only = set(a for a in sys.argv[1:] if not a.startswith("-"))
    if os.path.isdir(GALLERY_ROOT):
        optimize_galleries(only or None)
        write_manifest()
    else:
        print("images/projects is not present: this build ships no photo "
              "galleries, skipping them.", flush=True)
    optimize_hero()
    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
