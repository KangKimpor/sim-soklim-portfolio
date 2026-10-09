#!/usr/bin/env python3
"""Live checks for a deployed copy of the Sim Soklim portfolio.

Usage:
    python tools/_validate_live.py
    python tools/_validate_live.py --url https://sim-soklim-portfolio.vercel.app

Unlike tools/_validate.py, which reads the files on disk and never opens a
socket, this script talks to the running site. It is the only way to prove the
two things the offline validator cannot see:

  * the response headers actually reach the browser (vercel.json is applied)
  * the review-only files really are absent from the public URL

The second one is not theoretical. The first deploy of this project served
images/_portrait-preview.png, a QA artefact that README section 2 describes as
"never served", because the CLI uploads the working directory rather than the
git tree, so .gitignore has no effect on what the deployment exposes.
.vercelignore does. This script is the regression test for that.

Exit code is non-zero when a check fails.
"""
import argparse
import importlib.util
import os
import re
import sys
import urllib.error
import urllib.request

# The canonical URL and the list of review-only paths live in tools/_validate.py
# so the offline and live checks cannot drift apart. Loaded by path because
# tools/ is a script folder, not an importable package.
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_site_validate", os.path.join(_HERE, "_validate.py"))
_site_validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_site_validate)
CANONICAL = _site_validate.CANONICAL
IGNORED_PATHS = _site_validate.IGNORED_PATHS

# Served by the page or needed by it.
SERVED = [
    "/",
    "/css/style.css",
    "/js/script.js",
    "/fonts/Archivo-var.woff2",
    "/fonts/SourceSerif4-var.woff2",
    "/images/og-hero.jpg",
    "/images/sim-soklim-portrait.png",
    "/assets/Sim-Soklim-CV.pdf",
    "/favicon.svg",
    "/robots.txt",
    "/sitemap.xml",
]

# Set by the headers block in vercel.json.
EXPECTED_HEADERS = {
    "content-security-policy": "default-src 'self'",
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "geolocation=()",
}

# A directory that has no index 404s on its own, so IGNORED_PATHS alone would
# give a false pass for tools/. These are the concrete URLs an upload of the
# working directory would expose.
ALSO_NOT_SERVED = [
    "/.vercel/project.json",
    "/.vercel/auth-firefox/auth.json",
    "/tools/social-card.html",
    "/tools/social-card.css",
    "/tools/_validate.py",
    "/tools/make_public_cv.py",
    "/tools/cutout.py",
    "/README.md",
    "/REVIEW_CHECKLIST.md",
    "/OFFLINE_REVIEW.md",
]

UA = "sim-soklim-portfolio-validate-live/1.0"
problems = []


def fail(message):
    problems.append(message)
    print("  FAIL: " + message)


def ok(message):
    print("  ok:   " + message)


def fetch(url):
    """Return (status, headers, body) without raising on 4xx/5xx."""
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.headers, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.headers, err.read().decode("utf-8", "replace")
    except urllib.error.URLError as err:
        return None, {}, str(err.reason)


def check_served(base):
    print("[served]")
    for path in SERVED:
        status, _, _ = fetch(base + path)
        if status == 200:
            ok("200 %s" % path)
        else:
            fail("%s returned %s, expected 200" % (path, status))


def check_not_served(base):
    print("[review-only paths must not be reachable]")
    for entry in IGNORED_PATHS:
        path = "/" + entry
        status, _, _ = fetch(base + path)
        if status == 404:
            ok("404 %s" % path)
        else:
            fail("%s returned %s, expected 404" % (path, status))
    for extra in ("/.gitignore", "/vercel.json", "/.vercelignore") + tuple(ALSO_NOT_SERVED):
        status, _, _ = fetch(base + extra)
        if status == 404:
            ok("404 %s" % extra)
        else:
            fail("%s returned %s, expected 404" % (extra, status))


def check_headers(base):
    print("[headers from vercel.json]")
    status, headers, _ = fetch(base + "/")
    if status != 200:
        fail("the page returned %s" % status)
        return
    for name, needle in EXPECTED_HEADERS.items():
        value = headers.get(name, "")
        if not value:
            fail("missing header: " + name)
        elif needle not in value:
            fail("%s is %r, expected it to contain %r" % (name, value, needle))
        else:
            ok("%s set" % name)


def check_content(base):
    print("[page content]")
    status, _, body = fetch(base + "/")
    if status != 200:
        fail("the page returned %s" % status)
        return
    title = re.search(r"<title>(.*?)</title>", body)
    if title and "Sim Soklim" in title.group(1):
        ok("title: " + title.group(1))
    else:
        fail("unexpected <title>: %s" % (title.group(1) if title else None))

    for prop, expect in (("og:url", CANONICAL + "/"),
                         ("og:image", CANONICAL + "/images/og-hero.jpg")):
        found = re.search(r'<meta\b[^>]*property="%s"[^>]*content="([^"]*)"' % re.escape(prop), body)
        if found and found.group(1) == expect:
            ok("%s is absolute" % prop)
        else:
            fail("%s is %s, expected %s" % (prop, found.group(1) if found else None, expect))

    status, _, robots = fetch(base + "/robots.txt")
    if status == 200 and "Sitemap:" in robots:
        ok("robots.txt points at the sitemap")
    else:
        fail("robots.txt is missing or has no Sitemap line")

    status, _, sitemap = fetch(base + "/sitemap.xml")
    if status == 200 and "<urlset" in sitemap and CANONICAL in sitemap:
        ok("sitemap.xml lists the canonical URL")
    else:
        fail("sitemap.xml is missing or does not list %s" % CANONICAL)


def main():
    parser = argparse.ArgumentParser(description="live checks for the deployed portfolio")
    parser.add_argument("--url", default=CANONICAL, help="base URL, default %s" % CANONICAL)
    args = parser.parse_args()
    base = args.url.rstrip("/")
    print("validating " + base)

    check_served(base)
    check_not_served(base)
    check_headers(base)
    check_content(base)

    print("")
    if problems:
        print("RESULT: %d PROBLEM(S) FOUND" % len(problems))
        return 1
    print("RESULT: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
