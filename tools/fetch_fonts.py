#!/usr/bin/env python3
"""Vendor the site's typefaces into fonts/ as self-hosted woff2 files.

The site must render with no network access, so it never links Google Fonts at
run time. This script is the only part of the build that touches the network:
it runs once whenever the type system changes, and the resulting files are
committed alongside the site.

Usage:
    python tools/fetch_fonts.py            # download the latin subset of each face
    python tools/fetch_fonts.py --list     # show what would be fetched, no writes

Method: ask the Google Fonts CSS API for the families and weights below with a
modern browser User-Agent (so it answers with woff2 rather than legacy
formats), keep only the `/* latin */` @font-face block of each weight, and save
its woff2 to fonts/<FamilyPrefix>-<weight>.woff2. The latin subset already
covers general punctuation (U+2000-206F), which is where the en dashes and
middle dots used across the page live.

All three families are SIL Open Font License 1.1, which permits self-hosting.
"""
import os
import re
import sys
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

API = ("https://fonts.googleapis.com/css2"
       "?family=Archivo:wght@500;600;700"
       "&family=Source+Serif+4:wght@400;600"
       "&family=DM+Mono:wght@400;500"
       "&display=swap")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# CSS family name -> file prefix
PREFIX = {
    "Archivo": "Archivo",
    "Source Serif 4": "SourceSerif4",
    "DM Mono": "DMMono",
}


def get(url, binary=False):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
    return payload if binary else payload.decode("utf-8")


def faces(css):
    """Yield (family, weight, url) for every latin @font-face block."""
    pattern = re.compile(
        r"/\*\s*(?P<subset>[\w-]+)\s*\*/\s*@font-face\s*\{(?P<body>[^}]+)\}", re.S)
    for match in pattern.finditer(css):
        if match.group("subset") != "latin":
            continue
        body = match.group("body")
        family = re.search(r"font-family:\s*'([^']+)'", body)
        weight = re.search(r"font-weight:\s*(\d+)", body)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body)
        if family and weight and url:
            yield family.group(1), int(weight.group(1)), url.group(1)


def main():
    listing_only = "--list" in sys.argv
    print("requesting", API.split("?")[0])
    css = get(API)

    os.makedirs(FONT_DIR, exist_ok=True)
    kept, total = [], 0
    for family, weight, url in faces(css):
        prefix = PREFIX.get(family)
        if not prefix:
            print("  skipping unknown family:", family)
            continue
        name = "%s-%d.woff2" % (prefix, weight)
        target = os.path.join(FONT_DIR, name)
        if listing_only:
            print("  would fetch %s  (%s %d)" % (name, family, weight))
            continue
        data = get(url, binary=True)
        with open(target, "wb") as fh:
            fh.write(data)
        total += len(data)
        kept.append(name)
        print("  %-26s %6.1f KB  %s %d" % (name, len(data) / 1024.0, family, weight))

    if listing_only:
        return 0

    print("\n%d files, %.0f KB total" % (len(kept), total / 1024.0))
    stale = [f for f in sorted(os.listdir(FONT_DIR))
             if f.lower().endswith(".woff2") and f not in kept]
    if stale:
        print("not part of this type system (delete if unused):", ", ".join(stale))
    print("now point the @font-face rules in css/style.css at fonts/" +
          ", fonts/".join(sorted(kept)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
