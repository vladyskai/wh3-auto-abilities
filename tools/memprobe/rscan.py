r"""READ-ONLY whole-memory float scans (Cheat Engine style, with ranges), 2026-11-14.
  rscan.py first <lo> <hi>          every 4-byte-aligned float in [lo, hi] in all writable memory
  rscan.py range <lo> <hi>          keep candidates whose value is now in [lo, hi]
  rscan.py down | up | same         keep candidates that decreased / increased / did not change
  rscan.py show [n]                 print up to n candidates (address, previous value, current value)
Candidates live in runs/rscan_addr.npy and runs/rscan_val.npy."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m

FA = os.path.join(m.RUNS, "rscan_addr.npy")
FV = os.path.join(m.RUNS, "rscan_val.npy")
CHUNK = 64 * 2**20


def first(p, lo, hi):
    addrs, vals = [], []
    for base, size in p.regions():
        off = 0
        while off < size:
            n = min(CHUNK, size - off)
            b = p.read(base + off, n)
            if b:
                f = np.frombuffer(b[: len(b) // 4 * 4], dtype="<f4")
                idx = np.nonzero((f >= lo) & (f <= hi))[0]
                if idx.size:
                    addrs.append(np.uint64(base + off) + idx.astype(np.uint64) * np.uint64(4))
                    vals.append(f[idx].copy())
            off += n
    a = np.concatenate(addrs) if addrs else np.array([], np.uint64)
    v = np.concatenate(vals) if vals else np.array([], np.float32)
    np.save(FA, a); np.save(FV, v)
    print("first scan [%g, %g]: %d candidates" % (lo, hi, a.size))


def reread(p, a):
    """current float at every candidate address, region by region (NaN when unreadable)"""
    cur = np.full(a.size, np.nan, np.float32)
    for base, size in p.regions():
        lo_i = np.searchsorted(a, np.uint64(base))
        hi_i = np.searchsorted(a, np.uint64(base + size))
        if hi_i <= lo_i:
            continue
        off = 0
        while off < size:
            n = min(CHUNK, size - off)
            s = np.searchsorted(a, np.uint64(base + off))
            e = np.searchsorted(a, np.uint64(base + off + n))
            if e > s:
                b = p.read(base + off, n)
                if b:
                    f = np.frombuffer(b[: len(b) // 4 * 4], dtype="<f4")
                    rel = ((a[s:e] - np.uint64(base + off)) // np.uint64(4)).astype(np.int64)
                    good = rel < f.size
                    cur[s:e][good] = f[rel[good]]
            off += n
    return cur


def filt(p, mode, lo=None, hi=None):
    a, v = np.load(FA), np.load(FV)
    order = np.argsort(a); a, v = a[order], v[order]
    cur = reread(p, a)
    ok = ~np.isnan(cur)
    if mode == "range": keep = ok & (cur >= lo) & (cur <= hi)
    elif mode == "down": keep = ok & (cur < v)
    elif mode == "up": keep = ok & (cur > v)
    else: keep = ok & (cur == v)
    np.save(FA, a[keep]); np.save(FV, cur[keep])
    print("%s: %d -> %d candidates" % (mode, a.size, int(keep.sum())))


def show(p, n):
    a, v = np.load(FA), np.load(FV)
    cur = reread(p, a) if a.size < 5_000_000 else v
    for i in range(min(n, a.size)):
        print("0x%X  saved %.4f  now %.4f" % (int(a[i]), v[i], cur[i]))


def main():
    p = m.Proc()
    os.makedirs(m.RUNS, exist_ok=True)
    c = sys.argv[1]
    if c == "first": first(p, float(sys.argv[2]), float(sys.argv[3]))
    elif c == "range": filt(p, "range", float(sys.argv[2]), float(sys.argv[3]))
    elif c in ("down", "up", "same"): filt(p, c)
    elif c == "show": show(p, int(sys.argv[2]) if len(sys.argv) > 2 else 30)


if __name__ == "__main__":
    main()
