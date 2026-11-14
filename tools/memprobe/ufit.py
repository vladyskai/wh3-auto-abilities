r"""READ-ONLY analysis of uscan histories: keep slots whose history is a straight-line function of the
card's history (any scale, any sign). args: the card values, one per history column."""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
card = np.array([float(x) for x in sys.argv[1:]])
blocks = json.load(open(os.path.join(m.RUNS, "uscan_blocks.json")))
sel, h = np.load(os.path.join(m.RUNS, "uscan_sel.npy")), np.load(os.path.join(m.RUNS, "uscan_hist.npy")).astype(np.float64)
assert h.shape[1] == card.size, (h.shape, card.size)
fin = np.all(np.isfinite(h), 1) & np.all(np.abs(h) < 1e9, 1)
h, sel = h[fin], sel[fin]
c = card - card.mean()
x = h - h.mean(1, keepdims=True)
sx = np.sqrt((x * x).sum(1)); sc = np.sqrt((c * c).sum())
r = np.where(sx > 0, (x @ c) / (sx * sc + 1e-30), 0)
order = np.argsort(-np.abs(r))
print("slots analysed: %d;  |r| > 0.99: %d,  > 0.97: %d" % (len(r), int((np.abs(r) > 0.99).sum()), int((np.abs(r) > 0.97).sum())))
for k in order[:25]:
    a, path = blocks[sel[k, 0]]
    route = " -> ".join("+%X" % o for o in path + [int(sel[k, 1]) * 4])
    print("r=%+.4f  %-34s %s" % (r[k], route, " ".join("%.4g" % v for v in h[k])))
