r"""READ-ONLY: list every block within <depth> pointers of each unit handle whose int32 at +0x3B78 is plausible,
side by side for several units (lead from a public Cheat Engine table: 'signed current leadership', +0x3B78)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
OFF = 0x3B78
objs = [int(a, 16) for a in sys.argv[1:]]
def ok(x): return 0x10000 < x < 0x7FFFFFFFFFFF and x % 8 == 0
def paths(obj, depth=2):
    out, frontier = [([], obj)], [([], obj)]
    for _ in range(depth):
        nxt = []
        for path, a in frontier:
            b = p.read(a, 0x800) or b""
            for o in range(0, len(b) - 7, 8):
                q = struct.unpack_from("<Q", b, o)[0]
                if ok(q): nxt.append((path + [o], q))
        out += nxt; frontier = nxt
    return out
first = paths(objs[0])
for path, a in first:
    vals = []
    for o in objs:
        x = o
        for step in path:
            x = p.u64(x + step) if x is not None else None
        vals.append(p.i32(x + OFF) if x is not None else None)
    if vals[0] is not None and 1 <= vals[0] <= 200 and all(v is not None and -200 <= v <= 300 for v in vals):
        print("%-22s +3B78 -> %s" % (" -> ".join("+%X" % s for s in path) or "handle", vals))
