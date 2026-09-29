# Review Checklist

Work top to bottom. Tick the box only when you have actually seen it, then
record the outcome at the bottom. Items marked **[client]** can only be
confirmed by Sim Soklim.

---

## 1. Automated gate

- [ ] `python tools/_validate.py` ends with `RESULT: ALL OK`
- [ ] It prints **no `FAIL:` lines and no `note:` lines**: every class in the
      markup has a rule, every rule is used, and every design token is declared
      and referenced
- [ ] `node --check js/script.js` passes
- [ ] The `VET Charging Station` application line is not on the page
- [ ] The references section is still commented out (the validator fails if it
      is published)

## 2. Content accuracy — verify against `assets/Sim-Soklim-CV.pdf`

- [ ] Name spelled **Sim Soklim** everywhere
- [ ] Email `soklimlll@gmail.com` in hero, contact, drawer and footer
- [ ] Telephone `+855 95 810 472` (hero, contact, footer)
- [ ] LinkedIn `linkedin.com/in/soklim-sim-6589221a4` (contact, footer) and it
      opens the right profile
- [ ] Address `Phnom Penh, Cambodia`
- [ ] **Senior Project Coordinator** · SingBuild Construction · Nov 2025 – Present
- [ ] **Project Coordinator** · TCV Engineering Co., Ltd. · Apr 2022 – Aug 2025
- [ ] **Assistant to Project Manager** · Cana Sino Construction Corporation · May 2020 – Mar 2022
- [ ] **QA & QC Engineer** · Cana Sino Construction Corporation · Apr 2018 – Apr 2020
- [ ] All responsibility bullets match the CV wording (no invented duties)
- [ ] Projects: NBC – Pan Pacific Hotel; BP02; BP03; BP04; UVP2; National
      Assembly Building; Techo International Airport ATC & base building; The
      Elysee Building 3.5/3.6; Fly Over Bridge of Kbal Thnol
- [ ] Bachelor Degree of Civil Engineering · Norton University · 2017
- [ ] High School Diploma (National Baccalaureate – Bac II) · Bak Touk High School · 2012
- [ ] Trainings: Microsoft Project 2021 & Project Online (LinkedIn Learning, 2025),
      Civil Quantity Surveyor (Ecam School, 2019),
      AutoCAD 2D & 3D / Workshop / Mechanical Engineering (DCD Cambodia, 2014)
- [ ] All eleven core competencies present, none added
- [ ] Nothing on the page is missing from the CV **[client]**
- [ ] Nothing on the page is absent from the CV **[client]**

## 3. Privacy and consent

- [ ] Section 05 References is **not visible** on the page
- [ ] The commented block holds exactly the five CV referees with their CV numbers
- [ ] Decision recorded: publish references, or supply them on request only
- [ ] **[client]** Explicit consent obtained if references are to be published
- [ ] `assets/Sim-Soklim-CV.pdf` is the redacted copy: open it and confirm the
      References block is gone while the AutoCAD/DCD training is still there
- [ ] `python tools/make_public_cv.py` reports `leaked: none` and `missing: none`
- [ ] The downloaded PDF is confirmed to contain no referee name or number
      (select all, copy, paste into a text editor)
- [ ] `assets/Sim-Soklim-CV-original.pdf` is git-ignored and never deployed
- [ ] Portrait is the CV photo and is approved for the web **[client]**
- [ ] **[client]** Approval for the current job title, employers and dates
- [ ] **[client]** Acknowledge that the CV's Professional Summary names the
      employer its covering letter was written for; that stays in the PDF

## 4. Placeholders to replace before launch

- [ ] `images/hero.webp` — replace the stand-in construction image, or keep it
      with written permission, and update the `alt` text
- [ ] `images/og-hero.jpg` — replace with a 1200 × 630 card (check the preview
      when the link is pasted into a chat app)
- [ ] `images/portrait-cutout.webp` — optionally re-cut from a higher-resolution
      portrait with `python tools/cutout.py`
- [ ] Source files (`portrait.jpg`, `portrait.png`, `portrait-cutout.png`,
      `_portrait-preview.png`) removed or kept as documented

## 5. Layout and responsiveness

Breakpoints in use: 480 / 560 / 720 / 900 / 1180 px.

- [ ] 1440 px, 1280 px, 1180 px, 1024 px, 900 px, 768 px, 414 px, 375 px, 320 px
- [ ] Below 1000 px the top navigation collapses into the drawer
- [ ] Hero is a single column below 900 px, then headline beside a 300 px portrait plate
- [ ] Experience and Study share a row only above 1180 px; below that the timeline
      stacks with its rail hugging the left margin
- [ ] Capability columns are side by side from 900 px, tools row spans the full width
- [ ] Project register drops its column header and stacks the status below 720 px
- [ ] Contact cards sit side by side from 900 px; call-to-action band wraps its buttons
- [ ] Top bar email button is hidden below 560 px (it is still in the drawer and footer)
- [ ] No horizontal scrollbar at any width (drag the page sideways to confirm)
- [ ] Long project names wrap without clipping; timeline dates never collide with the spine
- [ ] Sticky top bar never covers a section heading when jumping to an anchor
- [ ] Scroll-progress rule under the top bar fills as you read
- [ ] Card hover lift is desktop-only and does not stick after a tap

