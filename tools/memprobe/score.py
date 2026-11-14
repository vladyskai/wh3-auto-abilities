r"""READ-ONLY: score wide.py candidates across every unit in the battle against each unit's base value from
land_units (the game's own table). At the start of a battle, before fighting, a real live stat field equals
the base for most units (rank, auras and items explain the rest).
usage: score.py <log cut or log path> <stat=column> ...   e.g. ma=melee_attack md=melee_defence"""
import os, re, sys, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memprobe as m
from wide import value, F

GD = r"C:\Users\vlady\Desktop\WH3_mod\gamedata\wh3\land_units.tsv"
LOG = sys.argv[1]
ROW = re.compile(rb"MAP t=\S+ side=(\S) id=(\d+) type=(\S+) .* addr=battle\.unit_\(([0-9A-F]+)\)")
units = {}
with open(LOG, "rb") as f:
    f.seek(max(0, os.path.getsize(LOG) - 3_000_000))
    for line in f:
        mm = ROW.search(line)
        if mm:
            units[mm.group(2).decode()] = (mm.group(3).decode(), int(mm.group(4), 16))
rows = list(csv.reader(open(GD, encoding="utf-8"), delimiter="\t"))
h, lu = rows[0], {r[0]: r for r in rows[1:] if r}
p = m.Proc()
print("units:", len(units))
for arg in sys.argv[2:]:
    name, col = arg.split("=")
    ci = h.index(col)
    base = {}
    for uid, (typ, hd) in units.items():
        try:
            base[uid] = float(lu[typ][ci])
        except (KeyError, ValueError):
            pass
    scored = []
    for path, kind in json.load(open(F(name))):
        hit = sum(1 for uid, b in base.items() if (lambda v: v is not None and abs(v - b) < 1e-3)(value(p, units[uid][1], path, kind)))
        scored.append((hit, path, kind))
    scored.sort(key=lambda x: -x[0])
    print("== %s (%s): %d units with a table value" % (name, col, len(base)))
    for hit, path, kind in scored[:6]:
        print("   %3d/%d  %s (%s)" % (hit, len(base), " -> ".join("+%X" % o for o in path), kind))
