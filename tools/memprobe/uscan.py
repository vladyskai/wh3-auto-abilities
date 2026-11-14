r"""READ-ONLY unknown-value scan (Cheat Engine 'unknown initial value') over the memory blocks reachable
from one unit handle (up to <depth> pointers, 0x1000 bytes per block), 2026-11-14.
  uscan.py first <obj> <depth>     snapshot every 4-byte slot of every reachable block
  uscan.py changed | same          keep slots whose float changed / did not change since the last step
  uscan.py down | up               keep slots whose float went down / up
  uscan.py show [n]                print survivors with their path from the handle and their value history
Survivors keep their full value history (runs/uscan_hist.npy) so the shape can be compared with the card."""
import os, sys, json, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m

NODE, PTRS = 0x1000, 0x800
F_BLK = os.path.join(m.RUNS, "uscan_blocks.json")   # [[addr, path], ...]
F_SEL = os.path.join(m.RUNS, "uscan_sel.npy")       # (block index, slot) survivors
F_HIST = os.path.join(m.RUNS, "uscan_hist.npy")     # float history per survivor


def ok(x):
    return 0x10000 < x < 0x7FFFFFFFFFFF and x % 8 == 0


def read_all(p, blocks):
    out = np.full((len(blocks), NODE // 4), np.nan, np.float32)
    for i, (a, _) in enumerate(blocks):
        b = p.read(a, NODE)
        if b and len(b) == NODE:
            out[i] = np.frombuffer(b, dtype="<f4")
    return out


def first(p, obj, depth):
    seen, blocks, frontier = {obj}, [], [(obj, [])]
    for level in range(depth + 1):
        nxt = []
        for a, path in frontier:
            blocks.append([a, path])
            if level == depth:
                continue
            b = p.read(a, PTRS) or b""
            for off in range(0, len(b) - 7, 8):
                q = struct.unpack_from("<Q", b, off)[0]
                if ok(q) and q not in seen:
                    seen.add(q); nxt.append((q, path + [off]))
        frontier = nxt
    json.dump(blocks, open(F_BLK, "w"))
    snap = read_all(p, blocks)
    bi, sl = np.nonzero(~np.isnan(snap))
    np.save(F_SEL, np.stack([bi, sl], 1).astype(np.int32))
    np.save(F_HIST, snap[bi, sl][:, None])
    print("%d blocks, %d slots snapshotted" % (len(blocks), bi.size))


def step(p, mode):
    blocks = json.load(open(F_BLK))
    sel, hist = np.load(F_SEL), np.load(F_HIST)
    cur = read_all(p, blocks)[sel[:, 0], sel[:, 1]]
    prev = hist[:, -1]
    good = ~np.isnan(cur)
    if mode == "changed": keep = good & (cur != prev)
    elif mode == "same": keep = good & (cur == prev)
    elif mode == "down": keep = good & (cur < prev)
    elif mode == "record": keep = good
    else: keep = good & (cur > prev)
    np.save(F_SEL, sel[keep])
    np.save(F_HIST, np.concatenate([hist, cur[:, None]], 1)[keep])
    print("%s: %d -> %d" % (mode, sel.shape[0], int(keep.sum())))


def show(n):
    blocks = json.load(open(F_BLK))
    sel, hist = np.load(F_SEL), np.load(F_HIST)
    for k in range(min(n, sel.shape[0])):
        a, path = blocks[sel[k, 0]]
        route = " -> ".join("+%X" % o for o in path + [int(sel[k, 1]) * 4])
        print("%-36s %s" % (route, " ".join("%.4g" % v for v in hist[k])))


def main():
    p = m.Proc()
    os.makedirs(m.RUNS, exist_ok=True)
    c = sys.argv[1]
    if c == "first": first(p, int(sys.argv[2], 16), int(sys.argv[3]))
    elif c in ("changed", "same", "down", "up", "record"): step(p, c)
    elif c == "show": show(int(sys.argv[2]) if len(sys.argv) > 2 else 40)


if __name__ == "__main__":
    main()
