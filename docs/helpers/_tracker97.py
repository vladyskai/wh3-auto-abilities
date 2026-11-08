# -*- coding: utf-8 -*-
"""ROUND 97 tracker update: mark every Class-A enemy-targeted ability's row.

For each of the 105 Class-A keys (97 entries) the section-3a row is updated:
status -> implemented (enemy-targeted ...), group -> enemy_unit / enemy_ground,
the proposal names the enemy-targeting trigger + the 70% bound, and the notes
gain the enemy-targeting-mechanism tag. A round-97 update note is added.
"""
import json, io

TR = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
plan = json.load(open("C:/Users/vlady/Desktop/WH3_mod/audit/_classA_impl_plan.json", encoding="utf-8"))

lines = io.open(TR, encoding="utf-8", newline="").read().split("\n")

# key -> plan entry
k2p = {}
for p in plan:
    for k in p["keys"]:
        k2p[k] = p

def newcells(p):
    if p["ground"]:
        status = "`implemented (enemy-targeted: enemy-ground area)`"
        group = "enemy_ground"
        proposal = ("When an enemy unit within the 70%% bound (%d m of %d m) is in melee or under missile "
                    "fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route)."
                    % (p["bound"], p["real"]))
    else:
        status = "`implemented (enemy-targeted: in-melee / under-fire)`"
        group = "enemy_unit"
        proposal = ("When an enemy unit within the 70%% bound (%d m of %d m) is in melee or under missile "
                    "fire: cast at the ENEMY (unit hex, fresh-handle route)." % (p["bound"], p["real"]))
    return status, group, proposal

changed = 0
done_keys = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    hit = None
    for k in k2p:
        if ("`%s`" % k) in l and l.count("|") >= 5:
            hit = k
            break
    if hit is None:
        continue
    cells = l.split("|")
    if cells[2].strip() != "`implemented (in-melee self)`":
        continue
    p = k2p[hit]
    status, group, proposal = newcells(p)
    cells[2] = " " + status + " "
    cells[3] = " " + group + " "
    cells[4] = " " + proposal + " "
    cells[5] = cells[5].rstrip() + " · enemy-targeting mechanism (harness 97)"
    lines[i] = "|".join(cells)
    changed += 1
    done_keys.add(hit)

# the round-97 update note, inserted before the "## 1." heading
NOTE = (
    "**Update 2026-10-10 (harness 97 — the rest of Class A: enemy-targeted abilities):** the 97 remaining "
    "Class-A entries from `WH3_audit_report.md` (98 total; **Accusation** was already done and is the template) "
    "now fire at the ENEMY on the PROVEN Accusation mechanism. **88** ride the existing `enemy_engaged_or_shot` "
    "trigger (enemy-UNIT hexes); **9** ride a NEW `enemy_ground_area` trigger (enemy-GROUND area hexes) that "
    "casts through `perform_special_ability_ground(key, ENEMY_POSITION, 0, 0)` on the chosen enemy's ground. "
    "Every entry carries its own REAL `target_intercept_range` (`range_real`, from `unit_spec_abil.tsv`) mapped "
    "at load to ONE named 70% constant per real range (`FOURTH.ENEMY_CAST_R<real>`, 12 constants, "
    "`floor(real*0.70)`); the offer test is `unit:unit_distance(enemy) <= that constant` ONLY — never the "
    "engine's `unit_in_range`. The chosen enemy is the CAST TARGET (never the owner); fresh handles, the "
    "in-melee-preferred trigger, the pre-cast re-check and the hold are the Accusation ones; the log prints the "
    "REAL distance. `melee_unwavering` 480 -> 383; the table stays 579 entries / 605 keys. Harness 97: "
    "3075 checks green (red control: 77 designed failures, 27/54 worlds). Installed pack md5 "
    "`f42ed662ce42fee8a570593346cca4e6`."
    "\n\n**Update 2026-10-10 (annotated copy):** `WH3_auto_ability_annotated.lua` carries the same change "
    "(the per-ability bound, the shared picker, the enemy-ground evaluator/helper/key-set) — log-free / "
    "find-free, as always."
)

for i, l in enumerate(lines):
    if l.startswith("## 1. Implemented today"):
        lines[i:i] = [NOTE, ""]
        break

io.open(TR, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("rows updated:", changed, "of", len(k2p), "keys")
print("keys updated:", len(done_keys))
missing = [k for k in k2p if k not in done_keys]
print("keys NOT updated:", missing)
