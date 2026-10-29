#!/usr/bin/env python3
"""Responsive, label-safe images for the site.

1. CROPS: framings of the original photos that leave the bag's sub-line (the words under the
   wordmark) out of frame. The product itself is never edited: these are crops only (owner
   decision D3). Originals in img/ are kept as they are (ads and old links point at them).
2. Every crop is written to img/opt/ as WebP and JPEG at 480/800/1200 px wide, plus
   img/opt/manifest.json (name -> intrinsic size and widths) that build_site.py reads.

Run after changing a crop or adding a photo:  python3 tools/images.py && python3 build_site.py
"""
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img")
OUT = os.path.join(ROOT, "img", "opt")
WIDTHS = (480, 800, 1200)

# name: (source file in img/, crop box in source pixels (left, top, right, bottom))
CROPS = {
    "breakfast-top":    ("hero_breakfast.jpg", (0, 0, 1200, 932)),     # bag, logo, wordmark, morning light
    "breakfast-og":     ("hero_breakfast.jpg", (0, 302, 1200, 932)),   # 1200x630 share image
    "shadows-top":      ("bag_shadows.jpg", (0, 0, 1200, 995)),
    "desk-top":         ("desk.jpg", (0, 0, 1200, 1478)),
    "kitchen-pour-top": ("kitchen_pour.jpg", (0, 0, 1200, 1312)),
    "scoop-top":        ("scoop.jpg", (0, 0, 1200, 1408)),
    "pour-top":         ("pour.jpg", (0, 0, 1200, 1298)),
    "flatlay-right":    ("flatlay.jpg", (564, 0, 1200, 1200)),          # mug, scoop, sunglasses
    "gym-face":         ("gym.jpg", (528, 0, 1200, 1116)),
    "patio-left":       ("patio_iced.jpg", (0, 150, 830, 1188)),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for name, (src, box) in CROPS.items():
        im = Image.open(os.path.join(SRC, src)).convert("RGB").crop(box)
        w0, h0 = im.size
        widths = [w for w in WIDTHS if w < w0] + [w0] if w0 not in WIDTHS else [w for w in WIDTHS if w <= w0]
        widths = sorted(set(min(w, w0) for w in widths))
        for w in widths:
            h = round(h0 * w / w0)
            r = im if w == w0 else im.resize((w, h), Image.LANCZOS)
            r.save(os.path.join(OUT, f"{name}-{w}.webp"), "WEBP", quality=78, method=6)
            r.save(os.path.join(OUT, f"{name}-{w}.jpg"), "JPEG", quality=80, optimize=True, progressive=True)
        manifest[name] = {"w": w0, "h": h0, "widths": widths, "src": src}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print("wrote", len(manifest), "images to img/opt/")


if __name__ == "__main__":
    main()
