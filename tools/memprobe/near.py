r"""READ-ONLY: find offsets (in the unit object, or one pointer deep) whose int32 or
float is within a tolerance of a target for EVERY unit. args: tol addr=target ..."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
SPAN = 0x2000
tol = float(sys.argv[1])
units = [(int(a, 16), float(v)) for a, v in (x.split("=") for x in sys.argv[2:])]
def match(blobs, off):
    oki = okf = True
    for b, (_, v) in zip(blobs, units):
        if b is None or len(b) < off + 4: return None
        i = struct.unpack_from("<i", b, off)[0]; f = struct.unpack_from("<f", b, off)[0]
        oki = oki and abs(i - v) <= tol * max(v, 1)
        okf = okf and abs(f - v) <= tol * max(v, 1)
    return "int" if oki else ("float" if okf else None)
blobs = [p.read(a, SPAN) for a, _ in units]
for off in range(0, SPAN - 4, 4):
    k = match(blobs, off)
    if k: print("direct +%X %s %s" % (off, k, [struct.unpack_from("<i" if k == "int" else "<f", b, off)[0] for b in blobs]))
for poff in range(0, SPAN - 8, 8):
    subs = []
    for b in blobs:
        ptr = struct.unpack_from("<Q", b, poff)[0]
        subs.append(p.read(ptr, SPAN) if 0x10000 < ptr < 0x7FFFFFFFFFFF else None)
    for off in range(0, SPAN - 4, 4):
        k = match(subs, off)
        if k: print("[+%X] +%X %s %s" % (poff, off, k, [struct.unpack_from("<i" if k == "int" else "<f", s, off)[0] for s in subs]))
