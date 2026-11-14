r"""READ-ONLY: like near.py but two pointers deep: obj -> [+a] -> [+b] -> +off."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
S1, S2, S3 = 0x600, 0x800, 0x1000
tol = float(sys.argv[1])
units = [(int(a, 16), float(v)) for a, v in (x.split("=") for x in sys.argv[2:])]
def ptrs(b, span):
    if b is None: return {}
    return {o: struct.unpack_from("<Q", b, o)[0] for o in range(0, min(span, len(b)) - 7, 8)}
def ok(ptr): return 0x10000 < ptr < 0x7FFFFFFFFFFF
lvl0 = [p.read(a, S1) for a, _ in units]
p0 = [ptrs(b, S1) for b in lvl0]
for a in sorted(p0[0]):
    if not all(ok(pp.get(a, 0)) for pp in p0): continue
    lvl1 = [p.read(pp[a], S2) for pp in p0]
    p1 = [ptrs(b, S2) for b in lvl1]
    for b in sorted(p1[0]):
        if not all(ok(pp.get(b, 0)) for pp in p1): continue
        lvl2 = [p.read(pp[b], S3) for pp in p1]
        if any(x is None or len(x) < S3 for x in lvl2): continue
        for off in range(0, S3 - 4, 4):
            for fmt in ("<i", "<f"):
                vals = [struct.unpack_from(fmt, x, off)[0] for x in lvl2]
                if all(abs(v - t) <= tol * max(t, 1) for v, (_, t) in zip(vals, units)):
                    print("[[+%X]+%X]+%X %s %s" % (a, b, off, fmt, vals))
