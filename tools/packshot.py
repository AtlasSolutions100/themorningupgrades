#!/usr/bin/env python3
"""Studio pack shot: a real bag on a warm seamless backdrop -> img/packshot.jpg.

The bag is img/bag_photo.png: the bag cut out of the owner's own phone photo of a real bag
(Nov 2026; background removed with rembg isnet-general-use, nothing else changed: no retouching,
recolouring or label edits; his counter and tiles are gone). BAG_SRC can point back at img/bag.png.

Nothing about the bag is changed: it is only scaled (down, so it stays sharp) and placed. The backdrop,
the light falloff and the contact shadow are drawn here in code; there are no props.
The frame is 1600x2000 (4:5). The bag sits in the lower middle so the phone crops still show all of it:
/shop stage at object-position 50% 70%, /corejava-coffee 50% 58% (the home hero is now tools/hero_scene.py).

Run:  python3 tools/packshot.py && python3 tools/images.py && python3 build_site.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 2000
BAG_SRC = "bag_photo.png"         # 883x1075 cutout of the real bag photo
BAG_H = 930                       # px tall in the frame (0.87x of the cutout, so no upscaling)
BASE_Y = 1585                     # where the bottom of the bag touches the floor
WALL = np.array([226, 216, 201], float)    # a shade under --linen (#ECE6DB), warm
FLOOR = np.array([238, 231, 220], float)   # floor in the light, near --linen/--ivory
SWEEP_Y = 1380                    # where the backdrop curves from wall into floor


def main():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # seamless sweep: wall colour above, floor colour below, a long smooth curve between
    t = np.clip((yy - (SWEEP_Y - 420)) / 640, 0, 1)
    t = t * t * (3 - 2 * t)
    bg = WALL[None, None, :] * (1 - t[..., None]) + FLOOR[None, None, :] * t[..., None]
    # one soft key light from the upper left: gentle brightening there, falloff to the corners
    d = np.hypot((xx - 0.36 * W) / W, (yy - 0.30 * H) / H)
    bg *= (1.045 - 0.16 * np.clip(d, 0, 1.2) ** 1.6)[..., None]
    # floor falls off toward the front edge a little
    bg *= (1 - 0.05 * np.clip((yy - BASE_Y) / (H - BASE_Y), 0, 1))[..., None]

    bag = Image.open(os.path.join(ROOT, "img", BAG_SRC)).convert("RGBA")
    s = BAG_H / bag.height
    bag = bag.resize((round(bag.width * s), BAG_H), Image.LANCZOS)
    bx = (W - bag.width) // 2 + 20           # a touch right of centre, the light side has room
    by = BASE_Y - bag.height

    def ellipse(cx, cy, rx, ry, blur):
        """A soft elliptical shadow (0..1) centred at (cx, cy)."""
        e = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1).astype(np.uint8) * 255
        return np.array(Image.fromarray(e, "L").filter(ImageFilter.GaussianBlur(blur)), float) / 255

    cx = bx + bag.width / 2
    # tight contact shadow that follows the bag's own bottom edge: its silhouette moved down a few px
    # and blurred, so only a thin dark line peeks out under the gusset
    sil = Image.new("L", (W, H), 0)
    sil.paste(bag.split()[3], (bx, by + 7))
    contact = np.array(sil.filter(ImageFilter.GaussianBlur(6)), float) / 255
    contact *= np.clip((yy - (BASE_Y - 140)) / 100, 0, 1)   # only near the floor, not up the sides
    # ambient occlusion: a wider, soft pool around the base
    ambient = ellipse(cx + 10, BASE_Y + 4, bag.width * 0.58, 46, 30)
    # long soft cast shadow falling back and to the right, away from the key light
    cast = ellipse(cx + bag.width * 0.32, BASE_Y - 30, bag.width * 0.62, 90, 70)
    dark = 1 - (0.38 * contact + 0.22 * ambient + 0.12 * cast)
    dark = np.clip(dark, 0.35, 1)
    bg *= dark[..., None]

    # fine grain so the backdrop reads as paper, not a flat fill
    rng = np.random.default_rng(7)
    bg += rng.normal(0, 1.6, (H, W, 1))
    canvas = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    canvas.alpha_composite(bag, (bx, by))
    canvas.convert("RGB").save(os.path.join(ROOT, "img", "packshot.jpg"), "JPEG", quality=92, optimize=True)
    print("wrote img/packshot.jpg", canvas.size, "bag", bag.size, "at", (bx, by))


if __name__ == "__main__":
    main()
