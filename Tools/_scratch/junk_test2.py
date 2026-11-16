import numpy as np
from PIL import Image
import cc

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
junkmask = junk[labs]
print("junk comps", int(junk.sum()), "junk px", int(junkmask.sum()))

content = opaque & ~junkmask
for p in [(0, 0), (1, 0), (0, 1), (1, 1)]:
    py, px = p
    A = content[py::2, px::2]
    B = content[py + 1::2, px::2] if py + 1 < H else A
    C = content[py::2, px + 1::2] if px + 1 < W else A
    D = content[py + 1::2, px + 1::2]
    m = min(A.shape[0], B.shape[0], C.shape[0], D.shape[0]), min(A.shape[1], C.shape[1])
    a4 = A[:m[0], :m[1]].astype(np.int8) + B[:m[0], :m[1]] + C[:m[0], :m[1]] + D[:m[0], :m[1]]
    mismatch = np.abs(a4 - (a4 >= 2) * 4).sum() / 4.0
    print("phase", p, "mismatch frac %.4f" % (mismatch / a4.size))

out = np.array(Image.open(SRC).convert("RGBA"))
out[junkmask] = (255, 0, 0, 255)
Image.fromarray(out).save(r"D:\Unity\Super Mario Bros\Tools\junk_vis.png")
