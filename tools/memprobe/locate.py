r"""READ-ONLY: for each rscan candidate, show its distance to the known blocks of a unit handle,
and every pointer from the unit's depth<=2 blocks that lands within 0x2000 bytes before it."""
import sys, os, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
obj = int(sys.argv[1], 16)
cands = [int(a) for a in np.load(os.path.join(m.RUNS, "rscan_addr.npy"))]
def ok(x): return 0x10000 < x < 0x7FFFFFFFFFFF
blocks = {"obj": obj}
b0 = p.read(obj, 0x800) or b""
for a in range(0, len(b0) - 7, 8):
    q = struct.unpack_from("<Q", b0, a)[0]
    if not ok(q): continue
    blocks["[+%X]" % a] = q
    b1 = p.read(q, 0x800) or b""
    for c in range(0, len(b1) - 7, 8):
        r = struct.unpack_from("<Q", b1, c)[0]
        if ok(r): blocks["[[+%X]+%X]" % (a, c)] = r
for x in cands:
    near = sorted(((x - v, k) for k, v in blocks.items() if 0 <= x - v < 0x2000))
    v = struct.unpack("<f", p.read(x, 4))[0]
    print("0x%X = %.2f  %s" % (x, v, ", ".join("%s+%X" % (k, d) for d, k in near[:3]) or "-"))
