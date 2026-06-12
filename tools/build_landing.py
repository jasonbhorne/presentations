#!/usr/bin/env python3
"""Regenerate the root index.html (landing page) from presentations.json.

Cards are grouped by category. Interactive decks get a badge. Run:
    python3 tools/build_landing.py
"""
import html
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "presentations.json")

# Section order + display headings.
CATEGORY_ORDER = [
    ("interactive", "Interactive talks"),
    ("ai", "AI &amp; technology"),
    ("other", "Other talks"),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Presentations &middot; Jason Horne</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,300;0,400;0,600&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#faf8f3; --surface:#f2ede2; --border:#d4c9b0;
  --ink:#1a1208; --muted:#6b5f4a; --accent:#c0392b;
  --display:'Playfair Display',serif; --body:'Source Serif 4',serif;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--ink); font-family:var(--body); min-height:100vh; padding:6vw 7vw 5vw; }
.eyebrow { font-size:14px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--accent); margin-bottom:18px; }
h1 { font-family:var(--display); font-weight:900; font-size:clamp(40px,7vw,76px); line-height:1.02; margin-bottom:14px; }
.sub { font-family:var(--body); font-weight:300; font-style:italic; font-size:clamp(18px,2.4vw,24px); color:var(--muted); max-width:680px; }
.rule { width:64px; height:3px; background:var(--accent); margin:34px 0 14px; }
section { margin-top:46px; }
.sectionhead { font-family:var(--body); font-size:13px; font-weight:600; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:20px; padding-bottom:10px; border-bottom:1px solid var(--border); }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:24px; }
a.card { display:block; text-decoration:none; color:inherit; background:var(--surface); border-top:3px solid var(--accent); padding:30px 28px; transition:transform .2s, box-shadow .2s; position:relative; }
a.card:hover { transform:translateY(-4px); box-shadow:0 10px 30px rgba(26,18,8,0.12); }
a.card h2 { font-family:var(--display); font-weight:700; font-size:24px; line-height:1.15; margin-bottom:10px; }
a.card p { font-family:var(--body); font-weight:300; font-size:16px; color:var(--muted); line-height:1.5; }
a.card .go { display:inline-block; margin-top:16px; font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--accent); }
.badge { position:absolute; top:14px; right:16px; font-size:10px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#fff; background:var(--accent); padding:3px 9px; border-radius:2px; }
footer { margin-top:60px; font-size:14px; color:var(--muted); }
footer a { color:var(--accent); text-decoration:none; }
</style>
</head>
<body>
  <div class="eyebrow">Presentations</div>
  <h1>Jason Horne</h1>
  <p class="sub">Interactive talks and slide decks on AI, education, and school operations. Open any presentation, then use arrow keys, click, or swipe to advance.</p>
  <div class="rule"></div>
"""

FOOT = """  <footer>Dr. Jason Horne &middot; Greeneville City Schools &middot; <a href="https://jasonhorne.org">jasonhorne.org</a></footer>
</body>
</html>
"""


def card(entry):
    title = html.escape(entry["title"])
    blurb = html.escape(entry.get("blurb", ""))
    slug = entry["slug"]
    badge = '<span class="badge">Interactive</span>' if entry.get("type") == "interactive" else ""
    return (
        f'    <a class="card" href="./{slug}/">{badge}'
        f'<h2>{title}</h2><p>{blurb}</p>'
        f'<span class="go">Open &rarr;</span></a>'
    )


def main():
    with open(MANIFEST) as f:
        manifest = json.load(f)

    parts = [HEAD]
    for cat_key, cat_label in CATEGORY_ORDER:
        items = [e for e in manifest if e.get("category") == cat_key]
        if not items:
            continue
        parts.append(f'  <section>\n    <div class="sectionhead">{cat_label}</div>\n    <div class="grid">')
        for e in items:
            parts.append(card(e))
        parts.append("    </div>\n  </section>")
    parts.append(FOOT)

    out = os.path.join(REPO, "index.html")
    with open(out, "w") as f:
        f.write("\n".join(parts))
    print(f"built index.html ({len(manifest)} decks)")


if __name__ == "__main__":
    main()
