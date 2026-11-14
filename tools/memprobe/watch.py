r"""READ-ONLY watcher (round 147 experiment). Takes unit addresses from the mod's MAP
rows (addr=battle.unit_(...)) in the battle log, then once per second records, for each
unit, the engine fields found on 2026-11-14 one pointer behind the handle ([obj+8]):
  [+280]+5CC current hit points (two pointers deep)
  +80 / +84  MAXIMUM hit points (never moved in a fight)   +A4  men alive   +A0  capacity?
  +208/+210  position x / z                     +228 ordered width
Writes tools/memprobe/runs/watch.tsv. Stop with Ctrl+C or after --seconds.

usage: uv run --with numpy python tools/memprobe/watch.py <log byte offset> [seconds]
"""
import os, re, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m

LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\zz_test_deadly_onslaught_log.txt"
ROW = re.compile(rb"MAP t=\S+ side=(\S) id=(\d+) type=(\S+) .* addr=battle\.unit_\(([0-9A-F]+)\)")


def units_from_log(offset):
    found = {}
    with open(LOG, "rb") as f:
        f.seek(offset)
        for line in f:
            mm = ROW.search(line)
            if mm:
                side, uid, typ, addr = mm.groups()
                found[uid.decode()] = (side.decode(), typ.decode(), int(addr, 16))
    return found


def main():
    offset = int(sys.argv[1])
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    p = m.Proc()
    units = units_from_log(offset)
    print("%d units from the log" % len(units))
    os.makedirs(m.RUNS, exist_ok=True)
    out = open(os.path.join(m.RUNS, "watch.tsv"), "w")
    out.write("t\tid\tside\ttype\thp_now\thp_max\tmen\tcap\tx\tz\twidth\n")
    t0 = time.time()
    while time.time() - t0 < seconds:
        t = time.time() - t0
        for uid, (side, typ, obj) in sorted(units.items()):
            sub = p.u64(obj + 8)
            b = p.read(sub, 0x230) if sub else None
            if not b or len(b) < 0x230:
                out.write("%.1f\t%s\t%s\t%s\t?\t?\t?\t?\t?\t?\t?\n" % (t, uid, side, typ))
                continue
            i = lambda o: struct.unpack_from("<i", b, o)[0]
            f = lambda o: struct.unpack_from("<f", b, o)[0]
            hp_obj = p.u64(sub + 0x280)
            hp_now = p.i32(hp_obj + 0x5CC) if hp_obj else None
            out.write("%.1f\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%.1f\t%.1f\t%.1f\n"
                      % (t, uid, side, typ, "?" if hp_now is None else hp_now, i(0x80), i(0xA4), i(0xA0),
                         f(0x208), f(0x210), f(0x228)))
        out.flush()
        time.sleep(1)
    out.close()


if __name__ == "__main__":
    main()
