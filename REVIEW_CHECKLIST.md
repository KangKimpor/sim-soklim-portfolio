# Portfolio review

The redesign presents the existing CV facts with a concise overview, grouped projects, four employment roles, expertise and education, and direct contact links. Use this checklist against the current local build before publishing.

## Content and privacy

- [ ] Name, titles, employers, employment dates and qualifications match the source CV.
- [ ] Pan Pacific Hotel / Norodom Business Center contains BP02, BP03 and BP04; those packages are not counted as independent projects.
- [ ] UVP2, National Assembly, Techo Airport, Elysee and Kbal Thnol remain present.
- [ ] Only National Assembly has an explicit completed label; employer dates are not used as project dates.
- [ ] The email, phone and LinkedIn URL are correct.
- [ ] No invented budgets, savings, project outcomes or design ownership appear.
- [ ] No referee names or numbers appear in the HTML source, including comments.
- [ ] Downloaded CV remains the redacted public PDF; the original is excluded from uploads.

## Browser and interaction

- [ ] Check Chrome and WebKit at 320, 360, 375, 390, 393, 402, 412, 430, 480, 600, 768, 900, 1024, 1280, 1440 and 1920 px.
- [ ] No horizontal overflow; titles, employers and email wrap naturally.
- [ ] CV and contact actions appear before the portrait on phones.
- [ ] Menu opens with focus on Close; Tab and Shift+Tab stay inside.
- [ ] Escape, Close and backdrop restore focus to the trigger.
- [ ] A menu section link closes the dialog and focuses its destination.
- [ ] Resizing to desktop closes the dialog and restores page scrolling.
- [ ] The hotel disclosure opens with mouse, touch and keyboard, and stays readable at 320 px.
- [ ] Anchor headings clear the sticky header; active links identify their section.
- [ ] All content and navigation are available with JavaScript disabled.
- [ ] Reduced motion removes smooth scrolling; no content depends on animation.
- [ ] Skip link and focus outlines are visible; 200% zoom remains usable.
- [ ] Print preview is readable and removes menus and actions.
- [ ] Forced-colours mode keeps controls and text readable.

## Assets and publishing

- [ ] Local fonts, portrait and CV load; no third-party resources are requested.
- [ ] Broken portrait asset falls back to the SS monogram.
- [ ] Social card is the new typographic 1200 × 630 JPEG, with matching metadata.
- [ ] `python tools/_validate.py` and `node --check js/script.js` pass.
- [ ] `git diff` contains only the intended redesign and QA documentation changes.
- [ ] If publishing, check live CSP/security headers and review-only paths with `tools/_validate_live.py`.

This checklist is a review aid, not a record of client approval or permission to deploy. Device widths are browser emulations unless an actual device is separately tested.
