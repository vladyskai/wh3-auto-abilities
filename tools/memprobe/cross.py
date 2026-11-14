r"""READ-ONLY: resolve every saved bfs path of <name> from several unit handles, side by side."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
from bfs import resolve
p = m.Proc()
name, objs = sys.argv[1], [int(a, 16) for a in sys.argv[2:]]
for path in json.load(open(os.path.join(m.RUNS, "bfs_%s.json" % name))):
    vals = [resolve(p, o, path) for o in objs]
    print("%-34s " % " -> ".join("+%X" % o for o in path) + " ".join("%8s" % ("?" if v is None else "%.2f" % v) for v in vals))
