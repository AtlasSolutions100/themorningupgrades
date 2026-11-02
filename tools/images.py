#!/usr/bin/env python3
"""Responsive images for the site.

Every photo is shown in its original framing (the owner confirmed in Oct 2026 that showing the
bag's real label on the site is fine; label-safe framing only matters in ads). Each entry below is
written to img/opt/ as WebP plus a fallback (JPEG, or PNG for cutouts and text graphics) at
480/800/1200 px wide and its own width, with img/opt/manifest.json (name -> intrinsic size, widths,
fallback extension) that build_site.py reads. Originals in img/ are kept as they are.

Run after adding or changing a photo:  python3 tools/images.py && python3 build_site.py
"""
import glob
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img")
OUT = os.path.join(ROOT, "img", "opt")
WIDTHS = (480, 800, 1200)
PAPER = (247, 243, 236)   # --paper in assets/site.css

# name: (source file in img/, options)
#   alpha: keep transparency (WebP with alpha + PNG fallback)
#   png:   PNG fallback instead of JPEG (text graphics stay crisp)
#   q:     WebP quality (default 78); aq: WebP alpha quality (default 100)
#   pad:   (w, h) compose the image centred on a --paper canvas of that size (share images)
#   avif:  also write AVIF (smaller than WebP; pic() lists it first). Used for the editorial stills.
#
# The lux_* stills (Oct 2026 redesign) are generated editorial photographs: cup, scoop, kettle,
# light. Where the bag appears it is soft-focus, partial or secondary; never a label close-up.
IMAGES = {
    "hero-props":       ("hero_props.png", {"alpha": True, "aq": 60}),   # hero: bag with coconut, MCT powder, beans, tea
    "props-og":         ("hero_props.png", {"pad": (1200, 630)}),       # 1200x630 share image
    "breakfast":        ("hero_breakfast.jpg", {}),
    "shadows":          ("bag_shadows.jpg", {}),
    "desk":             ("desk.jpg", {}),
    "kitchen-pour":     ("kitchen_pour.jpg", {}),
    "scoop":            ("scoop.jpg", {}),
    "pour":             ("pour.jpg", {}),
    "flatlay":          ("flatlay.jpg", {}),
    "gym":              ("gym.jpg", {}),
    "patio":            ("patio_iced.jpg", {}),
    "supplement-facts": ("supplement-facts.png", {"png": True, "q": 90}),
    "lux-hero":         ("lux_hero.jpg", {"avif": True}),          # cup and steam, bag soft at the frame edge
    "lux-scoop":        ("lux_scoop.jpg", {"avif": True}),         # a scoop over the cup
    "lux-pour":         ("lux_pour.jpg", {"avif": True}),          # kettle pour, steam
    "lux-cup":          ("lux_cup.jpg", {"avif": True}),           # top-down cup, morning light
    "lux-ingredients":  ("lux_ingredients.jpg", {"avif": True}),   # coffee, powder, tea leaves, coconut
    "lux-still":        ("lux_still.jpg", {"avif": True}),         # bag turned away, cup in focus
    "lux-table":        ("lux_table.jpg", {"avif": True}),         # morning table, bag far and soft
    "lux-iced":         ("lux_iced.jpg", {"avif": True}),          # iced, milk sinking
    "lux-pattern":      ("lux_pattern.jpg", {"avif": True}),       # the bag's copper line pattern, no text
    "lux-linen":        ("lux_linen.jpg", {"avif": True}),         # top-down linen, cup, bag at the edge
    "lux-og":           ("lux_og.jpg", {}),                        # 1200x630 share image: the hero cup
    # Nov 2026 second design pass: generated mood stills, no bag in frame
    "lux-darkpour":     ("lux_darkpour.jpg", {"avif": True}),      # slow pour into a charcoal stone cup, dark (the one dark band)
    "lux-stonecup":     ("lux_stonecup.jpg", {"avif": True}),      # cup on travertine, long window shadows (How to make it)
    "lux-granules":     ("lux_granules.jpg", {"avif": True}),      # a scoop of instant coffee granules on travertine
}


def load(src, opts):
    im = Image.open(os.path.join(SRC, src))
    if "pad" in opts:
        cw, ch = opts["pad"]
        im = im.convert("RGBA")
        s = min(cw / im.width, ch / im.height) * 0.94
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        canvas = Image.new("RGBA", (cw, ch), PAPER + (255,))
        canvas.alpha_composite(im, ((cw - im.width) // 2, (ch - im.height) // 2))
        return canvas.convert("RGB")
    return im.convert("RGBA" if opts.get("alpha") else "RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*")):
        os.remove(f)
    manifest = {}
    for name, (src, opts) in IMAGES.items():
        im = load(src, opts)
        w0, h0 = im.size
        widths = sorted({w for w in WIDTHS if w < w0} | {w0})
        ext = "png" if (opts.get("alpha") or opts.get("png")) else "jpg"
        for w in widths:
            h = round(h0 * w / w0)
            r = im if w == w0 else im.resize((w, h), Image.LANCZOS)
            r.save(os.path.join(OUT, f"{name}-{w}.webp"), "WEBP", quality=opts.get("q", 78), alpha_quality=opts.get("aq", 100), method=6)
            if opts.get("avif"):
                r.save(os.path.join(OUT, f"{name}-{w}.avif"), "AVIF", quality=58, speed=4)
            if ext == "png":
                q = r.quantize(256, method=Image.FASTOCTREE if r.mode == "RGBA" else Image.MEDIANCUT, dither=Image.NONE)
                q.save(os.path.join(OUT, f"{name}-{w}.png"), "PNG", optimize=True)
            else:
                r.save(os.path.join(OUT, f"{name}-{w}.jpg"), "JPEG", quality=80, optimize=True, progressive=True)
        manifest[name] = {"w": w0, "h": h0, "widths": widths, "src": src, "ext": ext}
        if opts.get("avif"):
            manifest[name]["avif"] = True
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print("wrote", len(manifest), "images to img/opt/")


if __name__ == "__main__":
    main()
