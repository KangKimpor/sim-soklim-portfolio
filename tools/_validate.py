#!/usr/bin/env python3
"""Structural checks for the offline review build of the Sim Soklim portfolio.

Usage:
    python tools/_validate.py

The site is a single static page (index.html + css/style.css + js/script.js)
and must work with no network access at all, so this script verifies:

  * every referenced file (CSS, JS, images, fonts, the CV PDF) exists on disk
  * nothing is loaded over http(s) and the CSS has no @import / remote url()
  * tag balance, anchor targets, SVG sprite references and the single <h1>
  * every class used in the markup is defined in css/style.css
  * every var(--token) used in the CSS is declared in :root
  * every id/selector js/script.js queries is present in the markup
  * the CV facts published on the page are present and retired values are gone
  * private referee details are absent from the entire HTML source
  * featured projects, subordinate packages and experience summaries keep the
    editorial layout's factual hierarchy
  * the share card is absolute and 1200x630, and .vercelignore still hides the
    review-only files from the deploy

Exit code is non-zero when a check fails, so it can gate a manual review.
"""
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANONICAL = "https://sim-soklim-portfolio.vercel.app"

REQUIRED_FILES = [
    "index.html",
    "css/style.css",
    "js/script.js",
    "images/og-hero.jpg",
    "images/sim-soklim-portrait.png",
    "assets/Sim-Soklim-CV.pdf",
    "favicon.svg",
    "robots.txt",
    "sitemap.xml",
]

# Paths that the deployment must NOT expose. `.vercelignore` is what enforces
# this at deploy time; tools/_validate_live.py asserts the same thing against a
# running URL, and the list is restated here so a careless edit to
# .vercelignore is caught before a deploy rather than after one.
IGNORED_PATHS = [
    ".vercel/",
    "tools/",
    "images/_portrait-preview.png",
    "images/portrait.jpg",
    "images/portrait.png",
    "images/portrait-cutout.png",
    "assets/Sim-Soklim-CV-original.pdf",
]

SECTIONS = [
    "overview",
    "experience-and-education",
    "core-competencies",
    "selected-projects",
    "contact",
]

JS_SELECTORS = ["[data-nav]", "section[id]", ".portrait-frame"]

JS_CLASS_HOOKS = ["js-enabled", "is-active", "is-empty", "menu-open"]

# Facts copied from the CV that must appear on the page.
REQUIRED_TEXT = [
    "soklimlll@gmail.com",
    "+855 95 810 472",
    "soklim-sim-6589221a4",
    "SingBuild Construction",
    "TCV Engineering Co., Ltd.",
    "Cana Sino Construction Corporation",
    "Norton University",
    "Bak Touk High School",
    "Ecam School",
    "DCD Cambodia",
    "National Assembly Building",
    "Techo International Airport",
    "Microsoft Project",
    "Civil Quantity Surveyor",
]

# Retired or incorrect values that must never come back.
FORBIDDEN_TEXT = [
    "98777174",
    "648937172",
    "Zhang Jian Ping",
    "Tang Hao",
    "Meng Lin",
    "VET Charging Station",
]

# Private reference details must stay out of the complete source, including
# comments. The public downloadable CV has its References block redacted.
WITHHELD_TEXT = [
    "Pich Rathy",
    "Richard Abas Lorbes",
    "Ryan Koh",
    "Sam Sithih",
    "Hok YekSrun",
    "+855 11 651 168",
    "+855 96 956 7510",
    "+855 69 840 234",
    "+855 16 229 666",
    "+855 93 878 818",
]

# A class selector is ".name" not preceded by a word character, quote or slash,
# which keeps file extensions ("SpaceMono-400.woff2") and numbers ("0.5rem") out.
CLASS_RE = re.compile(r"""(?<![\w.'"/\\])\.(-?[A-Za-z_][\w-]*)""")

problems = []


def fail(message):
    problems.append(message)
    print("  FAIL: " + message)


def ok(message):
    print("  ok:   " + message)


def note(message):
    print("  note: " + message)


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def check_files():
    print("[files]")
    for rel in REQUIRED_FILES:
        if os.path.isfile(os.path.join(ROOT, rel)):
            ok(rel)
        else:
            fail("missing file: " + rel)


def check_assets(html):
    print("[assets referenced by the markup]")
    assets = sorted(set(re.findall(r'(?:src|href)="((?:css|js|images|fonts|assets)/[^"?]+)', html)))
    for asset in assets:
        if os.path.isfile(os.path.join(ROOT, asset)):
            ok(asset)
        else:
            fail("missing asset: " + asset)
    if not assets:
        fail("the markup references no local assets at all")


