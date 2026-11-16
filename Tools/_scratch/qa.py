"""Render a section of the sheet with slice rectangles drawn on top, for visual QA."""
import sys
import json
import numpy as np
from PIL import Image, ImageDraw

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
OUT = r"D:\Unity\Super Mario Bros\Tools\out"

name = sys.argv[1]
scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
man = json.load(open(OUT + r"\manifest.json"))
items = man[name]

orig = np.array(Image.open(SRC).convert("RGBA"))
bg = Image.new("RGBA", (orig.shape[1], orig.shape[0]), (255, 255, 255, 255))
comp = Image.alpha_composite(bg, Image.fromarray(orig)).convert("RGB")
d = ImageDraw.Draw(comp)
for i, it in enumerate(items, 1):
    d.rectangle([it["x"], it["y"], it["x"] + it["w"] - 1, it["y"] + it["h"] - 1], outline=(255, 0, 0))

x0 = min(it["x"] for it in items)
y0 = min(it["y"] for it in items)
x1 = max(it["x"] + it["w"] for it in items)
y1 = max(it["y"] + it["h"] for it in items)
pad = 8
box = (max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad)
crop = comp.crop(box)
crop = crop.resize((crop.width * scale, crop.height * scale), Image.NEAREST)
crop.save(r"D:\Unity\Super Mario Bros\Tools\qa_%s.png" % name)
print(name, "sprites", len(items), "->", crop.size)
