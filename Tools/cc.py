"""Run-based connected-component labelling (8-connectivity) with numpy + union-find."""
import numpy as np


def label(mask):
    """Return (labels int32, n_components); 0 is background."""
    h = mask.shape[0]
    parent = []
    runs_by_row = []
    runs_flat = []
    for y in range(h):
        row = mask[y]
        cur = []
        if row.any():
            d = np.diff(np.r_[0, row.view(np.int8), 0])
            starts = np.flatnonzero(d == 1)
            ends = np.flatnonzero(d == -1)
            for s, e in zip(starts.tolist(), ends.tolist()):
                idx = len(parent)
                parent.append(idx)
                cur.append((s, e, idx))
        runs_by_row.append(cur)
        runs_flat.append((y, cur))

    p = parent

    def find(a):
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    for y in range(1, h):
        prev = runs_by_row[y - 1]
        if not prev:
            continue
        j = 0
        for s, e, idx in runs_by_row[y]:
            while j < len(prev) and prev[j][1] < s:
                j += 1
            k = j
            while k < len(prev) and prev[k][0] <= e:
                ra, rb = find(idx), find(prev[k][2])
                if ra != rb:
                    p[rb] = ra
                k += 1

    labs = np.zeros(mask.shape, np.int32)
    for y, cur in runs_flat:
        for s, e, idx in cur:
            labs[y, s:e] = find(idx) + 1
    ids = np.unique(labs)
    ids = ids[ids > 0]
    if len(ids) == 0:
        return labs, 0
    remap = np.zeros(int(ids.max()) + 1, np.int32)
    remap[ids] = np.arange(1, len(ids) + 1)
    return remap[labs], len(ids)


def bboxes(labs, n):
    """List of dicts x0,y0,x1,y1,area for labels 1..n."""
    ys, xs = np.nonzero(labs)
    lab = labs[ys, xs].astype(np.int64)
    big = 1 << 30
    x0 = np.full(n + 1, big, np.int64)
    y0 = np.full(n + 1, big, np.int64)
    x1 = np.full(n + 1, -big, np.int64)
    y1 = np.full(n + 1, -big, np.int64)
    np.minimum.at(x0, lab, xs)
    np.minimum.at(y0, lab, ys)
    np.maximum.at(x1, lab, xs)
    np.maximum.at(y1, lab, ys)
    area = np.bincount(lab, minlength=n + 1)
    out = [None]
    for i in range(1, n + 1):
        if area[i] == 0:
            out.append(None)
        else:
            out.append(dict(x0=int(x0[i]), y0=int(y0[i]), x1=int(x1[i]) + 1, y1=int(y1[i]) + 1,
                            area=int(area[i])))
    return out
