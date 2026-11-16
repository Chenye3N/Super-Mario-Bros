from PIL import Image
import numpy as np

SRC = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
im = Image.open(SRC).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
comp = Image.alpha_composite(bg, im).convert("RGB")

def crop(x0, y0, x1, y1, s, name):
    c = comp.crop((x0, y0, x1, y1)).resize(((x1 - x0) * s, (y1 - y0) * s), Image.NEAREST)
    c.save(r"D:\Unity\Super Mario Bros\Tools\%s.png" % name)
    print(name, x1 - x0, y1 - y0)

crop(600, 255, 780, 300, 5, "q_a")
crop(340, 495, 520, 545, 5, "q_b")
crop(330, 785, 480, 830, 5, "q_c")
