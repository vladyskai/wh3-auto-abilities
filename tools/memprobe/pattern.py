r"""READ-ONLY: in one unit object, up to two pointers deep, find blocks where
value v_i sits at offset base + d_i (float or int). args: obj  d:v  d:v ...  (d hex)"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
obj = int(sys.argv[1], 16)
pat = [(int(d, 16), float(v)) for d, v in (x.split(":") for x in sys.argv[2:])]
span = max(d for d, _ in pat) + 4
def ok(x): return 0x10000 < x < 0x7FFFFFFFFFFF
def scan(addr, label, size=0x1000):
    b = p.read(addr, size + span)
    if not b: return
    for base in range(0, size, 4):
        for fmt in ("<f", "<i"):
            if all(len(b) >= base + d + 4 and abs(struct.unpack_from(fmt, b, base + d)[0] - v) < 1e-4 for d, v in pat):
                print("%s+%X %s" % (label, base, fmt))
scan(obj, "obj")
b0 = p.read(obj, 0x600) or b""
for a in range(0, len(b0) - 7, 8):
    q = struct.unpack_from("<Q", b0, a)[0]
    if not ok(q): continue
    scan(q, "[+%X]" % a)
    b1 = p.read(q, 0x800) or b""
    for c in range(0, len(b1) - 7, 8):
        r = struct.unpack_from("<Q", b1, c)[0]
        if ok(r): scan(r, "[[+%X]+%X]" % (a, c))