def check_markup(html):
    print("[markup]")
    tags = ["section", "article", "div", "ul", "li", "dl", "header", "footer", "nav", "figure"]
    for tag in tags:
        opened = len(re.findall(r"<%s[\s>]" % tag, html))
        closed = len(re.findall(r"</%s>" % tag, html))
        if opened != closed:
            fail("<%s>: %d open, %d close" % (tag, opened, closed))
    ok("tag balance checked for %d element types" % len(tags))

    ids = set(re.findall(r'\sid="([^"]+)"', html))
    for target in sorted(set(re.findall(r'href="#([^"]+)"', html))):
        if target not in ids:
            fail("anchor points at a missing id: #" + target)
    for section in SECTIONS:
        if section not in ids:
            fail("missing section id: " + section)
    ok("anchor targets and the five section ids resolve")

    symbols = set(re.findall(r'<symbol id="([^"]+)"', html))
    used = set(re.findall(r'<use href="#([^"]+)"', html))
    for ref in sorted(used - symbols):
        fail("svg <use> points at a missing symbol: #" + ref)
    for ref in sorted(symbols - used):
        fail("svg symbol defined but never used: #" + ref)
    ok("%d svg sprite symbols defined and used" % len(symbols))

    h1 = len(re.findall(r"<h1[\s>]", html))
    if h1 != 1:
        fail("expected exactly one <h1>, found %d" % h1)
    else:
        ok("exactly one <h1>")

def check_no_network(html, css):
    print("[offline]")
    remote = re.findall(r'src="(https?://[^"]+)"', html)
    for tag in re.findall(r"<link\b[^>]*>", html):
        if re.search(r'rel="canonical"', tag):
            # A canonical URL is metadata for crawlers, never fetched by the
            # browser, so it costs nothing against the offline promise.
            continue
        found = re.search(r'href="(https?://[^"]+)"', tag)
        if found:
            remote.append(found.group(1))
    if remote:
        fail("remote resources would be requested: %s" % ", ".join(sorted(set(remote))))
    else:
        ok("no remote images, scripts, stylesheets or preloads")

    # Strip comments first: a file that *says* "no @import" must not trip this.
    css_bare = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if "@import" in css_bare:
        fail("css/style.css uses @import")
    elif re.search(r"url\(\s*['\"]?https?://", css_bare):
        fail("css/style.css loads a remote url()")
    else:
        ok("css/style.css only loads local url() targets")

    fonts = sorted(set(re.findall(r"url\(\s*['\"](\.\./fonts/[^'\"]+)['\"]", css)))
    for font in fonts:
        if not os.path.isfile(os.path.normpath(os.path.join(ROOT, "css", font))):
            fail("font file missing: " + font)
    ok("%d local font files referenced by @font-face" % len(fonts))

    for asset in sorted(set(re.findall(r"url\(\s*['\"]([^'\"]+)['\"]", css))):
        if asset.startswith(("data:", "http:", "https:", "..")):
            continue
        if not os.path.isfile(os.path.normpath(os.path.join(ROOT, "css", asset))):
            fail("css references a missing file: " + asset)



def check_classes(html, css):
    print("[class coverage]")
    css_clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    defined = set(CLASS_RE.findall(css_clean))

    used = set()
    for attr in re.findall(r'class="([^"]+)"', html):
        used.update(attr.split())

    for name in sorted(used - defined):
        fail("class used in the markup with no CSS rule: .%s" % name)
    if used <= defined:
        ok("all %d classes in the markup have CSS rules" % len(used))

    orphans = sorted(defined - used - set(JS_CLASS_HOOKS))
    if orphans:
        note("CSS rules not used by the markup (design tokens and utilities kept "
             "for reuse): " + ", ".join("." + n for n in orphans))

    for hook in JS_CLASS_HOOKS:
        if "." + hook not in css_clean:
            fail("js/script.js toggles .%s but css/style.css has no rule" % hook)
    ok("every class js/script.js toggles is styled")

    if css_clean.count("{") != css_clean.count("}"):
        fail("css braces unbalanced: %d open, %d close"
             % (css_clean.count("{"), css_clean.count("}")))
    else:
        ok("css braces balanced")


