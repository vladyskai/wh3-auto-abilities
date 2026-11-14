r"""READ-ONLY: current leadership ([handle+8]+0x3B78, int32) for units from the log, next to the card's UI copy."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
ui = int(sys.argv[1], 16)
for h in sys.argv[2:]:
    u = p.u64(int(h, 16) + 8)
    print("%s leadership %s  men %s" % (h, p.i32(u + 0x3B78), p.i32(u + 0xA4)))
b = p.read(ui, 4)
print("card (UI copy):", struct.unpack("<f", b)[0] if b else "?")
