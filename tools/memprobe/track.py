r"""READ-ONLY candidate tracker (the Cheat Engine 'next scan', on paths from the unit handle).
  track.py save <obj> <name> <value>     : store every depth<=2 path whose float == value
  track.py next <obj> <name> <value>     : keep only paths that now read value (re-resolved from obj)
  track.py show <obj> <name>             : print the remaining paths and their values"""
import sys, os, json, struct, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
p = m.Proc()
cmd, obj, name = sys.argv[1], int(sys.argv[2], 16), sys.argv[3]
F = os.path.join(m.RUNS, "track_%s.json" % name)
def resolve(path):
    a = obj
    for o in path[:-1]:
        a = p.u64(a + o)
        if a is None: return None
    b = p.read(a + path[-1], 4)
    return None if not b or len(b) < 4 else struct.unpack("<f", b)[0]
def parse(label):  # "[[+120]+238]+2A0" -> [0x120, 0x238, 0x2A0]
    return [int(x, 16) for x in label.replace("[", "").replace("]", "").split("+")[1:]]
if cmd == "save":
    out = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "pattern.py"), sys.argv[2],
                          "0:" + sys.argv[4]], capture_output=True, text=True).stdout.split("\n")
    paths = sorted({tuple(parse(l.split()[0])) for l in out if l.endswith("<f") and l.startswith("[")})
    json.dump([list(x) for x in paths], open(F, "w"))
    print("%s: %d candidate paths saved" % (name, len(paths)))
elif cmd == "next":
    v = float(sys.argv[4])
    paths = json.load(open(F))
    keep = [x for x in paths if (lambda r: r is not None and abs(r - v) < 1e-3)(resolve(x))]
    json.dump(keep, open(F, "w"))
    print("%s: %d -> %d" % (name, len(paths), len(keep)))
    for x in keep[:20]: print("  " + "".join("[" for _ in x[:-1]) + "".join("+%X]" % o for o in x[:-1]) + "+%X" % x[-1])
else:
    for x in json.load(open(F)): print(x, resolve(x))
