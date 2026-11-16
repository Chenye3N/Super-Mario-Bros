"""Draw every slice rect on the whole sheet (1x) for a global sanity check."""
import json
from PIL import Image, ImageDraw

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
OUT3 = r"D:\Unity\Super Mario Bros\Tools\out3"

a = Image.open(SRC).convert("RGBA")
bg = Image.new("RGBA", a.size, (255, 255, 255, 255))
comp = Image.alpha_composite(bg, a).convert("RGB")
d = ImageDraw.Draw(comp)
man = json.load(open(OUT3 + r"\manifest.json"))
for name, items in man.items():
    for it in items:
        d.rectangle([it["x"], it["y"], it["x"] + it["w"] - 1, it["y"] + it["h"] - 1], outline=(255, 0, 0))
comp.save(OUT3 + r"\..\overlay_all.png")
print(sum(len(v) for v in man.values()), "rects")
