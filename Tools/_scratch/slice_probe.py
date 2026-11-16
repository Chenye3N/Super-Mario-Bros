import numpy as np
from PIL import Image
from collections import Counter

p = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
im = Image.open(p)
print("mode", im.mode, "size", im.size)
a = np.array(im.convert("RGBA"))
print("alpha min/max", a[..., 3].min(), a[..., 3].max())
rgb = a[..., :3]
# most common colors
flat = rgb.reshape(-1, 3)
key = (flat[:, 0].astype(np.int64) << 16) | (flat[:, 1].astype(np.int64) << 8) | flat[:, 2]
cnt = Counter(key.tolist())
for k, v in cnt.most_common(12):
    print("color", (k >> 16) & 255, (k >> 8) & 255, k & 255, v)
# pinkish pixels
r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
pink = (r > 200) & (g > 120) & (g < 210) & (b > 170) & (b < 240) & (r - g > 40)
print("pink count", pink.sum())
ys, xs = np.nonzero(pink)
print("pink bbox", xs.min(), ys.min(), xs.max(), ys.max())
# unique pink colors
pk = key[pink.reshape(-1)]
c2 = Counter(pk.tolist())
print(c2.most_common(5))
