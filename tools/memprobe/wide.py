r"""READ-ONLY wide stat search (2026-11-14). Lesson of round 147: live leadership sits at [unit+8]+0x3B78, past the
0x1000 bytes the earlier searches covered. This reads the engine unit object [handle+8] up to SPAN bytes, and every
block it points to (also up to SPAN), and finds offsets whose int32 or float equals each card value.
  wide.py save <handle> name=value ...   remember every offset matching each value (handle = the unit's addr=)
  wide.py next <handle> name=value ...   keep the offsets that now hold the new value
  wide.py cross <name> <handle> ...      print the kept offsets of <name> read from several units
Offsets are stored as paths: [off] (inside [handle+8]) or [ptr_off, off] (inside [[handle+8]+ptr_off])."""
import os, sys, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m

SPAN = 0x8000
F = lambda n: os.path.join(m.RUNS, "wide_%s.json" % n)


def ok(x):
    return 0x10000 < x < 0x7FFFFFFFFFFF and x % 8 == 0


def blocks(p, handle):
    root = p.u64(handle + 8)
    out = {(): root}
    b = p.read(root, SPAN) or b""
    for o in range(0, len(b) - 7, 8):
        q = struct.unpack_from("<Q", b, o)[0]
        if ok(q):
            out[(o,)] = q
    return out


def value(p, handle, path, kind):
    a = p.u64(handle + 8)
    for o in path[:-1]:
        a = p.u64(a + o) if a else None
    if not a:
        return None
    b = p.read(a + path[-1], 4)
    if not b or len(b) < 4:
        return None
    return struct.unpack("<i" if kind == "i" else "<f", b)[0]


def save(p, handle, targets):
    found = {n: [] for n in targets}
    for prefix, addr in blocks(p, handle).items():
        b = p.read(addr, SPAN)
        if not b:
            continue
        b = b[: len(b) // 4 * 4]
        ints = memoryview(b).cast("i")
        fls = memoryview(b).cast("f")
        for n, v in targets.items():
            for i in range(len(ints)):
                if ints[i] == v:
                    found[n].append([list(prefix) + [i * 4], "i"])
                if fls[i] == v:
                    found[n].append([list(prefix) + [i * 4], "f"])
    for n, f in found.items():
        json.dump(f, open(F(n), "w"))
        print("%s=%g: %d candidate offsets" % (n, targets[n], len(f)))


def nxt(p, handle, targets):
    for n, v in targets.items():
        cands = json.load(open(F(n)))
        keep = [c for c in cands if (lambda r: r is not None and abs(r - v) < 1e-3)(value(p, handle, c[0], c[1]))]
        json.dump(keep, open(F(n), "w"))
        print("%s=%g: %d -> %d" % (n, v, len(cands), len(keep)))


def cross(p, name, handles):
    for path, kind in json.load(open(F(name))):
        vals = [value(p, h, path, kind) for h in handles]
        label = " -> ".join("+%X" % o for o in path) + " (%s)" % kind
        print("%-26s %s" % (label, " ".join("%8s" % ("?" if v is None else ("%.2f" % v if kind == "f" else v))
                                             for v in vals)))


def main():
    p = m.Proc()
    os.makedirs(m.RUNS, exist_ok=True)
    c = sys.argv[1]
    if c == "cross":
        cross(p, sys.argv[2], [int(h, 16) for h in sys.argv[3:]])
        return
    handle = int(sys.argv[2], 16)
    t = {k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])}
    save(p, handle, t) if c == "save" else nxt(p, handle, t)


if __name__ == "__main__":
    main()
