"""Slice SuperMarioBors.png into individual sprites, one folder per labelled section."""
import json
import os
import numpy as np
from PIL import Image
import cc

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
OUT = r"D:\Unity\Super Mario Bros\Tools\out"

# frame rectangles detected from the white guide boxes (verified: top edge 100% white, removed as junk)
# name, x0, y0, x1, y1
SECTIONS = [
    dict(name="CommonObjects", x0=7, y0=24, x1=318, y1=399),
    dict(name="PowerUps", x0=322, y0=24, x1=495, y1=211),
    dict(name="OutsideScenery", x0=604, y0=28, x1=916, y1=460),
    dict(name="HelpfulObjects", x0=323, y0=255, x1=592, y1=399),
    dict(name="Castle", x0=7, y0=426, x1=335, y1=822),
    dict(name="BowserCastle", x0=342, y0=427, x1=521, y1=607),
    dict(name="Pipes", x0=531, y0=483, x1=779, y1=643),
    dict(name="BackgroundColours", x0=793, y0=485, x1=995, y1=586),
    dict(name="UnderwaterScenery", x0=344, y0=628, x1=465, y1=887),
    dict(name="Transformed", x0=728, y0=843, x1=1081, y1=1038),
    dict(name="Mario", x0=10, y0=898, x1=359, y1=1278),
    dict(name="Luigi", x0=365, y0=909, x1=717, y1=1286),
    dict(name="Bloopa", x0=734, y0=1064, x1=820, y1=1128),
    dict(name="Lakitu", x0=832, y0=1064, x1=957, y1=1129),
    dict(name="Spiny", x0=961, y0=1085, x1=1126, y1=1129),
    dict(name="HammerBros", x0=735, y0=1158, x1=1058, y1=1285),
    dict(name="PrincessAndToad", x0=14, y0=1301, x1=105, y1=1362),
    dict(name="Goombas", x0=119, y0=1312, x1=491, y1=1363),
    dict(name="Beetle", x0=500, y0=1312, x1=713, y1=1442),
    dict(name="Piranha", x0=727, y0=1312, x1=834, y1=1436),
    dict(name="StarPower", x0=839, y0=1312, x1=1178, y1=1627),
    dict(name="Bowser", x0=15, y0=1392, x1=344, y1=1505),
    dict(name="BulletBill", x0=358, y0=1425, x1=467, y1=1505),
    dict(name="FireBalls", x0=17, y0=1530, x1=300, y1=1589),
    dict(name="CheepCheep", x0=329, y0=1540, x1=590, y1=1589),
]


def content_mask(a):
    """alpha>0 minus the sheet's white guide layer (1px section rectangles and label text)."""
    rgb = a[..., :3].astype(np.int32)
    al = a[..., 3]
    white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
    opaque = al > 0
    nonwhite = opaque & ~white
    H, W = opaque.shape
    labs, n = cc.label(white)
    bb = cc.bboxes(labs, n)
    junk = np.zeros(n + 1, bool)
    R = 2
    for i in range(1, n + 1):
        b = bb[i]
        if b is None:
            continue
        x0, y0, x1, y1 = b["x0"], b["y0"], b["x1"], b["y1"]
        w, h = x1 - x0, y1 - y0
        # 1) section rectangles: full top edge and full left edge are white
        if white[y0, x0:x1].all() and white[y0:y1, x0].all():
            junk[i] = True
            continue
        # 2) label text: small pure-white glyphs whose surroundings hold no other colour
        if h <= 13 and w <= 60:
            rx0, ry0 = max(0, x0 - R), max(0, y0 - R)
            rx1, ry1 = min(W, x1 + R), min(H, y1 + R)
            sub = nonwhite[ry0:ry1, rx0:rx1].copy()
            sub[y0 - ry0:y1 - ry0, x0 - rx0:x1 - rx0] = False
            if not sub.any():
                junk[i] = True
    return opaque & ~junk[labs]


def xycut(mask, ox, oy, out):
    if not mask.any():
        return
    empty_rows = ~mask.any(axis=1)
    if empty_rows.any():
        bands = runs(~empty_rows)
        if len(bands) > 1:
            for (r0, r1) in bands:
                xycut(mask[r0:r1], ox, oy + r0, out)
            return
    empty_cols = ~mask.any(axis=0)
    if empty_cols.any():
        cols = runs(~empty_cols)
        if len(cols) > 1:
            for (c0, c1) in cols:
                xycut(mask[:, c0:c1], ox + c0, oy, out)
            return
    ys, xs = np.nonzero(mask)
    out.append((ox + int(xs.min()), oy + int(ys.min()), ox + int(xs.max()) + 1, oy + int(ys.max()) + 1))


def runs(bool_row):
    d = np.diff(np.r_[0, bool_row.astype(np.int8), 0])
    s = np.flatnonzero(d == 1)
    e = np.flatnonzero(d == -1)
    return list(zip(s.tolist(), e.tolist()))


def main():
    a = np.array(Image.open(SRC).convert("RGBA"))
    cm = content_mask(a)
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    total = 0
    for sec in SECTIONS:
        name = sec["name"]
        x0, y0, x1, y1 = sec["x0"], sec["y0"], sec["x1"], sec["y1"]
        sub = cm[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
        rects = []
        xycut(sub, x0 + 1, y0 + 1, rects)
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        info = []
        for i, (rx0, ry0, rx1, ry1) in enumerate(rects, 1):
            # tighten to actual content
            m = cm[ry0:ry1, rx0:rx1]
            ys, xs = np.nonzero(m)
            rx0, ry0 = rx0 + int(xs.min()), ry0 + int(ys.min())
            rx1, ry1 = rx0 + int(xs.max()) - int(xs.min()) + 1, ry0 + int(ys.max()) - int(ys.min()) + 1
            crop = a[ry0:ry1, rx0:rx1].copy()
            if not crop[..., 3].any():
                continue
            fn = "%s_%02d.png" % (name, i)
            Image.fromarray(crop).save(os.path.join(d, fn))
            info.append(dict(file=fn, x=rx0, y=ry0, w=rx1 - rx0, h=ry1 - ry0))
        manifest[name] = info
        total += len(info)
        sizes = sorted({(v["w"], v["h"]) for v in info})
        print("%-18s %3d sprites  sizes=%s" % (name, len(info), sizes[:12]))
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print("TOTAL", total)


if __name__ == "__main__":
    main()
