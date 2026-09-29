# Sim Soklim — Review Build (offline-first)

A single-page review site for **Sim Soklim**, Civil Engineer · Project Control.
Plain HTML5, CSS3 and vanilla JavaScript. No build step, no framework, no
package manager, and **zero network requests** once the folder is on disk.

Open `index.html` in any modern browser and the whole page renders: fonts,
icons, imagery, styles and the downloadable CV are all local files.

Repository: <https://github.com/KangKimpor/sim-soklim-portfolio> ·
Deployment: see section 8.

---

## 1. Reviewing this build

| Goal | How |
| --- | --- |
| Quick look | Double-click `index.html` (works from `file://`, a USB stick or a ZIP) |
| Best fidelity | Serve the folder, e.g. `python -m http.server 8000` then open `http://localhost:8000` |
| Offline proof | Follow `OFFLINE_REVIEW.md` (turn off Wi-Fi, reload, check the network panel) |
| Acceptance pass | Work through `REVIEW_CHECKLIST.md` |
| Automated checks | `python tools/_validate.py` — prints `RESULT: ALL OK` when clean |

Requirements: a current Chrome, Edge, Firefox or Safari. Nothing else.

---

## 2. File map

```
index.html                 the entire site (semantic, single page)
css/style.css              design tokens + all layout and component styles
js/script.js               drawer nav, scroll-spy, scroll progress, portrait fallback, footer year
fonts/                     7 self-hosted .woff2 files (3 families, 231 KB)
images/
  hero.webp                featured band image  (PLACEHOLDER - see section 5)
  og-hero.jpg              social sharing card (PLACEHOLDER - see section 5)
  portrait-cutout.webp     portrait used on the page
  portrait.jpg             portrait source extracted from the CV
  portrait.png             portrait source
  portrait-cutout.png      cutout with transparency (source of the .webp)
  _portrait-preview.png    QA artefact: cutout composited on navy, never served
assets/Sim-Soklim-CV.pdf   the curriculum vitae, offered as a download
tools/
  _validate.py             structural, offline, token and content checks
  fetch_fonts.py           re-vendors the typefaces (the only network-touching tool)
  cutout.py                rebuilds the portrait cutout from images/portrait.jpg
  optimize_images.py       re-encodes gallery photos / hero (no galleries in this build)
README.md  OFFLINE_REVIEW.md  REVIEW_CHECKLIST.md
```

Total on disk is well under 1 MB of images and fonts plus the 180 KB CV.

---

## 3. Page structure

| # | Section | id | Content |
| --- | --- | --- | --- |
| 00 | Overview | `#overview` | Role line, headline, summary, four actions, portrait plate with key-facts spec table |
| — | Featured band | — | Wide construction image, project caption and a review-build marker |
| 01 | Experience & Education | `#experience-and-education` | Left-rail timeline of four roles (projects plus key responsibilities) with study alongside |
| 02 | Core Competencies | `#core-competencies` | Nine competencies in two numbered columns, then the tools |
| 03 | Selected Projects | `#selected-projects` | Nine-row project register with reference numbers, role and status |
| 04 | Contact | `#contact` | Channels, availability, and a navy call-to-action band for the CV |
| 05 | References | `#references` | **Commented out** — see section 4 |
| — | Footer | — | Summary, section links, spec sheet, provenance line, CV download |

### Design language

"Technical Dossier": the page behaves like a drawing set rather than a
brochure. Warm paper (`#f4f3f0`) and near-black ink (`#0d1116`), one copper
accent (`#a8562a`) reserved for indices, rules and active states, and deep navy
(`#16243a`) carrying the weight in the drawer and the call-to-action band. A
160 px tile of fractal-noise grain sits over the whole page at ~1.5% so the
paper reads as paper rather than as a flat hex value.

Structure comes from hairlines and markers rather than shadows: a 72 px
blueprint grid fades behind the hero, the portrait sits in a plate with four
corner registration marks and a `Fig. 01` caption, the career history runs down
a hairline spine with square nodes and a mono date gutter, and the project
register is numbered `01` to `09` like a schedule sheet. Radii stay between 2
and 5 px.

Colour only ever carries meaning in the two status pills: *Present* (amber,
with a pulsing dot) and *Completed* (green). Everything else is neutral.

#### Type system

Three faces, each with one job, all self-hosted and subset to latin:

| Role | Face | Where |
| --- | --- | --- |
| Structure / interface | **Archivo** 500·600·700 | headings, name, buttons, navigation, entry and register titles, data values |
| Prose | **Source Serif 4** 400·600 | ledes, paragraphs, responsibility lists, notes, footer copy |
| Annotation | **DM Mono** 400·500 | eyebrows, labels, reference numbers, dates, status pills, captions |

