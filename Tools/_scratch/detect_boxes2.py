import json
import numpy as np
from PIL import Image
import cc

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
a = np.array(Image.open(SRC).convert("RGBA"))
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
labs, n = cc.label(white)
bb = cc.bboxes(labs, n)
print("white comps", n)

rings = []
texts = []
for i in range(1, n + 1):
    b = bb[i]
    if b is None:
        continue
    w, h = b["x1"] - b["x0"], b["y1"] - b["y0"]
    span = max(w, h)
    # ring: large span, low fill
    fill = b["area"] / (w * h)
    if span > 40 and fill < 0.35:
        rings.append(b)
    elif h <= 10 and w <= 120:
        texts.append(b)

rings.sort(key=lambda b: (b["y0"], b["x0"]))
print("rings", len(rings))
for b in rings:
    print("  x %4d..%4d  y %4d..%4d  %dx%d fill=%.2f" % (b["x0"], b["x1"], b["y0"], b["y1"],
                                                          b["x1"] - b["x0"], b["y1"] - b["y0"],
                                                          b["area"] / ((b["x1"] - b["x0"]) * (b["y1"] - b["y0"]))))
print("texts", len(texts))
json.dump({"rings": rings, "texts": texts}, open(r"D:\Unity\Super Mario Bros\Tools\guides.json", "w"), indent=1)
