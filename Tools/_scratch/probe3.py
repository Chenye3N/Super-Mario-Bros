import numpy as np
from PIL import Image
from collections import Counter

a = np.array(Image.open(r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png").convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]

# print colors along vertical slice x=100 (should cross top border of first boxes)
for y in range(0, 40):
    px = tuple(a[y, 100])
    print(y, px)
print("---- x scan at y=18")
row = a[18]
prev = None
for x in range(0, 1188):
    c = tuple(row[x])
    if c != prev:
        print(x, c)
        prev = c
