import numpy as np
from PIL import Image
import cc

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
a = np.array(Image.open(SRC).convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
opaque = al > 0

labs, n = cc.label(white)
bb = cc.bboxes(labs, n)

# ring check: is there any opaque pixel in the 1px ring around the bbox (excluding the comp itself)?
junk = np.zeros(n + 1, bool)
report = []
for i in range(1, n + 1):
    b = bb[i]
    if b is None:
        continue
    x0, y0, x1, y1 = b["x0"], b["y0"], b["x1"], b["y1"]
    rx0, ry0 = max(0, x0 - 1), max(0, y0 - 1)
    rx1, ry1 = min(a.shape[1], x1 + 1), min(a.shape[0], y1 + 1)
    sub = opaque[ry0:ry1, rx0:rx1].copy()
    # remove the comp's own bbox area
    sub[y0 - ry0:y1 - ry0, x0 - rx0:x1 - rx0] = False
    if not sub.any():
        junk[i] = True
        report.append((i, b, x1 - x0, y1 - y0))

print("total white comps", n, "junk", len(report))
junkmask = junk[labs]
print("junk px", int(junkmask.sum()), "of white", int(white.sum()))

# what does non-junk pure white look like?
keep = white & ~junkmask
print("kept pure-white px", int(keep.sum()))
kb = [(i, bb[i]) for i in range(1, n + 1) if bb[i] and not junk[i] and (bb[i]["x1"]-bb[i]["x0"])*(bb[i]["y1"]-bb[i]["y0"]) < 4000]
print("kept small white comps", len(kb))
for i, b in kb[:40]:
    print("   ", b["x0"], b["y0"], b["x1"], b["y1"], b["area"])

out = np.array(Image.open(SRC).convert("RGBA"))
out[junkmask] = (255, 0, 0, 255)
Image.fromarray(out).save(r"D:\Unity\Super Mario Bros\Tools\junk_vis.png")

# alignment parity of remaining content
content = opaque & ~junkmask
cl, cn = cc.label(content)
cb = cc.bboxes(cl, cn)
even = sum(1 for b in cb[1:] if b and b["x0"] % 2 == 0 and b["y0"] % 2 == 0 and b["x1"] % 2 == 0 and b["y1"] % 2 == 0)
print("content comps", cn, "fully even-aligned", even)
print("x0 parity counts", np.bincount([b["x0"] % 2 for b in cb[1:] if b]).tolist(),
      "y0 parity", np.bincount([b["y0"] % 2 for b in cb[1:] if b]).tolist())
np.save(r"D:\Unity\Super Mario Bros\Tools\junkmask.npy", junkmask)