The serif body is a deliberate choice: it puts the page in the register of a
prepared document rather than a web page, and at 16.5 px / 1.7 it is more
comfortable than a sans for the long responsibility lists. DM Mono ships only
400 and 500, so no rule asks for a heavier mono weight — a synthetic bold would
smudge the labels. Layout caps at `1200px`; the two display faces are preloaded
so first paint is not reflowed.

Numbers in the mono and data roles carry `font-variant-numeric: tabular-nums`,
so dates, reference numbers and phone numbers line up in columns.

Animation is limited to a staggered hero reveal, a hero hairline that draws
itself, the status beacon, and a scroll-driven reveal for section heads and
registers — all suppressed under `prefers-reduced-motion` and the scroll-driven
part guarded by `@supports (animation-timeline: view())`.

### Print

A real print stylesheet ships with the build: `@page` margins, the navigation,
buttons and the navy band removed, grain and blueprint grid switched off,
hairline borders preserved, `break-inside: avoid` on every card, timeline item
and register row. The page prints or saves to PDF as a tidy multi-page document
instead of a screenshot of a website.

### JavaScript behaviour (all progressive enhancement)

* Mobile drawer: opens from the burger, moves focus to the close button, closes
  on backdrop click, link click or `Escape`; the closed panel is `inert`, so its
  links are unreachable by keyboard and screen reader.
* Scroll-spy: an `IntersectionObserver` marks the matching nav item `is-active`.
* Scroll progress: a 2 px copper rule under the top bar fills with reading
  progress, throttled through `requestAnimationFrame`.
* Portrait fallback: if `portrait-cutout.webp` is missing, `js/script.js` adds
  `.is-empty` to the plate and the CSS reveals the `SS` monogram instead of a
  broken image.
* Footer year comes from the visitor's clock; "Back to top" scrolls and updates
  the hash.

With JavaScript disabled the page still reads top to bottom, every link works,
the progress rule simply stays empty, and mobile navigation falls back to the
footer links.

---

## 4. Content provenance

Every biographical fact on the page comes from `assets/Sim-Soklim-CV.pdf`
(5 pages: covering letter + CV). Roles, employers, dates, project names,
responsibilities, education, trainings, competencies and all contact details
are transcribed from that document. Editorial changes are limited to:

* expanding month abbreviations (`Aug` → `August`, `Mar` → `March`);
* the employer name rendered as `SingBuild Construction` (the CV uses
  `SINGBUILD` in the role heading and both casings in the reference list);
* CV typos corrected, e.g. `ASSITANT TO PROJECT MANAGER` →
  *Assistant to Project Manager*;
* en dashes used as separators, matching the CV's own punctuation;
* descriptive bullet copy under Education and Trainings was **removed**, so the
  Study column states only what the CV states. The one remaining bullet under
  the Civil Quantity Surveyor certificate is the covering letter's own wording
  about cost awareness and budget-related project control;
