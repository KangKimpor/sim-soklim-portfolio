# Sim Soklim portfolio

A static professional profile for a civil engineer and project control professional in Phnom Penh. The page presents verified CV content in an editorial layout: overview, selected projects, experience, expertise and education, then contact.

Archivo is used for body text and interface labels; Source Serif 4 is used for the name. Both fonts ship locally. The portrait is the existing CV photo. The 1200 × 630 social card is original typography, with its source in `tools/social-card.html` and `tools/social-card.css`.

The project section shows three featured projects and three additional projects. BP02, BP03 and BP04 are work packages under Pan Pacific Hotel / Norodom Business Center, available through the native “Hotel work packages” disclosure. Employment dates are kept in the experience section; only the National Assembly project carries the source's explicit completion status. Each of the four roles has three concise responsibilities; the CV retains the detailed history.

## Run and check

Open `index.html` directly, or serve this folder:

```sh
python -m http.server 8000
```

Open `http://localhost:8000`. There are no dependencies or build steps.

```sh
python tools/_validate.py
node --check js/script.js
```

The validator checks local assets, markup and anchor wiring, offline loading, strict CSP compatibility, source privacy, project/package hierarchy, CV facts and share metadata. Browser review is described in `REVIEW_CHECKLIST.md`; offline review is described in `OFFLINE_REVIEW.md`.

## Files and behaviour

`index.html`, `css/style.css` and `js/script.js` are the complete site. CSS is consolidated into one file. JavaScript manages the accessible mobile dialog, active section links, portrait fallback and copyright year. Native links handle section navigation, CV downloads and contact. The page remains usable without JavaScript; the navigation wraps into the header instead of opening a menu.

The layout uses a 1160 px maximum content width, 48 px desktop gutters and 20 px phone gutters. Navigation becomes a menu at 1000 px, hero and project columns stack at 900 px, and the remaining columns stack at 600 px. Controls are at least 44 px high; primary actions are 48 px. Reduced motion disables smooth scrolling. Print styles remove navigation and actions.

The downloaded `assets/Sim-Soklim-CV.pdf` is the existing redacted public copy. Referee details are absent from the HTML, including comments. The original CV, portrait source files, tools and review documents are excluded from deployment by `.vercelignore`. Keep those exclusions: Vercel uploads from the working directory, so `.gitignore` alone does not protect a stray local file.

## Deployment

The production address is [sim-soklim-portfolio.vercel.app](https://sim-soklim-portfolio.vercel.app/), hosted by the LIM team's `sim-soklim-portfolio` project. Canonical, social metadata, robots and sitemap use that address. `vercel.json` sets a strict Content Security Policy, security headers and asset caching.

The Vercel project is connected to `KangKimpor/sim-soklim-portfolio`; pushes to `main` deploy to production. Validate locally before pushing, then run `python tools/_validate_live.py` to check the live page, headers and excluded paths. `.vercel/`, including local CLI authentication, is excluded from Git and deployment uploads.
