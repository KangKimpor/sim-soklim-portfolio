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
  * the references section stays commented out until referee consent is given

Exit code is non-zero when a check fails, so it can gate a manual review.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FILES = [
    "index.html",
    "css/style.css",
    "js/script.js",
    "images/hero.webp",
    "images/og-hero.jpg",
    "images/portrait-cutout.webp",
    "assets/Sim-Soklim-CV.pdf",
]

SECTIONS = [
    "overview",
    "experience-and-education",
    "core-competencies",
    "selected-projects",
    "contact",
]

JS_SELECTORS = ["[data-nav]", "section[id]", ".portrait-frame"]

JS_CLASS_HOOKS = ["is-open", "is-active", "is-empty", "menu-open"]

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
    ok("anchor targets and the five section ids resolve (#references is commented out)")

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

    if "\u2014" in html:
        fail("em dash (U+2014) in the markup, the CV punctuation is an en dash: %d found"
             % html.count("\u2014"))
    else:
        ok("punctuation follows the CV (no em dashes)")


def check_no_network(html, css):
    print("[offline]")
    remote = re.findall(r'src="(https?://[^"]+)"', html)
    for tag in re.findall(r"<link\b[^>]*>", html):
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
    root = re.search(r":root\s*\{(.*?)\n\}", css_clean, re.S)
    if not root:
        fail("no :root token block found in css/style.css")
        return
    defined = set(re.findall(r"(--[\w-]+)\s*:", root.group(1)))
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

    if '<section class="section section-alt" id="references">' in visible:
        fail("the references section is published; keep it commented out until consent")
    elif 'id="references"' in html:
        ok("references section present but commented out")
    else:
        fail("references section markup not found")


def main():
    print("validating " + ROOT)
    html = read("index.html")
    css = read("css/style.css")
    check_files()
    check_assets(html)
    check_markup(html)
    check_no_network(html, css)
    check_classes(html, css)
    check_tokens(css)
    check_javascript(html)
    check_content(html)

    print("")
    if problems:
        print("RESULT: %d PROBLEM(S) FOUND" % len(problems))
        return 1
    print("RESULT: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