def check_tokens(css):
    print("[design tokens]")
    css_clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    roots = re.findall(r":root\s*\{(.*?)\n\}", css_clean, re.S)
    if not roots:
        fail("no :root token block found in css/style.css")
        return
    defined = set(re.findall(r"(--[\w-]+)\s*:", "\n".join(roots)))
    declared = set(re.findall(r"(--[\w-]+)\s*:", css_clean))
    used = set(re.findall(r"var\(\s*(--[\w-]+)", css_clean))
    for name in sorted(used - declared):
        fail("var(%s) is never declared" % name)
    for name in sorted(used - defined):
        fail("var(%s) is used before it is declared in :root" % name)
    for name in sorted(defined - used):
        fail("%s is declared in :root but never used" % name)
    ok("%d custom properties declared in :root and all used" % len(defined))


def check_javascript(html):
    print("[javascript wiring]")
    js = read("js/script.js")
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    for el_id in sorted(set(re.findall(r"getElementById\('([^']+)'\)", js))):
        if el_id not in ids:
            fail("js queries #%s which is not in the markup" % el_id)
    for selector in JS_SELECTORS:
        attr_match = re.match(r"^([a-zA-Z][\w-]*)\[([\w-]+)\]$", selector)
        if attr_match:
            tag, attr = attr_match.groups()
            if ("<%s" % tag) not in html or (' %s="' % attr) not in html:
                fail("js queries %s but the markup has no <%s %s=...>" % (selector, tag, attr))
        elif selector.strip(".[]") not in html:
            fail("js queries %s which is not in the markup" % selector)
    ok("every id and selector used by js/script.js exists in the markup")


def check_content(html):
    print("[cv content]")
    visible = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    for text in REQUIRED_TEXT:
        if text not in visible:
            fail("missing CV fact: " + text)
    for text in FORBIDDEN_TEXT:
        if text in html:
            fail("retired value still present: " + text)
    ok("%d CV facts present, no retired values" % len(REQUIRED_TEXT))

    for text in WITHHELD_TEXT:
        if text in html:
            fail("private referee detail remains in HTML source: " + text)

    # A nested <!-- or --> inside a block comment closes it early: the rest of
    # the comment then parses as real markup, which is how the withheld referee
    # section once reached the page. Class-agnostic on purpose, since matching
    # the section tag by its exact class attribute is what let that slip past.
    if re.search(r'<section[^>]*\sid="references"', html):
        fail("private references section remains in HTML source")
    elif "-->" in visible or "<!--" in visible:
        fail("a block comment is closed early by a nested <!-- or --> inside it")
    else:
        ok("private references removed from HTML source")


def check_editorial_structure(html):
    print("[editorial content hierarchy]")
    featured = re.findall(r'<article class="project-feature">(.*?)</article>', html, re.S)
    additional = re.findall(r'<article class="register-row">', html)
    if len(featured) != 3 or len(additional) != 3:
        fail("expected three featured projects and three additional projects")
    else:
        ok("six project entries, with subordinate hotel packages")
    if not featured or not all(code in featured[0] for code in ('BP02', 'BP03', 'BP04')):
        fail("BP02, BP03 and BP04 must be scoped under the Pan Pacific project")
    else:
        ok("three hotel packages grouped under Pan Pacific")
    roles = re.findall(r'<article class="experience-row">(.*?)</article>', html, re.S)
    if len(roles) != 4:
        fail("expected four employment roles")
    for role in roles:
        if not 2 <= len(re.findall(r'<li>', role)) <= 3:
            fail("experience summaries require two or three responsibility bullets")
    ok("four concise employment summaries checked")
    panel = re.search(r'<aside\b[^>]*id="navPanel"[^>]*>', html)
    if not panel or not all(attr in panel.group(0) for attr in ('hidden', 'inert', 'aria-modal="true"', 'aria-hidden="true"')):
        fail("mobile dialog must start hidden and inert")
    else:
        ok("menu starts hidden and inert")


def check_csp(html):
    """The strict Content-Security-Policy in vercel.json assumes a clean page.

    `default-src 'self'` with no 'unsafe-inline' means an inline <script>, an
    inline <script> block, a style attribute or an on* handler would be blocked
    by the browser rather than by this script. Catch that here instead.
    """
    print("[csp compatibility]")
    if re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html):
        fail("inline <script> block: the Content-Security-Policy would block it")
    if re.search(r"\sstyle=\"", html):
        fail("style attribute present: the Content-Security-Policy would block it")
    handlers = re.findall(r"\s(on[a-z]+)=", html)
    if handlers:
        fail("inline event handler(s) %s: the policy would block them"
             % ", ".join(sorted(set(handlers))))
    if not re.search(r"<style[\s>]", html):
        ok("no inline script, style attribute, on* handler or <style> block")
    else:
        fail("<style> block present: the policy would block it")

    for pattern, why in ((r'src="https?://', "remote src"),
                         (r'<link\b(?![^>]*rel="(?:preconnect|dns-prefetch|canonical)")[^>]*href="https?://', "remote link")):
        if re.search(pattern, html):
            fail("%s: blocked by the policy's default-src 'self'" % why)
    ok("policy allows exactly what the page requests")


