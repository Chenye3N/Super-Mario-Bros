import numpy as np
from PIL import Image

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
im = Image.open(SRC).convert("RGBA")
a = np.array(im)
rgb = a[..., :3].astype(np.int32)
al = a[..., 3]
white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
print("white px", int(white.sum()))
# what colours are the frame lines? sample along the top edge of the Power ups frame at y=24
for y in (23, 24, 25):
    row = a[y, 322:340]
    print("y", y, [tuple(int(v) for v in p) for p in row])
bgs = [(255, 255, 255, 255)]
out = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")
c = out.crop((322, 14, 500, 50)).resize((178 * 6, 36 * 6), Image.NEAREST)
c.save(r"D:\Unity\Super Mario Bros\Tools\q_label.png")
