#!/usr/bin/env python3
"""Playwright smoke test for every generated page, at 390 px and 1440 px.

Per page and width: no horizontal overflow; exactly one <h1>; every <img> has alt text (alt=""
only for a decorative image inside a link that has its own text); every visible .btn has text
contrast >= 4.5:1 against what is behind it. Once per site: every internal link returns 200;
choosing a plan in a picker moves the sticky bar to the same plan (when the page has both).
Third-party requests are blocked, so nothing is sent anywhere.

    python3 tools/smoke.py              # checks only
    python3 tools/smoke.py --shots DIR  # also save fold + full-page screenshots
Writes tools/out/smoke.json.
"""
import glob
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from playwright.sync_api import sync_playwright
from testlib import ROOT, serve, block_third_party

CHECK_STICKY = True
WIDTHS = {"mobile": (390, 844), "desktop": (1440, 900)}

PAGE_JS = r"""() => {
  function rgb(s){ const m=s.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p=m[1].split(',').map(x=>parseFloat(x)); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; }
  function lum(c){ const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); }
  function bgOf(el){ let e=el; while(e){ const c=rgb(getComputedStyle(e).backgroundColor); if(c&&c.a>0.5) return c; e=e.parentElement; } return {r:255,g:255,b:255,a:1}; }
  function ratio(a,b){ const x=lum(a),y=lum(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); }
  const out={overflow: document.documentElement.scrollWidth - window.innerWidth, h1: document.querySelectorAll('h1').length, imgs: [], btns: []};
  document.querySelectorAll('img').forEach(i=>{ const alt=i.getAttribute('alt'); const a=i.closest('a');
    const deco = alt==='' && a && a.textContent.trim().length>0;
    if(alt===null || (alt.trim()==='' && !deco)) out.imgs.push(i.getAttribute('src')); });
  document.querySelectorAll('.btn').forEach(b=>{ const r=b.getBoundingClientRect(); if(!r.width||!r.height||getComputedStyle(b).visibility==='hidden') return;
    const fg=rgb(getComputedStyle(b).color), bg=bgOf(b); const cr=ratio(fg,bg);
    if(cr<4.5) out.btns.push({text:b.textContent.trim().slice(0,40), ratio:Math.round(cr*100)/100}); });
  out.links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'));
  return out;
}"""


def pages():
    out = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    return out


def main(argv):
    shots = argv[argv.index("--shots") + 1] if "--shots" in argv else None
    if shots:
        os.makedirs(shots, exist_ok=True)
    fails, report, links = [], {}, set()
    with serve() as base, sync_playwright() as p:
        b = p.chromium.launch()
        for label, (w, h) in WIDTHS.items():
            ctx = b.new_context(viewport={"width": w, "height": h})
            block_third_party(ctx, base)
            ctx.add_init_script("try{localStorage.setItem('tmu_notice','1')}catch(e){}")
            pg = ctx.new_page()
            for fn in pages():
                path = "/" + ("" if fn == "index.html" else fn)
                pg.goto(base + path, wait_until="domcontentloaded")
                pg.wait_for_timeout(150)
                r = pg.evaluate(PAGE_JS)
                key = f"{label}:{fn}"
                report[key] = {k: v for k, v in r.items() if k != "links"}
                for href in r["links"]:
                    u = urllib.parse.urljoin(base + path, href)
                    if u.startswith(base):
                        links.add(u.split("#")[0])
                if r["overflow"] > 1:
                    fails.append(f"{key}: horizontal overflow {r['overflow']}px")
                if r["h1"] != 1 and fn != "404.html" or (fn == "404.html" and r["h1"] != 1):
                    fails.append(f"{key}: {r['h1']} <h1> elements")
                for src in r["imgs"]:
                    fails.append(f"{key}: image without alt text: {src}")
                for bt in r["btns"]:
                    fails.append(f"{key}: button contrast {bt['ratio']}:1 < 4.5 ({bt['text']!r})")
                # sticky bar follows the picker
                if CHECK_STICKY and label == "mobile" and pg.locator("[data-picker]:visible").count() and pg.locator(".sticky a[data-buy]").count():
                    pk = pg.locator("[data-picker]:visible").first
                    for plan in ("onetime", "subscribe"):
                        pk.locator(f"input[value={plan}]").locator("xpath=..").click()
                        got = pg.locator(".sticky a[data-buy]").get_attribute("data-buy")
                        btn = pk.locator("[data-picker-btn]").get_attribute("data-buy")
                        if got != plan or btn != plan:
                            fails.append(f"{key}: picked {plan}, picker button={btn}, sticky={got}")
                if shots:
                    stem = fn[:-5]
                    pg.screenshot(path=os.path.join(shots, f"{label}_{stem}_fold.png"))
                    pg.screenshot(path=os.path.join(shots, f"{label}_{stem}_full.png"), full_page=True)
            ctx.close()
        b.close()
        for u in sorted(links):
            try:
                code = urllib.request.urlopen(urllib.request.Request(u, method="GET"), timeout=10).status
            except urllib.error.HTTPError as e:
                code = e.code
            if code != 200:
                fails.append(f"internal link {u[len(base):]} -> {code}")
    os.makedirs(os.path.join(ROOT, "tools", "out"), exist_ok=True)
    json.dump({"fails": fails, "pages": report, "links_checked": len(links)},
              open(os.path.join(ROOT, "tools", "out", "smoke.json"), "w"), indent=1)
    for f in fails:
        print("FAIL", f)
    print(f"smoke: {len(report)} page views, {len(links)} internal links, {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