def _jpeg_size(path):
    """Width and height of a baseline JPEG, read from the SOF marker."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def check_share_metadata(html):
    """A link preview is built from absolute URLs and a 1200x630 card.

    Facebook, LinkedIn and Twitter do not resolve a relative og:image, so a
    relative path here fails silently: the page is fine, the shared card has no
    image. These assertions are the only thing that catches it.
    """
    print("[share metadata]")

    favicon = re.search(r'<link\b[^>]*rel="icon"[^>]*>', html)
    if not favicon:
        fail("no favicon <link rel=\"icon\">: /favicon.ico falls back to a 404")
    else:
        ok("favicon declared")

    canonical = re.search(r'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"', html)
    if not canonical:
        fail("no <link rel=\"canonical\">")
    elif canonical.group(1) != CANONICAL + "/":
        fail("canonical is %s, expected %s/" % (canonical.group(1), CANONICAL))
    else:
        ok("canonical points at the stable production alias")

    for prop, expect in (("og:url", CANONICAL + "/"),
                         ("og:image", CANONICAL + "/images/og-hero.jpg"),
                         ("og:image:width", "1200"),
                         ("og:image:height", "630")):
        found = re.search(r'<meta\b[^>]*property="%s"[^>]*content="([^"]*)"' % re.escape(prop), html)
        if not found:
            fail("missing meta property: " + prop)
        elif found.group(1) != expect:
            fail("%s is %r, expected %r" % (prop, found.group(1), expect))

    for name, expect in (("twitter:card", "summary_large_image"),
                         ("twitter:image", CANONICAL + "/images/og-hero.jpg"),
                         ("twitter:title", None),
                         ("twitter:description", None)):
        found = re.search(r'<meta\b[^>]*name="%s"[^>]*content="([^"]*)"' % re.escape(name), html)
        if not found:
            fail("missing meta name: " + name)
        elif expect is not None and found.group(1) != expect:
            fail("%s is %r, expected %r" % (name, found.group(1), expect))

    for prop in ("og:image", "twitter:image"):
        found = re.search(r'<meta\b[^>]*(?:property|name)="%s"[^>]*content="([^"]*)"' % re.escape(prop), html)
        if found and not found.group(1).startswith("https://"):
            fail("%s must be absolute, crawlers do not resolve a relative URL" % prop)
    ok("social metadata is absolute and consistent")

    size = _jpeg_size(os.path.join(ROOT, "images/og-hero.jpg"))
    if size != (1200, 630):
        fail("images/og-hero.jpg is %s, the declared card is 1200x630" % (size,))
    else:
        ok("images/og-hero.jpg is really 1200x630")


def check_vercelignore():
    """The deploy is uploaded from disk, not from git, so .vercelignore decides
    what the public URL exposes. A missing line here quietly publishes the QA
    preview, the portrait sources or the unredacted CV."""
    print("[deployment payload]")
    path = os.path.join(ROOT, ".vercelignore")
    if not os.path.isfile(path):
        fail("no .vercelignore: the full working directory would be uploaded")
        return
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    lines = {ln.strip() for ln in body.splitlines()}

    for entry in IGNORED_PATHS:
        if entry not in lines:
            fail(".vercelignore does not exclude: " + entry)
    ok("%d review-only paths excluded from the upload" % len(IGNORED_PATHS))

    if "vercel.json" in lines:
        fail(".vercelignore excludes vercel.json, which would disable the headers")
    else:
        ok("vercel.json still reaches the build, so the headers apply")

    for served in ("favicon.svg", "robots.txt", "sitemap.xml"):
        if served in lines:
            fail(".vercelignore excludes %s, which the site must serve" % served)
    ok("the files the site serves are not excluded")


def main():
    print("validating " + ROOT)
    html = read("index.html")
    css = read("css/style.css")
    check_files()
    check_assets(html)
    check_markup(html)
    check_no_network(html, css)
    check_csp(html)
    check_classes(html, css)
    check_tokens(css)
    check_javascript(html)
    check_content(html)
    check_editorial_structure(html)
    check_share_metadata(html)
    check_vercelignore()

    print("")
    if problems:
        print("RESULT: %d PROBLEM(S) FOUND" % len(problems))
        return 1
    print("RESULT: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
