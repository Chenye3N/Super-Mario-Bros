import numpy as np
from PIL import Image

im = Image.open(r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png").convert("RGBA")
a = np.array(im)
al = a[..., 3]
rgb = a[..., :3].astype(np.int32)

# alpha as grayscale, inverted (content = black)
m = Image.fromarray(255 - al).convert("L")
m.save(r"D:\Unity\Super Mario Bros\Tools\alpha_mask.png")

# content classified: white pixels  vs other
white = (al > 0) & (rgb[..., 0] == 255) & (rgb[..., 1] == 255) & (rgb[..., 2] == 255)
vis = np.zeros((*al.shape, 3), np.uint8)
vis[:] = 255
vis[al > 0] = (200, 200, 200)
vis[white] = (255, 0, 0)
Image.fromarray(vis).save(r"D:\Unity\Super Mario Bros\Tools\white_vis.png")
print("white count", white.sum())
