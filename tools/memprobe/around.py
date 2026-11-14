r"""READ-ONLY: show readable text (ASCII and UTF-16) and nearby floats around each rscan candidate."""
import sys, os, re, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
R = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x200
for x in [int(a) for a in np.load(os.path.join(m.RUNS, "rscan_addr.npy"))]:
    b = p.read(x - R, 2 * R) or b""
    asc = set(s.decode() for s in re.findall(rb"[ -~]{6,}", b))
    u16 = set(s.decode("utf-16le") for s in re.findall(rb"(?:[ -~]\x00){5,}", b))
    fl = [struct.unpack_from("<f", b, R + d)[0] for d in range(-16, 20, 4)]
    print("0x%X  floats %s" % (x, " ".join("%.2f" % f if abs(f) < 1e6 else "~" for f in fl)))
    if asc or u16: print("      text:", sorted(asc | u16)[:6])