* the application-specific sentence of the covering letter ("Seeking to
  contribute … to VET Charging Station's growing infrastructure operations") is
  omitted: a portfolio should not name one employer's application;
* the hero summary is the CV's own professional summary, unedited — including
  "Proficient in Microsoft Project". The CV evidences *training*, not a
  certification, so soften that phrase if he prefers.

**References are intentionally not published.** Section 05 sits inside an HTML
comment and contains all five referees from the CV. To publish it, delete the
`<!--` and `-->` around that block. `tools/_validate.py` fails while the section
is visible, so it cannot be published by accident.

**The downloadable CV is redacted to match.** The supplied PDF also carries
those five direct numbers, so shipping it as-is would undo the page's own
position. `tools/make_public_cv.py` produces `assets/Sim-Soklim-CV.pdf` from the
unredacted original: it deletes the text objects in the References block with
PyMuPDF redactions, leaving the AutoCAD/DCD training above it intact, and then
verifies that no referee name or number survives while the employers,
education and trainings still do. The unredacted file stays at
`assets/Sim-Soklim-CV-original.pdf` and is listed in `.gitignore`, so it never
enters git history or a deployment. Note that the CV's own Professional Summary
names the employer the covering letter was written for; that sentence is
removed from the page, not from the PDF.

---

## 5. Placeholders the client must replace

| File | What it is now | Replace with |
| --- | --- | --- |
| `images/hero.webp` | Stand-in construction imagery, captioned to the two landmark projects | A licensed photograph, or a photo of Sim on site |
| `images/og-hero.jpg` | Crop of the same stand-in image, used when the page is shared | A 1200 × 630 branded card |
| `images/portrait-cutout.webp` | Real portrait, cut out of the CV PDF | A higher-resolution studio portrait, re-cut with `tools/cutout.py` |

The band image's `alt` text describes the projects rather than claiming the
image shows them, and the caption carries a visible "Review build · placeholder
photography" marker. Both should be updated when real photography is supplied;
deleting the marker is a one-line change in `index.html`.

---

## 6. Re-running the tools

```bash
# structural, offline, design-token and content checks
python tools/_validate.py

# re-vendor the typefaces (the only tool that needs the network)
python tools/fetch_fonts.py
python tools/fetch_fonts.py --list     # show the faces without downloading

# rebuild the transparent portrait from images/portrait.jpg
python tools/cutout.py

# re-encode project photos / hero (this build ships no galleries)
python tools/optimize_images.py
```

`cutout.py` needs `Pillow` and `numpy`; `optimize_images.py` needs `Pillow`.
Neither is required to view the site, and the fonts are already vendored, so
**nothing in the review path touches the network**.

---

## 7. Third-party assets and licences

| Asset | Source | Licence / action needed |
| --- | --- | --- |
| Archivo, Source Serif 4, DM Mono (7 `.woff2` files in `fonts/`) | Google Fonts, vendored with `tools/fetch_fonts.py` | SIL Open Font License 1.1 — free to self-host and ship; keep the family names if the fonts are modified |
| `images/portrait-cutout.webp` | Extracted from the supplied CV | Confirm Sim Soklim is happy for this photo to appear publicly **[client]** |
| `images/hero.webp`, `images/og-hero.jpg` | Stand-in construction imagery supplied with this build | **Replace, or obtain written permission for the current images** |
| `assets/Sim-Soklim-CV.pdf` | Redacted copy of the supplied CV: the five referees' names and direct numbers are deleted, the AutoCAD training is kept | Confirm the CV is cleared for publication **[client]** |
| `assets/Sim-Soklim-CV-original.pdf` | Unredacted original, **git-ignored and never deployed** | Keep private. Do not commit it |
| Paper grain (inline SVG `feTurbulence` data URI) | Generated in CSS | None — no request, no asset, nothing to licence |

No icon set, no stock photos and no third-party JavaScript are included; the
icons are hand-drawn paths in the inline SVG sprite inside `index.html`.

---

## 8. Deploying

The site is a plain static folder, so any static host serves it as-is. No build
command, no output directory, no environment variables, no secrets.

### Vercel, importing the repository (recommended)

1. Sign in at <https://vercel.com> and choose **Add New → Project**.
2. Import `KangKimpor/sim-soklim-portfolio`.
3. Vercel detects no framework, which is correct. Leave **Build Command**
   empty, **Output Directory** as `public`-less root (i.e. leave it unset /
   `.`), and **Install Command** empty.
4. Deploy. Every later push to `main` redeploys automatically.

`vercel.json` in the repo root sets `cleanUrls`, disables trailing slashes, and
adds the response headers: a strict `Content-Security-Policy`
(`default-src 'self'`, no `connect-src` and no `form-action`, which the page
does not need), `X-Content-Type-Options`, `Referrer-Policy` and
`Permissions-Policy`. It also sets cache lifetimes of 30 days for `/fonts` and
7 days for `/images`.

The cache windows are deliberately conservative: those filenames are stable
rather than content-hashed (`hero.webp`, not `hero.a1b2.webp`), so a one-year
`immutable` header would leave browsers holding a replaced file. If you swap an
image or a font under the same name, either rename it or version the URL.

The policy is compatible with the page because it has no inline `<script>`,
no `style` attributes and no `on*` handlers; `img-src` allows `data:` only for
the inlined paper grain. `tools/_validate.py` checks exactly that, and fails if
an inline script, style attribute, event handler or remote resource is ever
introduced, so the policy cannot silently break the page.

### Vercel, from the command line

```bash
vercel login                    # one-off, opens a browser
vercel deploy --prod            # or: npx vercel --prod
```

PowerShell blocks the `vercel.ps1` shim under the default execution policy;
call the `.cmd` shim directly or relax the policy:

```powershell
& "$env:APPDATA\npm\vercel.cmd" --prod
```

### Vercel, through the Vercel MCP server

A `vercel` MCP server is registered in Cline's settings at
`https://mcp.vercel.com`. It stays inert until OAuth is completed: while
`authorizationRequired` is true in `cline_mcp_settings.json`, the server
exposes no tools to the agent, so a deploy cannot be driven from chat. Finish
it once in the MCP panel (Authorize / Connect, which opens Vercel in a
browser), after which the deployment tools become available and `vercel.json`
in this repo is picked up unchanged.

Note that all three routes need a human at a browser exactly once. That is
Vercel's design: none of them will hand an agent a working token unattended.

### Anything else

Upload the folder as-is: GitHub Pages, Cloudflare Pages, Netlify, S3 + CloudFront
or a shared-hosting `public_html`. The only thing to change for a canonical
domain is `og:url` / `twitter:url` in `index.html`, which this build
deliberately omits.

### Before the first public deploy

* `python tools/_validate.py` → `RESULT: ALL OK`
* `python tools/make_public_cv.py` → `leaked: none`, `missing: none`
* Confirm `assets/Sim-Soklim-CV-original.pdf` is git-ignored, so the referees'
  numbers cannot be served
* Replace the placeholder photography (section 5), or obtain written permission
  for the images currently in place


