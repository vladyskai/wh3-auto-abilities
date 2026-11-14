r"""READ-ONLY: look at a unit object found through the mod's addr= field."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
a = int(sys.argv[1], 16)
print("module 0x%X" % p.base)
for off in range(0, 0x80, 8):
    v = p.u64(a + off)
    tag = ""
    if v is not None and p.base <= v < p.base + p.size: tag = " -> module+0x%X" % (v - p.base)
    print("+%03X  %s%s" % (off, "?" if v is None else "%016X" % v, tag))
# the Cheat Engine chain ended "... +200 -> +5CC"
for name, addr in (("[a+200]+5CC", (p.u64(a + 0x200) or 0) + 0x5CC), ("a+5CC", a + 0x5CC)):
    print(name, "0x%X" % addr, p.i32(addr))
