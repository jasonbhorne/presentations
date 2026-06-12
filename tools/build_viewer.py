#!/usr/bin/env python3
"""Build image-viewer index.html for each image-type deck in presentations.json.

A "viewer" is a self-contained page that flips through slide JPGs in <slug>/slides/.
Interactive decks (hand-built HTML) are skipped. Run from anywhere:
    python3 tools/build_viewer.py            # all image decks
    python3 tools/build_viewer.py <slug>     # just one
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "presentations.json")


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def list_slides(slug):
    sdir = os.path.join(REPO, slug, "slides")
    if not os.path.isdir(sdir):
        return []
    files = [f for f in os.listdir(sdir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    return sorted(files, key=natural_key)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600&display=swap" rel="stylesheet">
<style>
  :root {{ --accent:#c0392b; --muted:#cdbfa3; --body:'Source Serif 4',serif; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#14100a; overflow:hidden; font-family:var(--body); }}
  .stage {{ position:fixed; inset:0; display:flex; align-items:center; justify-content:center; }}
  .stage img {{ max-width:100vw; max-height:100vh; object-fit:contain; display:block; user-select:none; -webkit-user-drag:none; }}
  /* subtle chrome that does not fight the slide */
  .back {{ position:fixed; top:16px; left:20px; z-index:10; font-size:13px; letter-spacing:0.08em;
           text-transform:uppercase; color:#fff; opacity:0.55; text-decoration:none; mix-blend-mode:difference; }}
  .back:hover {{ opacity:1; }}
  .counter {{ position:fixed; bottom:16px; right:22px; z-index:10; font-size:13px; color:#fff;
              opacity:0.5; mix-blend-mode:difference; }}
  .dots {{ position:fixed; bottom:14px; left:50%; transform:translateX(-50%); display:flex; gap:7px;
           z-index:10; max-width:70vw; flex-wrap:wrap; justify-content:center; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:#fff; opacity:0.3; cursor:pointer;
          border:none; padding:0; transition:all .25s; }}
  .dot.active {{ background:var(--accent); opacity:1; transform:scale(1.4); }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition-duration:0.01ms !important; }} }}
</style>
</head>
<body>
  <div class="stage"><img id="slide" alt="{title} slide"></div>
  <a class="back" href="../">&larr; All talks</a>
  <div class="counter" id="counter"></div>
  <nav class="dots" id="dots" aria-label="Slide navigation"></nav>
<script>
  const SLIDES = {slides_json};
  const BASE = "slides/";
  let i = 0;
  const img = document.getElementById('slide');
  const counter = document.getElementById('counter');
  const dotsNav = document.getElementById('dots');
  const pad = n => String(n).padStart(2,'0');

  // preload
  SLIDES.forEach(s => {{ const p = new Image(); p.src = BASE + s; }});

  SLIDES.forEach((_, idx) => {{
    const d = document.createElement('button');
    d.className = 'dot' + (idx===0?' active':'');
    d.setAttribute('aria-label', 'Go to slide ' + (idx+1));
    d.addEventListener('click', e => {{ e.stopPropagation(); go(idx); }});
    dotsNav.appendChild(d);
  }});
  const dots = [...document.querySelectorAll('.dot')];

  function go(n) {{
    if (n < 0 || n >= SLIDES.length) return;
    i = n;
    img.src = BASE + SLIDES[i];
    counter.textContent = pad(i+1) + ' / ' + pad(SLIDES.length);
    dots.forEach((d,j) => d.classList.toggle('active', j===i));
  }}
  const next = () => go(i+1), prev = () => go(i-1);

  document.addEventListener('keydown', e => {{
    if (e.key==='ArrowRight'||e.key===' ') {{ e.preventDefault(); next(); }}
    if (e.key==='ArrowLeft') prev();
    if (e.key==='Home') go(0);
    if (e.key==='End') go(SLIDES.length-1);
  }});
  document.addEventListener('click', e => {{
    if (e.target.closest('a, button')) return;
    (e.clientX > window.innerWidth/2) ? next() : prev();
  }});
  let tx = 0;
  document.addEventListener('touchstart', e => {{ tx = e.touches[0].clientX; }}, {{passive:true}});
  document.addEventListener('touchend', e => {{
    const d = tx - e.changedTouches[0].clientX;
    if (Math.abs(d) > 50) (d>0 ? next() : prev());
  }}, {{passive:true}});
  let wheelLock = false;
  document.addEventListener('wheel', e => {{
    if (wheelLock) return; wheelLock = true; setTimeout(()=>wheelLock=false, 600);
    (e.deltaY>0 ? next() : prev());
  }}, {{passive:true}});

  go(0);
</script>
</body>
</html>
"""


def build_one(entry):
    slug = entry["slug"]
    slides = list_slides(slug)
    if not slides:
        print(f"  SKIP {slug}: no slides found")
        return False
    html = TEMPLATE.format(
        title=entry["title"].replace("{", "{{").replace("}", "}}"),
        slides_json=json.dumps(slides),
    )
    out = os.path.join(REPO, slug, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"  built {slug}/index.html ({len(slides)} slides)")
    return True


def main():
    with open(MANIFEST) as f:
        manifest = json.load(f)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for entry in manifest:
        if entry.get("type") != "images":
            continue
        if only and entry["slug"] != only:
            continue
        build_one(entry)


if __name__ == "__main__":
    main()
