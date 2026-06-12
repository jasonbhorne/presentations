#!/bin/bash
# Convert one .pptx into slide JPGs under <repo>/<slug>/slides/.
# Usage: convert.sh "<absolute path to .pptx>" "<slug>" [dpi]
#
# Pipeline: stage a dequarantined copy -> PowerPoint exports it to PDF
# (tools/export_to_pdf.scpt) -> pdftoppm rasterizes to JPGs.
# Use ~110 dpi for image-heavy decks, ~150 for text-heavy ones.
#
# After converting, run: python3 tools/build_viewer.py <slug> && python3 tools/build_landing.py
set -euo pipefail

SRC="$1"
SLUG="$2"
DPI="${3:-150}"

# Repo root = parent of this tools/ directory.
TOOLS="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$TOOLS/.." && pwd)"
DL="$HOME/Downloads"
PDFTOPPM="$(command -v pdftoppm || echo /opt/homebrew/bin/pdftoppm)"

[ -f "$SRC" ] || { echo "MISSING SOURCE: $SRC" >&2; exit 1; }

STAGE="$DL/_ppt_src_${SLUG}.pptx"
TMP_PDF_NAME="_ppt_export_${SLUG}.pdf"
TMP_PDF="$DL/$TMP_PDF_NAME"

# Stage a dequarantined copy so PowerPoint does not open it in Protected View.
cp "$SRC" "$STAGE"
xattr -cr "$STAGE" 2>/dev/null || true
rm -f "$TMP_PDF"

echo "[$SLUG] exporting to PDF via PowerPoint..."
RESULT=$(osascript "$TOOLS/export_to_pdf.scpt" "$STAGE" "$TMP_PDF_NAME" 2>&1)
echo "[$SLUG] $RESULT"
rm -f "$STAGE"
[ -f "$TMP_PDF" ] || { echo "[$SLUG] FAILED: no PDF produced" >&2; exit 2; }

OUT="$REPO/$SLUG/slides"
rm -rf "$OUT"; mkdir -p "$OUT"
echo "[$SLUG] rasterizing at ${DPI} dpi..."
"$PDFTOPPM" -jpeg -r "$DPI" "$TMP_PDF" "$OUT/slide"
rm -f "$TMP_PDF"

COUNT=$(ls "$OUT"/*.jpg 2>/dev/null | wc -l | tr -d ' ')
SIZE=$(du -sh "$OUT" | cut -f1)
echo "[$SLUG] DONE: $COUNT slides, $SIZE"
