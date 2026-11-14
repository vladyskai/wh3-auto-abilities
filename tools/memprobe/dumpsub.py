r"""READ-ONLY: print int32 fields of [obj+8] side by side for several units."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
objs = [int(a, 16) for a in sys.argv[2:]]
span = int(sys.argv[1], 16)
subs = [p.read(p.u64(a + 8), span) for a in objs]
for off in range(0, span, 4):
    vals = [struct.unpack_from("<i", s, off)[0] for s in subs]
    fl = [struct.unpack_from("<f", s, off)[0] for s in subs]
    if any(v != 0 for v in vals) and all(-1 < v < 10**6 for v in vals):
        print("+%03X " % off + " ".join("%8d" % v for v in vals))
    elif all(0.001 < abs(f) < 1e5 for f in fl):
        print("+%03X " % off + " ".join("%8.2f" % f for f in fl) + "  (float)")
