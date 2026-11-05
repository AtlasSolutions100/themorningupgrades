#!/usr/bin/env python3
"""Bundle images for /shop: the 2 real product images side by side on the --paper colour.

Left: the CoreJava bag (img/bag_photo.png, the owner's own photo of a real bag, cut out; scaled only).
Right: the house coffee bag design already used on its product page (img/house_cupofjoe.jpg or
img/house_mushroom.jpg), scaled only (its bag the same height as the CoreJava bag). Nothing on either
label is changed; only a soft contact shadow under the CoreJava bag is drawn here.

Writes img/bundle_cupofjoe.jpg and img/bundle_mushroom.jpg (1600x2000, 4:5, like the other cards).
Run:  python3 tools/bundle_shot.py && python3 tools/images.py && python3 build_site.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 2000
BG = (247, 242, 236)      # the house mockups' own background (close to --paper)
BAG_H = 860               # both bags this tall (CoreJava cutout is 1075 px: scaled down only)
BASE_Y = 1520             # where both bags stand
GAP = 70


def house_bag(fn):
    """The house mockup and the box of its bag (not its faint drawn shadow)."""
    im = Image.open(os.path.join(ROOT, "img", fn)).convert("RGB")
    a = np.abs(np.array(im).astype(int) - np.array(BG)).sum(2)
    ys, xs = np.nonzero(a > 30)
    return im, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def main():
    cj = Image.open(os.path.join(ROOT, "img", "bag_photo.png")).convert("RGBA")
    cj = cj.crop(cj.split()[3].getbbox())
    cj = cj.resize((round(cj.width * BAG_H / cj.height), BAG_H), Image.LANCZOS)
    for key in ("cupofjoe", "mushroom"):
        im, (l, t, r, b) = house_bag(f"house_{key}.jpg")
        s = BAG_H / (b - t)
        hw = round((r - l) * s)
        x0 = (W - (cj.width + GAP + hw)) // 2
        canvas = Image.new("RGB", (W, H), BG)
        # the whole mockup (its background is the same colour as ours, so its own drawn shadow carries over),
        # placed so its bag stands on BASE_Y right of the CoreJava bag
        big = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        hx, hy = x0 + cj.width + GAP - round(l * s), BASE_Y - round(b * s)
        canvas.paste(big, (hx, hy))
        # a soft contact shadow under the CoreJava bag only
        alpha = Image.new("L", (W, H), 0)
        alpha.paste(cj.split()[3], (x0, BASE_Y - BAG_H + 10))
        dark = 1 - 0.16 * np.array(alpha.filter(ImageFilter.GaussianBlur(18)), float) / 255
        bg = np.array(canvas, float) * dark[..., None]
        canvas = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        canvas.alpha_composite(cj, (x0, BASE_Y - BAG_H))
        out = os.path.join(ROOT, "img", f"bundle_{key}.jpg")
        canvas.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
        print("wrote", os.path.relpath(out, ROOT), "CoreJava", cj.size, key, (hw, BAG_H))


if __name__ == "__main__":
    main()
