#!/usr/bin/env python3
"""Round 164: the tracker rows (28 implemented) and section 10.42, and the database family texts."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SRC = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua", encoding="utf-8").read()
KF = GW.keys_in(SRC)
WW = GW.derive(KF)
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
NOTE = " · **round 164 (2026-11-16):** the friendly-fire breaths, user ruling \"%s\"."
KEYS = """wh3_main_item_abilities_bangstick wh2_main_item_abilities_black_dragon_egg wh3_main_daemon_arms_abilities_blue_fire
wh3_main_daemon_arms_abilities_blue_fire_upgraded wh_main_item_abilities_fiery_ring_of_thori
wh2_main_lord_abilities_gaze_of_malice wh3_dlc24_unit_abilities_jade_dragons_breath wh3_main_item_abilities_kovsh_breath
wh3_dlc27_spell_bound_lash_of_slaanesh wh3_main_spell_bound_lash_of_slaanesh
wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets wh3_dlc20_spell_bound_pink_fire_of_tzeentch
wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound wh2_main_mount_bound_scorch wh3_dlc20_spell_bound_stream_of_corruption
wh3_main_spell_nurgle_stream_of_corruption_bound wh2_main_weapon_abilities_sunfang
wh3_dlc20_weapon_abilities_the_spear_slaupnir wh2_dlc11_spell_bound_tidecall wh2_dlc11_spell_bound_wind_blast
wh2_dlc15_character_abilities_fishy_breathe wh2_main_mount_bound_pestilent_breath wh3_main_spell_bound_pestilent_breath
wh2_dlc13_character_ability_shatter wh_main_weapon_abilities_skabscrath wh3_dlc29_unit_active_ripping_blades
wh3_dlc29_unit_abilities_flesh_eating_scarabs wh2_dlc15_lord_abilities_da_boss_loons""".split()
assert len(KEYS) == 28


def bound(k):
    return int(math.floor(float(USA[k]["target_intercept_range"]) * 0.70 + 1e-9))


def row_text(k):
    fam = KF[k]
    kind, r, path, off, buf, allies, ground = WW[k]
    b = bound(k)
    if fam == "enemy_wave":
        melee = " Not while its caster is in melee (the game's rule)." if k in GW.nomelee([k]) else ""
        return ("implemented (clear wave path, most value, target standing: enemy_wave)",
                "When armed and standing still, casts at the standing enemy within %d m whose %g m path holds the most "
                "enemy value and none of our other units within %g m of it (the caster's own breath does not count).%s"
                % (b, path, r + 10, melee), "Wave rule")
    if fam == "enemy_wave_charge":
        return ("implemented (charging enemy, clear wave path: enemy_wave_charge)",
                "When armed and standing still, casts its wave at a fast enemy within %d m closing on our units, when the "
                "%g m path from the caster through it holds none of our other units within %g m (it slows the target: "
                "rule 10)." % (b, path, r + 10), "Charge, clear path")
    if fam == "enemy_cone":
        return ("implemented (clear cone, most value: enemy_cone)",
                "When armed and standing still, breathes at the standing enemy within %d m whose %g m cone from the "
                "caster holds the most enemy value and none of our other units within %g m of it." % (b, off + path, r + 10),
                "Clear cone, most value")
    if fam == "enemy_sweep":
        return ("implemented (melee sweep, no friend near: enemy_sweep)",
                "When armed, in melee and not wavering, sweeps the closest enemy in melee within %d m when none of our "
                "other units are within %g m of the caster (its %g m reach + 10 m)." % (b, r + 10, r),
                "Sweeps clear; Loons as wanderer")
    assert fam == "enemy_wander" and kind == 6, (k, fam, kind)
    return ("implemented (wanderer released at the caster: enemy_wander)",
            "When armed and standing still, casts at the standing enemy infantry within %d m worth the most, when none of "
            "our other units are within %g m of the caster (radius %g + reach %d + 10 m)." % (b, r + buf + 10, r, buf),
            "Sweeps clear; Loons as wanderer")


ROWS = {k: row_text(k) for k in KEYS}
SECTION = """

### 10.42 Round 164 - the friendly-fire breaths (2026-11-16)

**Earlier status:** "excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))", a RULE, never a
ruling on these 28 abilities one by one. They are VORTEX breaths (the 77 projectile breaths already ride enemy_blob).

**Rulings (user, 2026-11-16).**

- **18 target-launched breaths:** "Wave rule" -> `enemy_wave`.
- **Tidecall, Wind Blast (slows, rule 10):** "Charge, clear path" -> NEW `enemy_wave_charge`.
- **5 breaths from the caster's front:** "Clear cone, most value" -> NEW `enemy_cone`.
- **Disembowelling Sweep, Flesh-eating Scarabs:** "Sweeps clear" -> NEW `enemy_sweep`; **Da Boss' Loons:** "Loons as
  wanderer" -> `enemy_wander` (the safety ring around the caster).
- **"Caster doesn't count":** a caster's own breath or wave never blocks its cast (round 162's waves included).
- **Side effects named in the proposal:** warpflame (armour -10), poison (speed and damage x0.85), Tidecall speed x0.75,
  Wind Blast speed x0.6, morale -6 / -16 for the sweeps.

**Arithmetic.**

- **Rows:** implemented 975 + 28 = **1,003 rows / keys**; not implemented among the included 148 - 28 = **120**, of which
  36 are the user's skips.
- **The mod:** 918 + 28 = **946 entries / 1,003 keys**; **95** families.
- **Tests:** harness 163 full suite **6,947 checks / 0 failures**, run twice byte-identical. RED 16/16.
- **Install:** pack md5 `b4ff0c03c8246166b426bb881c2012aa`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in ROWS:
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            st, pr, rule = ROWS[k]
            c[1] = "`%s`" % st
            c[3] = pr
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.42" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION and all("\u2014" not in t for v in ROWS.values() for t in v)
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.42" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_wave_charge": "The caster STANDING STILL; a FAST enemy in range closing on our units (enemy_fast_near_'
       'ally\'s test) whose wave path, from the caster through it, holds none of our OTHER units within radius + 10 m; the '
       'most enemy value on the path. Casts on that enemy; re-checked before the cast.",\n'
       '        "enemy_cone": "The caster STANDING STILL; a STANDING enemy in range; the zone from the caster through it '
       '(offset + path long, radius + 10 m wide) holds none of our OTHER units; the most enemy value in it. Casts on that '
       'enemy; re-checked before the cast.",\n'
       '        "enemy_sweep": "The caster in melee and not wavering; none of our OTHER units within the sweep\'s reach + 10 m '
       'of the caster; the closest enemy in range that is fighting in melee. Casts on that enemy (on its ground for a '
       'ground-only sweep); re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and '"enemy_cone":' not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 3 family texts")
