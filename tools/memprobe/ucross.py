r"""READ-ONLY: take the uscan survivors that fit the card perfectly (|r| > 0.999) and resolve each one's path
from another unit handle. A real per-unit field resolves there too, to a sensible value."""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
from bfs import resolve
p = m.Proc()
other = int(sys.argv[1], 16)
card = np.array([float(x) for x in sys.argv[2:]])
blocks = json.load(open(os.path.join(m.RUNS, "uscan_blocks.json")))
sel, h = np.load(os.path.join(m.RUNS, "uscan_sel.npy")), np.load(os.path.join(m.RUNS, "uscan_hist.npy")).astype(np.float64)
fin = np.all(np.isfinite(h), 1) & np.all(np.abs(h) < 1e9, 1)
h, sel = h[fin], sel[fin]
c = card - card.mean(); x = h - h.mean(1, keepdims=True)
sx = np.sqrt((x * x).sum(1)); r = np.where(sx > 0, (x @ c) / (sx * np.sqrt((c * c).sum()) + 1e-30), 0)
n_ok = 0
for k in np.nonzero(np.abs(r) > float(os.environ.get("UCUT", "0.999")))[0]:
    path = blocks[sel[k, 0]][1] + [int(sel[k, 1]) * 4]
    v = resolve(p, other, path)
    if v is not None and abs(v) < 1e6:
        n_ok += 1
        print("%-34s ours now %.4g   other unit: %.4g" % (" -> ".join("+%X" % o for o in path), h[k, -1], v))
print("perfect fits: %d; resolving on the other unit: %d" % (int((np.abs(r) > float(os.environ.get("UCUT", "0.999"))).sum()), n_ok))
