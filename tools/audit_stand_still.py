#!/usr/bin/env python3
"""Round 190 audit (user 2026-11-21: "Fix the 8 and also audit all the triggers"): for every trigger family, does an
ANIMATED cast (the game's wind_up_stance, FOURTH.ANIM: the cast stops a moving caster, round 168) wait for its caster
to stand still?

Method: each family's evaluator (FOURTH.evaluators wiring) and every FOURTH.* function it reaches (transitive call
closure over the mod source). A family is GATED when that closure reaches FOURTH.blob_still (the one stand-still test;
ww_caster_ok and shot_caster_ok call it). Read-only; prints a table and writes docs/WH3_stand_still_audit_<date>.tsv."""
import collections
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_stand_still_audit_2026-11-21.tsv"
if len(sys.argv) > 1:   # ROUND 191: a later snapshot goes to its own file; the round-190 table stays as it was
    OUT = sys.argv[1]


def bodies(src):
    out, cur, buf = {}, None, []
    for line in src.split("\n"):
        m = re.match(r"function FOURTH\.(\w+)\(", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(1), [line]
            continue
        if cur:
            buf.append(line)
            if line == "end":
                out[cur] = "\n".join(buf)
                cur, buf = None, []
    return out


def closure(name, B, seen=None):
    seen = set() if seen is None else seen
    if name in seen or name not in B:
        return seen
    seen.add(name)
    for c in re.findall(r"FOURTH\.(\w+)\(", B[name]):
        closure(c, B, seen)
    return seen


def main():
    src = open(SRC, encoding="utf-8").read()
    B = bodies(src)
    anim = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', src).group(1).split(";"))
    wiring = dict(re.findall(r"\n\t(\w+) = FOURTH\.(evaluate_\w+),", src))
    tips = dict(re.findall(r'\n\t(\w+) = "(Fires[^"]*)"', src))
    m191 = re.search(r"\nFOURTH\.STILL_GATE_TRIGGERS = \{\n(.*?)\n\}\n", src, re.S)
    still_set = set(re.findall(r"(\w+) = true", m191.group(1))) if m191 else set()
    entries, _, _ = bd.mod_entries()
    fam = collections.defaultdict(list)
    for e in entries:
        fam[e.get("trigger")].append(e)
    rows = []
    for f in sorted(fam):
        ev = wiring.get(f)
        cl = closure(ev, B) if ev else set()
        # ROUND 191: an entry on a FOURTH.STILL_GATE_TRIGGERS trigger is wrapped at load (FOURTH.still_wrap asks blob_still)
        gated = "blob_still" in cl or f in still_set
        animated = [e for e in fam[f] if any(k in anim for k in e["keys"])]
        rows.append((f, ev or "?", len(fam[f]), len(animated), "yes" if gated else "NO",
                     "; ".join(e["name"] for e in animated), tips.get(f, "")))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["family", "evaluator", "entries", "animated", "stand_still_gate", "animated_entries", "card_tip"])
        w.writerows(rows)
    gap = [r for r in rows if r[4] == "NO" and r[3] > 0]
    ok = [r for r in rows if r[4] == "yes" and r[3] > 0]
    print("families", len(rows), "| with animated entries:", len(gap) + len(ok), "| gated:", len(ok),
          "| NOT gated:", len(gap), "| animated entries not gated:", sum(r[3] for r in gap))
    for r in sorted(gap, key=lambda r: -r[3]):
        print("%-32s %3d/%3d | %s | %s" % (r[0], r[3], r[2], r[6][:90], r[5][:150]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
