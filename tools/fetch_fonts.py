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
the woff2 files into fonts/.

Two of the three families are variable fonts, and the API answers every weight
of a variable family with the *same* URL. Saving one file per weight therefore
just writes the same bytes under three names. So this script groups the weights
of a family by URL: a family whose weights all point at one file is stored once
as <Prefix>-var.woff2 (declare it with a font-weight range in CSS), and a
family with genuinely different files is stored per weight. The script prints
the @font-face weight range to paste for each variable family.

The latin subset already covers general punctuation (U+2000-206F), which is
where the en dashes and middle dots used across the page live.

All three families are SIL Open Font License 1.1, which permits self-hosting.
"""
import os
import re
import sys
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

# (CSS family name, file prefix, weights to ask for)
SPEC = [
    ("Archivo", "Archivo", [500, 600, 700]),
    ("Source Serif 4", "SourceSerif4", [400, 600]),
    ("DM Mono", "DMMono", [400, 500]),
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def api_url():
    parts = []
    for family, _prefix, weights in SPEC:
        parts.append("family=%s:wght@%s"
                     % (family.replace(" ", "+"), ";".join(str(w) for w in weights)))
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


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


def plan(css):
    """Group the requested weights by family, then by URL, oldest weight first.

    Returns [(family, prefix, [(name, url, weight, shared_with_n_families)]...)]
    ordered so a family is either a single variable file or one file per weight.
    """
    wanted = {family: (prefix, weights) for family, prefix, weights in SPEC}
    by_family = {}
    for family, weight, url in faces(css):
        if family not in wanted:
            continue
        by_family.setdefault(family, []).append((weight, url))

    out = []
    for family, prefix, _weights in SPEC:
        entries = sorted(by_family.get(family, []))
        if not entries:
            print("  warning: no latin block returned for", family)
            continue
        distinct = {url for _w, url in entries}
        if len(distinct) == 1:
            # One file for the whole family: the API is serving a variable font.
            lo, hi = entries[0][0], entries[-1][0]
            out.append((family, prefix, [("%s-var.woff2" % prefix, entries[0][1], hi)]))
            print("  %s is variable: %d..%d all point at one file"
                  % (family, lo, hi))
        else:
            files = [("%s-%d.woff2" % (prefix, w), url, w) for w, url in entries]
            out.append((family, prefix, files))
    return out


def main():
    listing_only = "--list" in sys.argv
    url = api_url()
    print("requesting", url.split("?")[0])
    css = get(url)

    os.makedirs(FONT_DIR, exist_ok=True)
    kept, total, ranges = [], 0, []
    for family, prefix, files in plan(css):
        for name, href, weight in files:
            target = os.path.join(FONT_DIR, name)
            if listing_only:
                print("  would fetch %-24s (%s)" % (name, family))
                continue
            data = get(href, binary=True)
            with open(target, "wb") as fh:
                fh.write(data)
            total += len(data)
            kept.append(name)
            print("  %-24s %6.1f KB  %s" % (name, len(data) / 1024.0, family))
            if name.endswith("-var.woff2"):
                ranges.append((prefix, family, weight))

    if listing_only:
        return 0

    print("\n%d files, %.0f KB total" % (len(kept), total / 1024.0))
    for prefix, family, hi in ranges:
        print("  declare %s once with `font-weight: 400 %d;` in css/style.css"
              % (family, hi))
    stale = [f for f in sorted(os.listdir(FONT_DIR))
             if f.lower().endswith(".woff2") and f not in kept]
    if stale:
        print("no longer part of this type system:", ", ".join(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
