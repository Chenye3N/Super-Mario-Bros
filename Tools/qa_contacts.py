"""Build per-section contact sheets straight from Tools\\out3 (no writing into Assets)."""
import json
import os
import sys
from PIL import Image, ImageDraw

TOOLS = r"D:\Unity\Super Mario Bros\Tools"
OUT3 = os.path.join(TOOLS, "out3")


def contact(section, items, outdir):
    imgs = [Image.open(os.path.join(OUT3, section, it["file"])).convert("RGBA") for it in items]
    cell_w = max(i.width for i in imgs) + 12
    cell_h = max(i.height for i in imgs) + 18
    cols = max(1, min(8, int(1000 / cell_w) or 1))
    rows = (len(imgs) + cols - 1) // cols
    W, H = cols * cell_w, rows * cell_h
    sheet = Image.new("RGB", (W, H), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(imgs):
        r, c = divmod(k, cols)
        cx = c * cell_w + (cell_w - im.width) // 2
        cy = r * cell_h + 14 + (cell_h - 18 - im.height) // 2
        sheet.paste(im, (cx, cy), im)
        d.text((c * cell_w + 3, r * cell_h + 2), "%d" % (k + 1), fill=(200, 0, 0))
        d.rectangle([c * cell_w, r * cell_h, c * cell_w + cell_w - 1, r * cell_h + cell_h - 1],
                    outline=(220, 220, 220))
    outdir = os.path.join(TOOLS, "contact")
    os.makedirs(outdir, exist_ok=True)
    sheet.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(outdir, section + ".png"))


if __name__ == "__main__":
    man = json.load(open(os.path.join(OUT3, "manifest.json")))
    for s, items in man.items():
        contact(s, items, None)
    print("contact sheets:", len(man))
