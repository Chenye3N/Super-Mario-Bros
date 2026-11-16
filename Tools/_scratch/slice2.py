"""Slice v2: per-section connected components with slight dilation (bridges 1-2px gaps inside a sprite)."""
import json
import os
import numpy as np
from PIL import Image
import cc
from slice import SECTIONS, content_mask, SRC, OUT


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            sh = np.zeros_like(m)
            ys0, ys1 = max(0, dy), m.shape[0] + min(0, dy)
            xs0, xs1 = max(0, dx), m.shape[1] + min(0, dx)
            sh[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            out |= sh
    return out


def main(r=2, outdir=OUT):
    a = np.array(Image.open(SRC).convert("RGBA"))
    cm = content_mask(a)
    os.makedirs(outdir, exist_ok=True)
    manifest = {}
    total = 0
    for sec in SECTIONS:
        name = sec["name"]
        x0, y0, x1, y1 = sec["x0"], sec["y0"], sec["x1"], sec["y1"]
        sub = cm[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
        labs, n = cc.label(dilate(sub, r))
        bb = cc.bboxes(labs, n)
        d = os.path.join(outdir, name)
        os.makedirs(d, exist_ok=True)
        info = []
        for i in range(1, n + 1):
            b = bb[i]
            if b is None:
                continue
            # regenerate tight bbox from undilated content
            rx0, ry0, rx1, ry1 = b["x0"], b["y0"], b["x1"], b["y1"]
            m = cm[y0 + 1 + ry0:y0 + 1 + ry1, x0 + 1 + rx0:x0 + 1 + rx1]
            ys, xs = np.nonzero(m)
            gx0 = x0 + 1 + rx0 + int(xs.min())
            gy0 = y0 + 1 + ry0 + int(ys.min())
            gx1 = x0 + 1 + rx0 + int(xs.max()) + 1
            gy1 = y0 + 1 + ry0 + int(ys.max()) + 1
            w, h = gx1 - gx0, gy1 - gy0
            area = int(m.sum())
            if max(w, h) <= 4 or area < 24:
                continue
            info.append(dict(x=gx0, y=gy0, w=w, h=h, area=area))
        info.sort(key=lambda t: (round(t["y"] / 8), t["x"]))
        for i, it in enumerate(info, 1):
            crop = a[it["y"]:it["y"] + it["h"], it["x"]:it["x"] + it["w"]].copy()
            it["file"] = "%s_%02d.png" % (name, i)
            Image.fromarray(crop).save(os.path.join(d, it["file"]))
        manifest[name] = info
        total += len(info)
        print("%-18s %3d  sizes=%s" % (name, len(info), sorted({(v["w"], v["h"]) for v in info})[:10]))
    json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w"), indent=1)
    print("TOTAL", total)


if __name__ == "__main__":
    import sys
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
