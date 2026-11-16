import numpy as np
from PIL import Image

p = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
a = np.array(Image.open(p).convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]

PEACH = np.array([255, 207, 190])
peach = (np.abs(rgb - PEACH).sum(-1) <= 6) & (al > 0)
print("peach total", peach.sum())

H, W = peach.shape


def runs(mask_1d, minlen):
    """Return list of (start, end_exclusive) for True runs >= minlen."""
    out = []
    idx = np.flatnonzero(np.diff(np.r_[0, mask_1d.astype(np.int8), 0]))
    for s, e in zip(idx[::2], idx[1::2]):
        if e - s >= minlen:
            out.append((s, e))
    return out


hsegs = []  # (y, x0, x1)
for y in range(H):
    for s, e in runs(peach[y], 30):
        hsegs.append((y, s, e))
vsegs = []  # (x, y0, y1)
for x in range(W):
    for s, e in runs(peach[:, x], 30):
        vsegs.append((x, s, e))

print("hsegs", len(hsegs), "vsegs", len(vsegs))
for s in hsegs[:40]:
    print("H y=%d x=%d..%d len=%d" % (s[0], s[1], s[2], s[2] - s[1]))
print("...")
for s in vsegs[:40]:
    print("V x=%d y=%d..%d len=%d" % (s[0], s[1], s[2], s[2] - s[1]))
