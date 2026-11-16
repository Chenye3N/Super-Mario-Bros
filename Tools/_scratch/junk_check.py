import numpy as np
from PIL import Image
import cc, json

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
a = np.array(Image.open(SRC).convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
opaque = al > 0
nonwhite = opaque & ~white
labs, n = cc.label(white)
bb = cc.bboxes(labs, n)
junk = np.zeros(n + 1, bool)
H, W = opaque.shape
for i in range(1, n + 1):
    b = bb[i]
    if b is None:
        continue
    x0, y0, x1, y1 = b["x0"], b["y0"], b["x1"], b["y1"]
    rx0, ry0 = max(0, x0 - 1), max(0, y0 - 1)
    rx1, ry1 = min(W, x1 + 1), min(H, y1 + 1)
    sub = nonwhite[ry0:ry1, rx0:rx1].copy()
    sub[y0 - ry0:y1 - ry0, x0 - rx0:x1 - rx0] = False
    if not sub.any():
        junk[i] = True
jm = junk[labs]
print("frame pixel (330,24) junk?", bool(jm[24, 330]))
g = json.load(open(r"D:\Unity\Super Mario Bros\Tools\guides.json"))
for b in g["rings"]:
    x0, y0, x1, y1 = b["x0"], b["y0"], b["x1"], b["y1"]
    top = jm[y0, x0:x1].mean()
    print("ring %4d..%4d %4d..%4d junk_top=%.2f" % (x0, x1, y0, y1, top))
print("junk px", int(jm.sum()))
