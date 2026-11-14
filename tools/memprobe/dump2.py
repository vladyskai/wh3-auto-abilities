r"""READ-ONLY: print fields of [[obj+8]+A] from offset lo to hi, side by side for several units.
usage: dump2.py <A hex> <lo hex> <hi hex> <obj> ..."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
A, lo, hi = (int(x, 16) for x in sys.argv[1:4])
objs = [int(a, 16) for a in sys.argv[4:]]
blk = []
for o in objs:
    q = p.u64(p.u64(o + 8) + A)
    blk.append(p.read(q + lo, hi - lo))
for off in range(0, hi - lo, 4):
    iv = [struct.unpack_from("<i", b, off)[0] for b in blk]
    fv = [struct.unpack_from("<f", b, off)[0] for b in blk]
    if all(v == 0 for v in iv): continue
    if all(0.0001 < abs(f) < 1e6 for f in fv) or all(f == 0 for f in fv):
        print("+%03X f " % (lo + off) + " ".join("%9.2f" % f for f in fv))
    else:
        print("+%03X i " % (lo + off) + " ".join("%9d" % v for v in iv))
