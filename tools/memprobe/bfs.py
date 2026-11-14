r"""READ-ONLY deep candidate search from a unit handle (breadth-first, each memory block visited once).
  bfs.py save <obj> <depth> name=value ...   every float path (up to <depth> pointers) holding value
  bfs.py next <obj> name=value ...           keep the paths of <name> that now read value
Paths are stored in runs/bfs_<name>.json and re-resolved from <obj> on every 'next'."""
import sys, os, json, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m

NODE = 0x1000      # bytes searched for values in each block
PTRS = 0x800       # bytes searched for pointers in each block


def ok(x):
    return 0x10000 < x < 0x7FFFFFFFFFFF and x % 8 == 0


def resolve(p, obj, path):
    a = obj
    for o in path[:-1]:
        a = p.u64(a + o)
        if a is None:
            return None
    b = p.read(a + path[-1], 4)
    return None if not b or len(b) < 4 else struct.unpack("<f", b)[0]


def save(p, obj, depth, targets):
    hits = {n: [] for n in targets}
    seen = {obj}
    frontier = [(obj, [])]
    t0 = time.time()
    for level in range(depth + 1):
        nxt = []
        for addr, path in frontier:
            b = p.read(addr, NODE)
            if not b:
                continue
            fl = memoryview(b)[: len(b) // 4 * 4].cast("f")
            for i, f in enumerate(fl):
                for n, v in targets.items():
                    if f == v:
                        hits[n].append(path + [i * 4])
            if level == depth:
                continue
            for off in range(0, min(PTRS, len(b)) - 7, 8):
                q = struct.unpack_from("<Q", b, off)[0]
                if ok(q) and q not in seen:
                    seen.add(q)
                    nxt.append((q, path + [off]))
        print("level %d: %d blocks searched (%.0f s)" % (level, len(frontier), time.time() - t0))
        frontier = nxt
    for n, h in hits.items():
        json.dump(h, open(os.path.join(m.RUNS, "bfs_%s.json" % n), "w"))
        print("%s=%s: %d candidate paths" % (n, targets[n], len(h)))


def nxt(p, obj, targets):
    for n, v in targets.items():
        f = os.path.join(m.RUNS, "bfs_%s.json" % n)
        paths = json.load(open(f))
        keep = [x for x in paths if (lambda r: r is not None and abs(r - v) < 1e-3)(resolve(p, obj, x))]
        json.dump(keep, open(f, "w"))
        print("%s=%s: %d -> %d" % (n, v, len(paths), len(keep)))
        for x in keep[:15]:
            print("   " + " -> ".join("+%X" % o for o in x))


def main():
    cmd, obj = sys.argv[1], int(sys.argv[2], 16)
    p = m.Proc()
    os.makedirs(m.RUNS, exist_ok=True)
    if cmd == "save":
        depth = int(sys.argv[3])
        save(p, obj, depth, {k: float(v) for k, v in (a.split("=") for a in sys.argv[4:])})
    else:
        nxt(p, obj, {k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])})


if __name__ == "__main__":
    main()
