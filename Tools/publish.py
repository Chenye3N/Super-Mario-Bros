"""Publish the slices into the Unity project and build QA contact sheets."""
import hashlib
import json
import os
import shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = r"D:\Unity\Super Mario Bros"
OUT3 = os.path.join(ROOT, "Tools", "out3")
DEST = os.path.join(ROOT, "Assets", "Sprites")
TOOLS = os.path.join(ROOT, "Tools")
SRC_META = os.path.join(ROOT, "Assets", "Sources", "SuperMarioBors.png.meta")

PPU = 32

lines = open(SRC_META, encoding="utf-8").read().splitlines()


def idx(prefix):
    for i, l in enumerate(lines):
        if l == prefix:
            return i
    raise KeyError(prefix)


body1 = lines[idx("  externalObjects: {}"):idx("  platformSettings:")]
body2 = lines[idx("  platformSettings:"):idx("  spriteSheet:")]
tail = lines[-5:]

body1 = [l.replace("  spriteMode: 2", "  spriteMode: 1")
          .replace("  spritePixelsToUnits: 100", "  spritePixelsToUnits: %d" % PPU)
          .replace("  spriteGenerateFallbackPhysicsShape: 1", "  spriteGenerateFallbackPhysicsShape: 0")
          .replace("    filterMode: 1", "    filterMode: 0") for l in body1]
body2 = [l.replace("    textureCompression: 1", "    textureCompression: 0") for l in body2]


def make_meta(path):
    guid = hashlib.md5(path.encode("utf-8")).hexdigest()
    out = ["fileFormatVersion: 2", "guid: " + guid, "TextureImporter:",
           "  internalIDToNameTable: []"] + body1 + body2 + tail
    return "\n".join(out) + "\n"


def contact(section, items, srcdir):
    imgs = [Image.open(os.path.join(srcdir, it["file"])).convert("RGBA") for it in items]
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
    sheet = sheet.resize((W * 2, H * 2), Image.NEAREST)
    os.makedirs(os.path.join(TOOLS, "contact"), exist_ok=True)
    sheet.save(os.path.join(TOOLS, "contact", section + ".png"))


def main():
    man = json.load(open(os.path.join(OUT3, "manifest.json")))
    assert os.path.basename(DEST) == "Sprites" and DEST.startswith(os.path.join(ROOT, "Assets"))
    if os.path.isdir(DEST):
        shutil.rmtree(DEST)
    index = {}
    total = 0
    for section, items in man.items():
        d = os.path.join(DEST, section)
        os.makedirs(d, exist_ok=True)
        for it in items:
            src = os.path.join(OUT3, section, it["file"])
            dst = os.path.join(d, it["file"])
            shutil.copyfile(src, dst)
            rel = "Assets/Sprites/%s/%s" % (section, it["file"])
            open(dst + ".meta", "w", encoding="utf-8", newline="\n").write(make_meta(rel))
            it["asset"] = rel
        contact(section, items, d)
        index[section] = items
        total += len(items)
    json.dump(index, open(os.path.join(TOOLS, "sprites_index.json"), "w"), indent=1)
    print("published", total, "sprites to", DEST)


if __name__ == "__main__":
    main()
