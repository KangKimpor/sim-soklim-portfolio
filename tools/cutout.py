#!/usr/bin/env python3
"""Cut the studio-white background out of the portrait photo.

Usage:
    python tools/cutout.py [src] [dst] [preview]

Defaults:
    src     = images/portrait.jpg          (or .png / .jpeg)
    dst     = images/portrait-cutout.png
    preview = images/_portrait-preview.png (cutout composited on navy)

Method:
  1. Strict flood fill from the image border across near-white, low-chroma
     pixels removes the open studio-white background. White clothing inside
     the subject (shirt, collar) is preserved because only border-connected
     regions are cleared.
  2. Some white pockets get sealed between hair strands by anti-aliased
     edge pixels the strict threshold cannot cross. A second flood pass
     grows from the cleared region through slightly darker "loose" pixels,
     but ONLY inside a band around dark hair in the head area, so the white
     shirt/jacket can never be reached. Remaining near-white pockets close
     to the cleared area inside that band are force-cleared.
  3. The mask is grown 2 px to remove the light halo, feathered 0.6 px for
     a soft edge, and the result is auto-cropped with a small margin.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

WHITE_MIN = 243     # strict "white background": every channel at least this
CHROMA_MAX = 20     # max channel spread allowed for strict white
LOOSE_MIN = 205     # relaxed brightness for growth through anti-aliased hair edges
LOOSE_CHROMA = 45   # relaxed chroma for the same
DARK_MAX = 90       # "dark" pixels: hair, eyebrows, jacket


def flood(mask, seeds):
    """Flood fill: all pixels of `mask` reachable from `seeds`."""
    seen = seeds & mask
    queue = deque(map(tuple, np.argwhere(seen)))
    h, w = mask.shape
    while queue:
        y, x = queue.popleft()
        if y > 0 and mask[y - 1, x] and not seen[y - 1, x]:
            seen[y - 1, x] = True; queue.append((y - 1, x))
        if y < h - 1 and mask[y + 1, x] and not seen[y + 1, x]:
            seen[y + 1, x] = True; queue.append((y + 1, x))
        if x > 0 and mask[y, x - 1] and not seen[y, x - 1]:
            seen[y, x - 1] = True; queue.append((y, x - 1))
        if x < w - 1 and mask[y, x + 1] and not seen[y, x + 1]:
            seen[y, x + 1] = True; queue.append((y, x + 1))
    return seen


def dilate(mask, size):
    img = Image.fromarray((mask * 255).astype(np.uint8), 'L')
    return np.asarray(img.filter(ImageFilter.MaxFilter(size))) > 0


def build_background(a):
    h, w = a.shape[:2]
    mn, mx = a.min(axis=2), a.max(axis=2)
    spread = mx - mn

    white = (mn >= WHITE_MIN) & (spread <= CHROMA_MAX)

    border = np.zeros((h, w), dtype=bool)
    border[0, :] = border[-1, :] = True
    border[:, 0] = border[:, -1] = True

    # Pass 1: open background reachable from the border.
    bg = flood(white, white & border)

    # Head-area band around dark hair (stops above the jacket so clothing
    # can never be reached by the relaxed growth).
    dark = mx < DARK_MAX
    cutoff = h - 1
    for y in range(int(h * 0.30), h):
        if dark[y].sum() > 0.25 * w:      # first row where the jacket starts
            cutoff = max(y - 12, 0)
            break
    band = dilate(dark, 25)
    band[cutoff:, :] = False

    # Pass 2: grow through anti-aliased hair edges to reach sealed pockets.
    loose = (mn >= LOOSE_MIN) & (spread <= LOOSE_CHROMA)
    bg = flood(white | (band & loose), bg)

    # Pass 3: force-clear near-white pockets inside the hair band that sit
    # close to already-cleared background (fully enclosed slivers).
    near_bg = dilate(bg, 19)
    extra = white & band & near_bg & ~bg
    bg |= extra

    return bg, cutoff, int(extra.sum())


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join('images', 'portrait.jpg')
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join('images', 'portrait-cutout.png')
    prev = sys.argv[3] if len(sys.argv) > 3 else os.path.join('images', '_portrait-preview.png')

    if not os.path.exists(src):
        print('ERROR: source photo not found:', src)
        raise SystemExit(1)

    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    bg, cutoff, extra = build_background(a)

    bg_img = Image.fromarray((bg * 255).astype(np.uint8), 'L')
    bg_img = bg_img.filter(ImageFilter.MaxFilter(5))       # grow 2 px -> eats halo
    alpha = bg_img.point(lambda v: 255 - v)                # invert -> subject
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))    # feathered edge

    out = im.convert('RGBA')
    out.putalpha(alpha)

    box = alpha.getbbox()
    if box:
        pad = 8
        box = (max(box[0] - pad, 0), max(box[1] - pad, 0),
               min(box[2] + pad, out.width), min(box[3] + pad, out.height))
        out = out.crop(box)
    out.save(dst)

    canvas = Image.new('RGB', out.size, (0, 40, 59))       # site navy #00283b
    canvas.paste(out, mask=out.split()[3])
    canvas.save(prev)

    total = out.width * out.height
    clear = int((np.asarray(out.split()[3]) == 0).sum())
    print('saved      :', dst)
    print('preview    :', prev)
    print('source     :', im.size, '-> cutout:', out.size)
    print('jacket row cutoff:', cutoff, '| forced-clear pixels:', extra)
    print('transparent: %.1f%% of pixels' % (100.0 * clear / total))


if __name__ == '__main__':
    main()
