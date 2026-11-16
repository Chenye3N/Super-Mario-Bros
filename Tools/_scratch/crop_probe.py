from PIL import Image
im = Image.open(r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png").convert("RGBA")
white = Image.new("RGBA", im.size, (255, 255, 255, 255))
comp = Image.alpha_composite(white, im).convert("RGB")
crops = {
    "c1_top_left": (0, 0, 360, 300),
    "c2_mario": (0, 900, 360, 1300),
    "c3_guide_edge": (280, 1180, 560, 1330),
}
for name, box in crops.items():
    c = comp.crop(box)
    c = c.resize((c.width * 3, c.height * 3), Image.NEAREST)
    c.save(rf"D:\Unity\Super Mario Bros\Tools\{name}.png")
    print(name, box, c.size)
