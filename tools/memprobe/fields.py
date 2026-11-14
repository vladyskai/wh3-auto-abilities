r"""READ-ONLY: find offsets inside the unit objects (and one pointer deep) whose
int32 / float value equals a known per-unit number for EVERY unit."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
SPAN = 0x2000
units = [(int(a, 16), float(v)) for a, v in (x.split("=") for x in sys.argv[1:])]
def ints(a):
    b = p.read(a, SPAN) or b""
    return b
blobs = [ints(a) for a, _ in units]
# direct fields
for off in range(0, SPAN - 4, 4):
    oki = all(len(b) >= off + 4 and struct.unpack_from("<i", b, off)[0] == int(v) for b, (_, v) in zip(blobs, units))
    okf = all(len(b) >= off + 4 and abs(struct.unpack_from("<f", b, off)[0] - v) < 1e-3 for b, (_, v) in zip(blobs, units))
    if oki or okf: print("direct +%X %s" % (off, "int" if oki else "float"))
# one pointer deep
for poff in range(0, SPAN - 8, 8):
    subs = []
    for b in blobs:
        ptr = struct.unpack_from("<Q", b, poff)[0] if len(b) >= poff + 8 else 0
        subs.append(p.read(ptr, SPAN) if 0x10000 < ptr < 0x7FFFFFFFFFFF else None)
    if any(s is None for s in subs): continue
    for off in range(0, SPAN - 4, 4):
        oki = all(len(s) >= off + 4 and struct.unpack_from("<i", s, off)[0] == int(v) for s, (_, v) in zip(subs, units))
        okf = all(len(s) >= off + 4 and abs(struct.unpack_from("<f", s, off)[0] - v) < 1e-3 for s, (_, v) in zip(subs, units))
        if oki or okf: print("[+%X] +%X %s" % (poff, off, "int" if oki else "float"))
