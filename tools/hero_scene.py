#!/usr/bin/env python3
"""Home hero scene: the REAL bag photo composited onto a generated still-life plate -> img/hero_scene.jpg.

The plate (img/hero_scene_plate.jpg) is AI-generated (Higgsfield, GPT Image 2.5, Nov 2026): travertine
counter, window light from the left, a cup of black coffee, a brass spoon on linen. It has no bag, no
package and no text. The bag is img/bag_photo.png (the owner's own phone photo, background removed).
All coordinates are in the 1600x2000 output frame. The phone crop (16:10, object-position 50% 45%
in assets/site.css) shows rows 450 to 1450, so the bag (rows 500 to 1400) stays whole.

The bag's pixels are only scaled and given a global white balance / exposure grade, a broad left-to-right
light falloff, a soft light wrap at the outer edge and grain: no retouching, no recolouring of the print,
no label edits. The contact, ambient and cast shadows and the faint reflection are drawn on the plate.

Run:  python3 tools/hero_scene.py && python3 tools/images.py && python3 build_site.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

W, H = 1600, 2000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bag_p = os.path.join(ROOT, "img", "bag_photo.png")
bg_p = os.path.join(ROOT, "img", "hero_scene_plate.jpg")
out_p = os.path.join(ROOT, "img", "hero_scene.jpg")
BAG_H, BASE_Y, CX = 900, 1400, 520   # bag height (0.84x of the cutout: scaled down only), floor line, centre x
WARM = 1.0     # white balance shift toward the plate's warm light
GAIN = 1.0     # exposure
REFL = 0.22    # faint mirror reflection on the polished counter

bg_im = Image.open(bg_p).convert("RGB").resize((W, H), Image.LANCZOS)
bg = np.asarray(bg_im, float)

bag = Image.open(bag_p).convert("RGBA")
# matte cleanup only: choke the alpha by 1px so no wall/counter fringe from the cutout survives
r_, g_, b_, al_ = bag.split()
bag = Image.merge("RGBA", (r_, g_, b_, al_.filter(ImageFilter.MinFilter(3))))
s = BAG_H / bag.height
bag = bag.resize((round(bag.width * s), BAG_H), Image.LANCZOS)
bw, bh = bag.size
bx, by = CX - bw // 2, BASE_Y - bh

# ---- full-frame alpha of the bag
A = Image.new("L", (W, H), 0)
A.paste(bag.split()[3], (bx, by))
a = np.asarray(A, float) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(float)


def blur(arr, r):
    return np.asarray(Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r)), float) / 255


# ---- shadows on the counter (light from the upper left: cast shadow goes back and to the right)
# contact: silhouette nudged down, tight blur, only near the floor line
contact = blur(np.roll(a, 6, axis=0), 5) * np.clip((yy - (BASE_Y - 120)) / 90, 0, 1)
# ambient occlusion pool under the base
amb = ((((xx - CX) / (bw * 0.56)) ** 2 + ((yy - BASE_Y - 2) / 34) ** 2) <= 1).astype(float)
amb = blur(amb, 22)
# cast shadow: the silhouette laid on the counter plane (squashed, sheared right, extending back)
sil = bag.split()[3]
sq = sil.resize((bw, max(1, int(bh * 0.36))), Image.LANCZOS)
sh_h = sq.height
shear = 1.15           # px right per px back
pad = int(sh_h * shear) + 10
sh = Image.new("L", (bw + pad, sh_h), 0)
sh.paste(sq, (0, 0))
sh = sh.transform(sh.size, Image.AFFINE, (1, shear, -shear * sh_h, 0, 1, 0), Image.BILINEAR)
C = Image.new("L", (W, H), 0)
C.paste(sh, (bx + 18, BASE_Y - sh_h + 4))
cast = blur(np.asarray(C, float) / 255, 18)
# fade the cast shadow as it goes back (softer, lighter farther from the base)
cast *= np.clip(1 - (BASE_Y - yy) / (sh_h * 1.2), 0, 1) ** 0.8
dark = np.clip(1 - (0.55 * contact + 0.34 * amb + 0.42 * cast), 0.3, 1)
tint = np.array([1.0, 0.97, 0.93])      # warm, slightly brown shadows like the cup's
shade = dark[..., None] ** (1 / tint)[None, None, :]
out = bg * shade
if REFL > 0:   # a faint, blurred, fading mirror image of the bag's lower part on the polished stone
    rh = 140
    part = bag.crop((0, bh - rh, bw, bh)).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(3))
    R = Image.new("RGBA", (W, H), (0, 0, 0, 0)); R.paste(part, (bx, BASE_Y - 2))
    rr = np.asarray(R, float); ra = rr[..., 3] / 255 * REFL * np.clip(1 - (yy - BASE_Y) / rh, 0, 1) ** 1.5
    out = out * (1 - ra[..., None]) + rr[..., :3] * ra[..., None]

# ---- grade the bag: global exposure + white balance toward the scene's warm light
bag_rgb = np.zeros((H, W, 3))
bag_rgb[by:by + bh, bx:bx + bw] = np.asarray(bag.convert("RGB"), float)
wb = np.array([1.0 + 0.07 * WARM, 1.0 + 0.015 * WARM, 1.0 - 0.09 * WARM]) * GAIN
g = bag_rgb * wb
# key light from the left: a broad, gentle left-to-right falloff across the whole bag (global, not local)
fall = 1.06 - 0.14 * np.clip((xx - bx) / bw, 0, 1)
g = g * fall[..., None]
# warm ambient bounce from the sunlit stone: a small even lift
g = g + np.array([4.0, 3.0, 1.0]) * WARM
# soft light wrap: blurred scene colour bleeding over the outer few px of the silhouette
inner = blur(a, 6)
wrap = np.clip(a - inner, 0, 1) * 0.9 + np.clip(a * (1 - blur(a, 14)), 0, 1) * 0.25
wrap = np.clip(wrap, 0, 0.55)
bg_blur = np.asarray(bg_im.filter(ImageFilter.GaussianBlur(20)), float)
g = g * (1 - wrap[..., None] * 0.35) + bg_blur * wrap[..., None] * 0.35
# grain like the plate
rng = np.random.default_rng(11)
g += rng.normal(0, 2.0, (H, W, 1)) * a[..., None]
# slightly softened matte edge
ae = blur(a, 0.7)
out = out * (1 - ae[..., None]) + g * ae[..., None]
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").save(out_p, "JPEG", quality=92, optimize=True)
print("wrote", out_p, "bag", (bw, bh), "at", (bx, by), "scale %.2f" % s)
