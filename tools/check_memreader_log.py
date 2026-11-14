r"""Round 148 field check: compare the memreader fields on the MAP rows with the engine's own reads.
  mr_men  must equal men=<alive>
  mr_hp   / (the unit's mr_hp while hp=1.00) must equal hp= (2 decimals)
  mr_lead is reported per unit (min / max / changes); the card is compared by hand.
usage: python tools/check_memreader_log.py <battle log cut>"""
import re, sys
from collections import defaultdict

ROW = re.compile(r"MAP t=(\S+) side=(\S) id=(\d+) type=(\S+) .* men=(\d+)/(\d+) hp=(\S+) .*mr_lead=(\S+) mr_hp=(\S+) mr_men=(\S+) ")
rows = []
with open(sys.argv[1], "rb") as f:
    for line in f:
        m = ROW.search(line.decode("utf-8", "replace"))
        if m:
            rows.append(m.groups())
print("rows with mr_ fields:", len(rows))
bad_men, full_hp, unread = [], {}, 0
for t, side, uid, typ, men, men0, hp, ml, mh, mm in rows:
    if "?" in (ml, mh, mm) or "-" in (ml, mh, mm):
        unread += 1
        continue
    if int(mm) != int(men):
        bad_men.append((t, uid, men, mm))
    if hp == "1.00" and uid not in full_hp:
        full_hp[uid] = int(mh)
print("rows unread (? or -):", unread)
print("mr_men != men: %d%s" % (len(bad_men), (" e.g. %s" % bad_men[:5]) if bad_men else ""))
hp_n = hp_bad = 0
worst = []
for t, side, uid, typ, men, men0, hp, ml, mh, mm in rows:
    if uid not in full_hp or hp == "?" or "?" in mh or "-" in mh:
        continue
    frac = int(mh) / full_hp[uid]
    hp_n += 1
    d = abs(frac - float(hp))
    if d > 0.0051:
        hp_bad += 1
        worst.append((d, t, uid, hp, mh, full_hp[uid]))
print("hp checks: %d, off by more than 0.005: %d" % (hp_n, hp_bad))
for w in sorted(worst, reverse=True)[:5]:
    print("   worst: d=%.3f t=%s id=%s hp=%s mr_hp=%s full=%s" % w)
lead = defaultdict(list)
for t, side, uid, typ, men, men0, hp, ml, mh, mm in rows:
    if ml not in ("?", "-"):
        lead[(side, uid, typ)].append(int(ml))
print("\nleadership per unit (first, min, max, number of changes):")
for (side, uid, typ), v in sorted(lead.items()):
    ch = sum(1 for a, b in zip(v, v[1:]) if a != b)
    print("  %s %s %-45s %4d %4d %4d  %3d" % (side, uid, typ[-45:], v[0], min(v), max(v), ch))