## 6. Interaction

- [ ] Burger opens the drawer; focus moves into the panel; `Escape` closes it
- [ ] Closing the drawer returns focus to the burger button
- [ ] Closed drawer links are not reachable with Tab (inert / off-canvas)
- [ ] Drawer closes when a link is tapped and when the backdrop is tapped
- [ ] The active nav item tracks the section being read (scroll-spy)
- [ ] "Download CV" saves `Sim-Soklim-CV.pdf`; the PDF opens in the viewer
- [ ] "Back to top" scrolls to the overview and updates the address bar hash
- [ ] Footer copyright year matches the current year
- [ ] With JavaScript disabled, the whole CV is still readable and linkable

## 7. Typography and accessibility

- [ ] All three faces actually load: **Archivo** for headings and interface,
      **Source Serif 4** for prose, **DM Mono** for labels and figures
- [ ] No labels look smeared or fake-bold (DM Mono only ships 400 and 500, so a
      heavier request would be synthesised)
- [ ] First `Tab` reveals the "Skip to content" link and it jumps to `#main`
- [ ] Heading order is one `h1`, then `h2` per section, then `h3` per card
- [ ] Focus ring is visible on every interactive element (2 px copper outline)
- [ ] Drawer: `aria-expanded` toggles, panel is `aria-hidden` when closed
- [ ] Decorative SVG icons are `aria-hidden`; no icon is the only label
- [ ] Status pills ("Present" / "Completed") are readable, not colour-only
- [ ] Text contrast meets WCAG AA. Measured: body 8.5:1, labels 5.2:1, copper on
      paper 4.7:1, pill text 6.6:1 and 7.9:1, white on navy 15.6:1
- [ ] Dates, reference numbers and telephone numbers line up (tabular figures)
- [ ] Body serif text is not synthesised or too thin on Windows
- [ ] Reduced-motion emulation removes the beacon pulse and the hero reveal
- [ ] 200% zoom and 400% text-only zoom keep all content reachable
- [ ] Windows forced-colours / high-contrast mode **[not yet signed off]**

## 8. Offline behaviour

- [ ] Wi-Fi off → reload → page renders identically
- [ ] DevTools Network shows only relative paths, no third-party origin
- [ ] No cookies, no localStorage, no service worker
- [ ] Opens from a `file://` path, a USB stick and an extracted ZIP
- [ ] Deleting `images/portrait-cutout.webp` shows the `SS` monogram, not a
      broken-image icon
- [ ] The four `.woff2` files in `fonts/` load with the network off; no
      fallback to Georgia or a system sans is visible at any point
- [ ] Headings still read as heavier than body copy — Archivo and Source Serif 4
      are variable faces declared with a `font-weight` range, so confirm the
      weight axis is applied rather than every weight rendering identically
- [ ] The paper grain still renders (it is an inline SVG, not a request)

## 9. Print and sharing

- [ ] Print preview: top bar, drawer, hero buttons and the featured band are dropped
- [ ] Hairline borders and card backgrounds survive, navy band prints on white
- [ ] No card, timeline item or register row is split across a page break
- [ ] "Save as PDF" produces a readable multi-page document with the CV link removed
- [ ] Page title and meta description read correctly in a search snippet preview
- [ ] `og:title`, `og:description`, `og:image` render a sensible card when shared

---

## 10. Public deploy

Repository: <https://github.com/KangKimpor/sim-soklim-portfolio> (`main`).
Setup instructions are in README section 8.

- [ ] `python tools/_validate.py` passes, including the new `[csp compatibility]` group
- [ ] `git status` is clean and the branch is pushed
- [ ] `assets/Sim-Soklim-CV-original.pdf` is absent from the repository tree
      (check the file list in the GitHub UI, not just `.gitignore`)
- [ ] Deployed site returns the expected headers: `content-security-policy`,
      `x-content-type-options`, `referrer-policy`, `permissions-policy`
- [ ] Live site loads with no third-party requests and no CSP violations in the
      browser console
- [ ] `/assets/Sim-Soklim-CV.pdf` downloads, is 5 pages, and has no References block
- [ ] Placeholder photography replaced, or written permission recorded
- [ ] `og:url` / `twitter:url` added once the production domain is known
- [ ] Privacy of the repository itself: it is **public**, so anyone can read the
      full commit history — confirm that is intended

---

### Sign-off

| Item | Reviewer | Date | Outcome |
| --- | --- | --- | --- |
| Content accuracy | | | |
| Privacy / references decision | | | |
| Placeholders replaced | | | |
| Responsive and interaction | | | |
| Accessibility | | | |
| Offline behaviour | | | |
| Final approval to publish | | | |

### Known open items at the time of writing

1. `images/hero.webp` and `images/og-hero.jpg` are stand-in imagery.
2. References are commented out pending consent.
3. Forced-colours / high-contrast mode has not been signed off.
4. Section 05 is not in the navigation, by design; add a nav link when it is
   published.

