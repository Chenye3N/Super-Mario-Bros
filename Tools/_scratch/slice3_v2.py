"""Slice v3 = XY-cut, then split each cut by connected components (1px tolerance) when it
still holds several substantial objects (catches overlapping scenery drawings)."""
import json
import os
import sys
import numpy as np
from PIL import Image
import cc
from slice import SECTIONS, content_mask, SRC, runs

OUT3 = r"D:\Unity\Super Mario Bros\Tools\out3"


def xycut(mask, ox, oy, out):
    if not mask.any():
        return
    bands = runs(mask.any(axis=1))
    if len(bands) > 1:
        for (r0, r1) in bands:
            xycut(mask[r0:r1], ox, oy + r0, out)
        return
    cols = runs(mask.any(axis=0))
    if len(cols) > 1:
        for (c0, c1) in cols:
            xycut(mask[:, c0:c1], ox + c0, oy, out)
        return
    ys, xs = np.nonzero(mask)
    out.append((ox + int(xs.min()), oy + int(ys.min()), ox + int(xs.max()) + 1, oy + int(ys.max()) + 1))


def dilate1(m):
    out = m.copy()
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def refine(cm, rect):
    """Split a cut that still holds several separate objects.

    Objects are grouped when their bboxes overlap, so a sprite drawn as a white body
    inside a 1px outline (e.g. the Bloopers) is not torn into two sprites.  Parts too
    small to be objects of their own are attached to the nearest object, never dropped.
    """
    x0, y0, x1, y1 = rect
    m = cm[y0:y1, x0:x1]
    total = int(m.sum())
    labs, n = cc.label(m)
    bb = cc.bboxes(labs, n)
    comps = []
    for i in range(1, n + 1):
        b = bb[i]
        if b is None:
            continue
        mm = m[b["y0"]:b["y1"], b["x0"]:b["x1"]]
        ys, xs = np.nonzero(mm)
        comps.append([x0 + b["x0"] + int(xs.min()), y0 + b["y0"] + int(ys.min()),
                      x0 + b["x0"] + int(xs.max()) + 1, y0 + b["y0"] + int(ys.max()) + 1,
                      int(mm.sum())])
    # union components whose bboxes intersect: one sprite may be drawn as several
    # touching colour regions (e.g. a white body inside a 1px outline)
    groups = []
    while comps:
        cur = comps.pop()
        merged = True
        while merged:
            merged = False
            for j, o in enumerate(comps):
                if not (cur[2] <= o[0] or o[2] <= cur[0] or cur[3] <= o[1] or o[3] <= cur[1]):
                    cur = [min(cur[0], o[0]), min(cur[1], o[1]), max(cur[2], o[2]),
                           max(cur[3], o[3]), cur[4] + o[4]]
                    comps.pop(j)
                    merged = True
                    break
        groups.append(cur)
    if len(groups) < 2:
        return [rect]
    groups.sort(key=lambda g: -g[4])
    big = [g for g in groups if g[4] >= 0.02 * total and g[2] - g[0] >= 8 and g[3] - g[1] >= 8]
    if len(big) < 2:
        return [rect]
    for g in groups:
        if g in big:
            continue
        cx, cy = (g[0] + g[2]) / 2.0, (g[1] + g[3]) / 2.0
        t = min(big, key=lambda b: abs((b[0] + b[2]) / 2.0 - cx) + abs((b[1] + b[3]) / 2.0 - cy))
        t[0], t[1] = min(t[0], g[0]), min(t[1], g[1])
        t[2], t[3] = max(t[2], g[2]), max(t[3], g[3])
    return [tuple(g[:4]) for g in big]


def reading_order(rects):
    if not rects:
        return rects
    hs = sorted(r[3] - r[1] for r in rects)
    t = max(6, 0.5 * hs[len(hs) // 2])
    rects = sorted(rects, key=lambda r: (r[1], r[0]))
    out, band, by = [], [], None
    for r in rects:
        if by is None or r[1] - by <= t:
            band.append(r)
            by = r[1] if by is None else by
        else:
            out.extend(sorted(band, key=lambda r: r[0]))
            band = [r]
            by = r[1]
    out.extend(sorted(band, key=lambda r: r[0]))
    return out


def main():
    a = np.array(Image.open(SRC).convert("RGBA"))
    cm = content_mask(a)
    os.makedirs(OUT3, exist_ok=True)
    manifest = {}
    total = 0
    for sec in SECTIONS:
        name = sec["name"]
        x0, y0, x1, y1 = sec["x0"], sec["y0"], sec["x1"], sec["y1"]
        sub = cm[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
        rects = []
        xycut(sub, x0 + 1, y0 + 1, rects)
        refined = []
        for r in rects:
            refined.extend(refine(cm, r))
        refined = reading_order(refined)
        d = os.path.join(OUT3, name)
        os.makedirs(d, exist_ok=True)
        info = []
        covered = np.zeros(sub.shape, dtype=bool)
        for i, (rx0, ry0, rx1, ry1) in enumerate(refined, 1):
            w, h = rx1 - rx0, ry1 - ry0
            covered[ry0 - y0 - 1:ry1 - y0 - 1, rx0 - x0 - 1:rx1 - x0 - 1] = True
            if max(w, h) <= 4:
                continue
            crop = a[ry0:ry1, rx0:rx1].copy()
            fn = "%s_%02d.png" % (name, i)
            Image.fromarray(crop).save(os.path.join(d, fn))
            info.append(dict(file=fn, x=rx0, y=ry0, w=w, h=h))
        lost = int((sub & ~covered).sum())
        manifest[name] = info
        total += len(info)
        print("%-18s %3d  lost=%d" % (name, len(info), lost))
    json.dump(manifest, open(os.path.join(OUT3, "manifest.json"), "w"), indent=1)
    print("TOTAL", total)


if __name__ == "__main__":
    main()
