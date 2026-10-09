# Offline review

The portfolio loads entirely from local files: HTML, one stylesheet, one script, two font files and the CV portrait. The PDF downloads from `assets/Sim-Soklim-CV.pdf`. Icons are an inline SVG sprite. There is no fetch, CDN, analytics, cookie, storage or service worker.

Open `index.html` from the folder, or start `python -m http.server 8000` and open `http://localhost:8000`. Switch off connectivity and reload. The page should render identically. Email, telephone and LinkedIn are user-selected external destinations; connectivity is needed for their respective applications.

In browser DevTools, the resource list should contain only local assets. Fetch/XHR and WebSocket views should be empty. The social card URL in metadata is for link-preview crawlers; the browser does not load it as a page resource.

With JavaScript disabled, the header navigation wraps, the menu button is hidden, native hotel-package disclosure still works, and all content and links remain available. A missing portrait falls back to the SS monogram when JavaScript is enabled. Reduced-motion preferences disable smooth scrolling, and print styles produce a plain readable document.

For offline sharing, copy the public site files or create an archive that preserves their paths. Exclude the original unredacted CV and local review/source files; `.vercelignore` documents the deployment exclusions. An extracted copy of the public files can be opened directly without a server.

Run `python tools/_validate.py` to confirm local file references, no remote loading, CSP compatibility, metadata and source privacy. Responsive and keyboard checks are in `REVIEW_CHECKLIST.md`.
