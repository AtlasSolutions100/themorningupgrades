#!/usr/bin/env python3
"""Studio pack shot: the real bag cutout (img/bag.png) on a warm seamless backdrop -> img/packshot.jpg.

Nothing about the bag is changed: it is only scaled (down, so it stays sharp) and placed. The backdrop,
the light falloff and the contact shadow are drawn here in code; there are no props.
The frame is 1600x2000 (4:5). The bag sits in the lower middle so the phone crops still show all of it:
home hero 16:10 at object-position 50% 62% (rows 620 to 1620), /shop stage 50% 70%.

Run:  python3 tools/packshot.py && python3 tools/images.py && python3 build_site.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 2000
BAG_H = 930                       # px tall in the frame (the cutout is 1000 tall, so 0.93x, no upscaling)
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

    bag = Image.open(os.path.join(ROOT, "img", "bag.png")).convert("RGBA")
    s = BAG_H / bag.height
    bag = bag.resize((round(bag.width * s), BAG_H), Image.LANCZOS)
    bx = (W - bag.width) // 2 + 20           # a touch right of centre, the light side has room
    by = BASE_Y - bag.height

    def ellipse(cx, cy, rx, ry, blur):
        """A soft elliptical shadow (0..1) centred at (cx, cy)."""
        e = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1).astype(np.uint8) * 255
        return np.array(Image.fromarray(e, "L").filter(ImageFilter.GaussianBlur(blur)), float) / 255

    cx = bx + bag.width / 2
    # tight contact shadow where the gusset meets the floor; most of it sits behind the bag
    contact = ellipse(cx, BASE_Y - 6, bag.width * 0.44, 16, 7)
    # ambient occlusion: a wider, soft pool around the base
    ambient = ellipse(cx + 10, BASE_Y + 4, bag.width * 0.58, 46, 30)
    # long soft cast shadow falling back and to the right, away from the key light
    cast = ellipse(cx + bag.width * 0.32, BASE_Y - 30, bag.width * 0.62, 90, 70)
    dark = 1 - (0.42 * contact + 0.22 * ambient + 0.12 * cast)
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
