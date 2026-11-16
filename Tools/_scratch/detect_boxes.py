import json
import numpy as np
from PIL import Image

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
im = Image.open(SRC).convert("RGBA")
a = np.array(im)
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
H, W = al.shape
content = al > 0


def runs(mask_1d, minlen):
    out = []
    idx = np.flatnonzero(np.diff(np.r_[0, mask_1d.astype(np.int8), 0]))
    for s, e in zip(idx[::2], idx[1::2]):
        if e - s >= minlen:
            out.append((int(s), int(e)))
    return out


# long straight runs of ONE constant color = candidate guide lines
hlines, vlines = [], []
for y in range(H):
    row = rgb[y]
    x = 0
    while x < W:
        c = row[x]
        x2 = x
        while x2 < W and np.array_equal(row[x2], c):
            x2 += 1
        if x2 - x >= 40 and al[y, x] > 0:
            hlines.append((y, x, x2, tuple(c)))
        x = x2
for x in range(W):
    col = rgb[:, x]
    y = 0
    while y < H:
        c = col[y]
        y2 = y
        while y2 < H and np.array_equal(col[y2], c):
            y2 += 1
        if y2 - y >= 40 and al[y, x] > 0:
            vlines.append((x, y, y2, tuple(c)))
        y = y2

print("hlines", len(hlines), "vlines", len(vlines))
from collections import Counter
print("h colors", Counter(h[3] for h in hlines).most_common(6))
print("v colors", Counter(v[3] for v in vlines).most_common(6))
print("sample h", hlines[:8])
print("sample v", vlines[:8])

# Build rectangles: pair a horizontal top line with a horizontal bottom line of same x-range
hs = {}
for y, x0, x1 in [(h[0], h[1], h[2]) for h in hlines if h[3] == (255, 255, 255)]:
    hs.setdefault((x0, x1), []).append(y)

rects = []
for (x0, x1), ys in hs.items():
    ys = sorted(ys)
    for i in range(0, len(ys) - 1):
        if 40 < ys[i + 1] - ys[i] < 1200:
            rects.append((x0, ys[i], x1, ys[i + 1]))
rects = sorted(set(rects))
print("rects from h-pairs", len(rects))
for r in rects:
    print(r, "w=%d h=%d" % (r[2] - r[0], r[3] - r[1]))
json.dump(rects, open(r"D:\Unity\Super Mario Bros\Tools\rects_raw.json", "w"))
