#!/usr/bin/env python3
"""Publish a public-safe copy of the CV: the references block is really removed.

The supplied document is five pages:

    1     covering letter addressed to a named employer
    2-4   the CV proper
    5     the last training, then "References" with five referees' direct
          telephone numbers

The website deliberately does not publish those references, so shipping the
file unchanged would hand the numbers to anyone who clicks Download. Drawing a
white box over them would not help either: the text would stay extractable.

This script uses PyMuPDF redaction annotations instead, which delete the
underlying text objects. Only the region from the "References" heading to the
end of the last line on that page is removed, so the AutoCAD/DCD training that
sits directly above it survives and the published PDF still matches what the
website claims.

The source is the unredacted original, which is deliberately git-ignored. It must
not be changed to point at the public copy: once the references are gone there
is no "References" heading left to find, so a second run would fail rather than
silently ship something different. Regenerate with:

    python tools/make_public_cv.py

The original file is never modified.

Usage:
    python tools/make_public_cv.py [out.pdf]

Requires PyMuPDF and pypdf, for the redaction and the verification pass.
"""
import os
import sys

import pypdf

try:
    import pymupdf
except ImportError:  # older PyMuPDF releases expose the module as fitz
    import fitz as pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The unredacted original. Not the published file next to it: the "References"
# heading this script looks for only exists in the original, so re-running
# against assets/Sim-Soklim-CV.pdf would fail instead of quietly producing a
# different result.
SOURCE = os.path.join(ROOT, "assets", "Sim-Soklim-CV-original.pdf")

# Text that must not survive into the published file.
FORBIDDEN = [
    "References",
    "Pich Rathy", "Richard Abas", "Ryan Koh", "Sam Sithih", "Hok YekSrun",
    "651 168", "956 7510", "840 234", "229 666", "878 818",
    "National Assembly Cambodia", "HSE Manager", "QA/QC Manager",
]

# Text that must still be there, so the PDF keeps matching the website.
REQUIRED = [
    "SingBuild", "TCV", "Cana Sino", "Norton", "Ecam", "AutoCAD",
    "soklimlll@gmail.com",
]


def redact_references(document):
    """Delete the References block from the last page. Returns the rect used."""
    for page in reversed(document):
        hits = page.search_for("References")
        if not hits:
            continue
        top = hits[0]
        bottom = max((block[3] for block in page.get_text("blocks")), default=top.y1)
        rect = pymupdf.Rect(page.rect.x0 + 20, top.y0 - 6, page.rect.x1 - 20, bottom + 6)
        page.add_redact_annot(rect)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
        return rect
    raise SystemExit("could not find a References heading in the source PDF")


def report(out):
    reader = pypdf.PdfReader(out)
    text = "".join((page.extract_text() or "") for page in reader.pages)
    leaked = [needle for needle in FORBIDDEN if needle in text]
    missing = [needle for needle in REQUIRED if needle not in text]
    print("  pages    : %d" % len(reader.pages))
    print("  size     : %.0f KB" % (os.path.getsize(out) / 1024.0))
    print("  leaked   : %s" % (", ".join(leaked) if leaked else "none"))
    print("  missing  : %s" % (", ".join(missing) if missing else "none"))
    return not leaked and not missing


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "Sim-Soklim-CV.pdf")
    if not os.path.isfile(SOURCE):
        print("source not found:", SOURCE, file=sys.stderr)
        return 1

    print("source : %s (%.0f KB)" % (SOURCE, os.path.getsize(SOURCE) / 1024.0))
    document = pymupdf.open(SOURCE)
    rect = redact_references(document)

    # PyMuPDF will not save over a file it still holds open, and we normally
    # write back to the same path, so go via a temporary file and swap.
    tmp = out + ".tmp"
    document.save(tmp, garbage=3, deflate=True)
    document.close()
    os.replace(tmp, out)

    print("removed: References block at %s" % (tuple(round(v, 1) for v in rect),))
    print("public : %s" % out)
    return 0 if report(out) else 2


if __name__ == "__main__":
    sys.exit(main())
