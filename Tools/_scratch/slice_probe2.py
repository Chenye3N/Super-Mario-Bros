import numpy as np
from PIL import Image
from collections import Counter

p = r"D:\Unity\Super Mario Bros\Assets\Sources\SuperMarioBors.png"
a = np.array(Image.open(p).convert("RGBA"))
rgb = a[..., :3].astype(int)
al = a[..., 3]
mag = (rgb[..., 0] == 255) & (rgb[..., 1] == 0) & (rgb[..., 2] == 255)
print("magenta px", mag.sum(), "alpha uniq on magenta", np.unique(al[mag])[:10])
print("alpha==0 count", (al == 0).sum(), "total", al.size)
print("alpha uniq overall", np.unique(al))
# is every alpha0 pixel magenta?
print("alpha0 & not magenta", ((al == 0) & ~mag).sum())
print("magenta & alpha>0", ((mag) & (al > 0)).sum())
