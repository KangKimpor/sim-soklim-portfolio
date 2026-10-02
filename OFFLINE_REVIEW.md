# Offline Review Guide

This build is meant to be reviewed with **no internet connection at all** — on a
plane, in a meeting room with no Wi-Fi, or from a USB stick handed to a
recruiter. This page explains how to prove that, and what to expect.

---

## 1. Why it is offline-first

* **No CDN, no external fonts, no analytics, no trackers, no web fonts.** Three
  type families ship as `.woff2` files in `fonts/` (Archivo, Source Serif 4 and
  DM Mono — 4 files, 113 KB in total) and are declared with local `@font-face`
  rules. Archivo and Source Serif 4 are variable faces, so one file each covers
  every weight the page uses.
  `tools/fetch_fonts.py` and `tools/_validate_live.py` are the only tools that
  ever use the network, and neither is part of the review path.
* **Icons are an inline SVG sprite.** `index.html` defines eight `<symbol>`
  elements (`ico-arrow-down`, `ico-arrow-up`, `ico-close`, `ico-mail`,
  `ico-phone`, `ico-linkedin`, `ico-download`, `ico-pin`) and reuses them with
  `<use>`, so there is no icon font or SVG request.
* **The paper grain is an inline SVG data URI** in `css/style.css`, so the
  texture costs no request either.
* **The CV is a local file** (`assets/Sim-Soklim-CV.pdf`) and downloads with a
  plain `download` attribute.
* **The only external destinations are things a person chooses to click**: the
  LinkedIn profile (`target="_blank" rel="noopener noreferrer"`), a `mailto:`
  address and a `tel:` number. Those are links, not resources; they are the
  only things on the page that need connectivity to do anything.

`tools/_validate.py` fails the build if a remote `src` or stylesheet/preload
link appears, so the offline property cannot regress silently.

---

## 2. How to review it offline

### Option A — straight from the folder (fastest)

1. Copy the whole `sim-soklim-portfolio` folder anywhere (USB stick, Desktop,
   a shared drive).
2. Double-click `index.html`.
3. Switch off Wi-Fi (or open DevTools → Network → **Offline**) and press
   reload. Nothing should change.

The page works from a `file://` origin: no modules, no `fetch`, no service
worker, no CORS-restricted resource.

### Option B — through a local server (closer to production)

```bash
cd sim-soklim-portfolio
python -m http.server 8000
# then open http://localhost:8000
```

### Option C — zip it

Right-click the folder → *Compress to ZIP* → send or copy the archive. Extract
and open `index.html`. Nested folders and filenames contain no spaces or
non-ASCII characters, so extraction on Windows, macOS or Linux is safe.

---

## 3. Verifying there are no network requests

1. Open DevTools (`F12`) → **Network**.
2. Tick **Preserve log**, then reload.
3. Every entry must be a relative path, and the list is limited to:
   `index.html`, `css/style.css`, `js/script.js`, `favicon.svg`,
   `images/hero.webp`, `images/portrait-cutout.webp`, and the `fonts/*.woff2`
   files the page actually renders (a subset of the four shipped). There is
   nothing else: no third-party origin, no font CDN, no tracking pixel.
4. Filter by **Fetch/XHR** and **WS**: both must be empty. The script makes no
   `fetch`, `XMLHttpRequest` or WebSocket calls.
5. The **Security** or **Application → Storage** panel should show no cookies,
   no localStorage and no service-worker registration.

Archivo and Source Serif 4 are single variable files, so one request each covers
every weight the page asks for; the two DM Mono cuts load only where a 400 or a
500 label is painted. All of that is expected and still entirely local. A full
first load (HTML + CSS + JS + images + favicon + every font) is about 350 KB
(0.35 MB), plus 190 KB if the CV is downloaded.

---

## 4. Behaviour without a network (and without JavaScript)

| Situation | What happens |
| --- | --- |
| No internet | Page renders identically; only the LinkedIn link is inert until you reconnect |
| No JavaScript | Full content, all links, footer navigation; the progress rule stays empty |
| Portrait file deleted | `SS` monogram is shown in its place (no broken-image icon) |
| `hero.webp` deleted | The band collapses to its caption; the rest of the page is unaffected |
| Print / Save as PDF | Print stylesheet drops the chrome and keeps the card structure |
| Very old browser | Content is fully readable; only the blueprint grid, `color-mix()` pill borders and the scroll-driven reveal are dropped |

---

## 5. Browser notes

* Tested markup targets current Chrome, Edge, Firefox and Safari.
* `color-mix()` is used to tint the status-pill borders; browsers without it
  keep the plain `rgba()` border declared immediately before, so the pills look
  the same, just with a slightly harder edge.
* The scroll-driven reveal sits behind
  `@supports (animation-timeline: view())`, so browsers without scroll
  timelines simply never run it.
* `mask-image` behind the hero grid and `mix-blend-mode: multiply` for the paper
  grain are both progressive: without them the page is a flat paper colour, and
  the grain does not affect legibility.
* `prefers-reduced-motion: reduce` switches off the beacon pulse, the hero
  reveal, the hover lifts and smooth scrolling.
* `inert` on the closed drawer is honoured by all current browsers; where it is
  unsupported the drawer is still `aria-hidden` and off-canvas. The open panel
  is a `role="dialog"` with `aria-modal` and its own `Tab` trap, so keyboard
  focus stays in the panel whether or not `inert` is supported.
* `scrollbar-gutter: stable` keeps the page from shifting sideways when the
  drawer locks scrolling behind it.
* Windows high contrast / forced-colours mode is not yet signed off — see
  `REVIEW_CHECKLIST.md`.

---

## 6. If you want to serve this publicly later

Nothing in the build prevents it: upload the folder as-is to any static host
(GitHub Pages, Netlify, S3 + CloudFront, a shared-hosting `public_html`). No
server-side code, no build output, no configuration is required. Only two
files would need updating at that point: `og:url` / `twitter:url` in
`index.html` and the links that currently point at the client's own profile.
