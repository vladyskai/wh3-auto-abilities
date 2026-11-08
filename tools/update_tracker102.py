"""Round-102 tracker update: per-row statuses for every touched ability, the
three new trigger names, and the round's §10.4 record."""
import json, os, re

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
TRK = os.path.join(ROOT, "docs", "WH3_ability_tracker.md")
plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))

lines = open(TRK, "rb").read().decode("utf-8").split("\n")

def real(k):
    return k

A_KEYS = plan["A_keys"]
D_KEYS = plan["D_keys"]
F_KEYS = plan["F_keys"]

# per-key range text
spec_ranges = {}
import csv
T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
with open(os.path.join(T, "unit_spec_abil.tsv"), "r", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        k = r.get("key") or ""
        if k.startswith("#"):
            continue
        try:
            spec_ranges[k] = float(r.get("target_intercept_range") or 0)
        except ValueError:
            spec_ranges[k] = 0.0

def bound_text(k):
    r = spec_ranges.get(k, 0.0)
    if r <= 0:
        return "no real range (target_intercept_range = -1.0) - no 70% bound"
    return "%d m of its %g m target_intercept_range" % (int(r * 0.70 + 1e-9), r)

CLASSES = {}
for k in A_KEYS + D_KEYS:
    CLASSES[k] = ("A", "`implemented (enemy-ground: closest FIGHTING enemy)`", "enemy_ground_melee",
                  "The CLOSEST enemy within the ability's 70%% bound (%s) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check)." % bound_text(k),
                  "implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102)")
for k in F_KEYS:
    CLASSES[k] = ("F", "`implemented (closest non-commander enemy in melee, enemy ground)`", "enemy_melee_noncommander",
                  "ANY enemy within the ability's 70%% bound (%s) that is IN MELEE and is NOT a Lord or Hero; the closest wins; the explosion + summon is placed on THAT ENEMY's ground." % bound_text(k),
                  "implemented per the user's ruling for this key (harness 102)")
CLASSES["wh3_dlc26_lord_abilities_eye_of_khorne"] = ("E",
    "`implemented (enemy finisher: lowest-health non-commander below 20%)`", "enemy_low_health_noncommander",
    "ANY enemy within the ability's 70% bound (35 m of 50 m) that is BELOW 20% health and is NOT a Lord or Hero; the LOWEST-health one wins (closest as the tiebreak); cast on that enemy through the UNIT form (target_enemies).",
    "implemented per the user's finisher ruling (harness 102)")
CLASSES["wh3_main_lord_abilities_nurgling_tide"] = ("B",
    "`implemented (self-summon: the caster itself is in melee)`", "self_summon_melee",
    "Fires ONLY when the CASTER ITSELF is in melee (owner alive, not routing, is_in_melee()); cast on SELF, no range bound needed.",
    "the user's ruling, verbatim: \"that one should only trigger when the caster himself is in melee\" (harness 102)")
for k in ("wh2_dlc10_lord_abilities_deadly_mislead", "wh3_dlc24_lord_item_deceiving_shadows",
          "wh2_dlc14_unit_abilities_doppelgang", "wh2_dlc10_lord_abilities_mislead"):
    CLASSES[k] = ("C", "`excluded (not in wheel: illusion summon)`", "—",
                  "illusion (spawn_is_decoy; refused when engaged in melee)",
                  "excluded 2026-10-17 (round 102) - the engine refuses an illusion while its caster is engaged in melee, so a melee trigger can never fire it")

updated = []
missing = []
for key, (cls, status, trig, logic, note) in CLASSES.items():
    hits = 0
    for i, ln in enumerate(lines):
        if not ln.startswith("| "):
            continue
        if ("`%s`" % key) not in ln:
            continue
        cells = ln.split(" | ")
        if len(cells) < 5:
            continue
        # cells[0] = "| name `key`", cells[1] = status, [2] = trigger, [3] = logic, [4] = stats...|
        cells[1] = status
        cells[2] = trig
        cells[3] = logic
        last = cells[-1]
        if "round 102" not in last:
            if last.endswith(" |"):
                last = last[:-2] + " · **round 102 (2026-10-17):** " + note + " |"
            else:
                last = last + " · **round 102 (2026-10-17):** " + note
        cells[-1] = last
        lines[i] = " | ".join(cells)
        hits += 1
    if hits:
        updated.append((cls, key, hits))
    else:
        missing.append((cls, key))

print("rows updated:", len(updated), "| files keys with no status row:", len(missing))
for cls in "ABCDF":
    n = sum(1 for c, k, h in updated if c == cls)
    print("  class", cls, "keys with a row:", n)
print("missing:", missing)

# ---- the top-of-file Update paragraph (after the harness-101 one) ----------
anchor = None
for i, ln in enumerate(lines):
    if ln.startswith("**Update 2026-10-17 (harness 101 — BOSS-ONLY EXCLUSION + GATE OF KHORNE).**"):
        anchor = i
        break
assert anchor is not None

UPDATE = (
"**Update 2026-10-17 (harness 102 — THE SUMMON ROUND).** **A. The rest of the summon class.** Every in-wheel, "
"non-illusion, **GROUND-CASTABLE** `wh_type_summon_unit` row (derived from the game's own data: `spawned_unit` set + "
"type `wh_type_summon_unit` + `spawn_is_decoy` false + `target_ground` true + in-wheel + not boss-only + not already "
"implemented) is now **implemented on the proven `enemy_ground_melee` trigger** — the closest FIGHTING enemy inside the "
"ability's own 70% bound, the summon placed on THAT ENEMY's ground: **57 entries / 68 keys**. Exactly **one** row of the "
"label set cannot take a ground point — **Nurgling Tide** (no target flags at all, `affect_self` = true, range 0) — and "
"it is the one self-target summon (B). One A entry (The Tallyman's Blades Upgraded) declares "
"`target_intercept_range` = -1.0, so it carries `unbounded = true` and has no 70% bound to take. "
"**B. Nurgling Tide** rides a NEW `self_summon_melee` trigger — the user's rule, verbatim: *\"that one should only "
"trigger when the caster himself is in melee.\"* Owner alive + not routing + `is_in_melee()`, cast on SELF through the "
"unit form with a freshly re-fetched caster controller, a hold and a pre-cast re-check of the same state; NO range "
"bound (a self cast has no distance to measure). "
"**C. The four illusions are EXCLUDED** — `excluded (not in wheel: illusion summon)`, reason *illusion (spawn_is_decoy; "
"refused when engaged in melee)*: Call of the Shadow Dancer, Deceiving Shadows, Doppelgang, Mislead. None was ever in "
"the mod, so nothing had to be removed. "
"**D. The nine unlabelled real spawners** are implemented on the same trigger: Beast Pack, Blacktoof's Conjuration, "
"Call to Gwindalor, Lesser Raise Dead, Savage Dominion, Savage Predators, Tide of Death, Tide of Pox, Wake Da Idol "
"(9 entries / 9 keys). "
"**E. Eye of Khorne** is a FINISHER on a NEW `enemy_low_health_noncommander` trigger: any enemy inside its 70% bound "
"(35 m of 50 m) BELOW 20% health that is NOT a Lord or Hero; the lowest-health one wins (closest as the tiebreak), "
"cast through the UNIT form. The Lord/Hero test is a REAL READ — a derived commander-class key set from the game's own "
"`land_units.class` = \"com\" ∪ `main_units.caste` ∈ {lord, hero}, matched by exact whole-key equality against "
"`battle_unit:type()`, with `battle_unit:unit_class()` == \"com\" as the fallback and a FAIL-CLOSED default. "
"**F. The Dreaded Thirteenth** (four keys, one entry) rides a NEW `enemy_melee_noncommander` trigger: the closest "
"non-commander enemy in melee inside its 70% bound (70 m of 100 m), placed on its ground. "
"**Counts:** ABILITIES **573 -> 642 entries** (573 + 69), **599 -> 682 keys** (599 + 83); `melee_unwavering` stays "
"**360**, `enemy_engaged_or_shot` stays **86**, `enemy_ground_area` stays **9**; `enemy_ground_melee` **1 -> 67**; the "
"new `self_summon_melee` / `enemy_low_health_noncommander` / `enemy_melee_noncommander` each **1**. Full record: **§10.4**. "
"Spreadsheet: `docs/WH3_abilities_master_v4_2026-10-17.xlsx` (v4 supersedes v3; v1-v3 unchanged)."
)
lines.insert(anchor + 1, "")
lines.insert(anchor + 2, UPDATE)

open(TRK, "wb").write("\n".join(lines).encode("utf-8"))
print("tracker written; bytes", os.path.getsize(TRK))
