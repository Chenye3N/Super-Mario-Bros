import numpy as np
from PIL import Image
from collections import Counter

a = np.array(Image.open(r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png").convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
H, W = al.shape

lens = Counter()
for y in range(0, H):
    row = rgb[y]
    x = 0
    while x < W:
        c = row[x]
        x2 = x
        while x2 < W and np.array_equal(row[x2], c):
            x2 += 1
        if al[y, x] > 0 and not (c[0] == 255 and c[1] == 255 and c[2] == 255):
            lens[x2 - x] += 1
        x = x2
print("top run lengths:", lens.most_common(20))

vl = Counter()
for x in range(0, W):
    col = rgb[:, x]
    y = 0
    while y < H:
        c = col[y]
        y2 = y
        while y2 < H and np.array_equal(col[y2], c):
            y2 += 1
        if al[y, x] > 0 and not (c[0] == 255 and c[1] == 255 and c[2] == 255):
            vl[y2 - y] += 1
        y = y2
print("top col run lengths:", vl.most_common(20))
