"""Clone build_and_install104.py into the round-105 release builder.

Adds the round note and the round's content gates, and re-pins the five
table-size gates 642 -> 643 (Tz'arkan is ONE new entry, FIVE new keys).
"""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
SRC_DIR = os.path.join(ROOT, "mod_source", "releases", "20261017_nurgling_star_harness104")
DST_DIR = os.path.join(ROOT, "mod_source", "releases", "20261017_tzarkan_harness105")
os.makedirs(DST_DIR, exist_ok=True)

src = open(os.path.join(SRC_DIR, "build_and_install104.py"), encoding="utf-8").read()
lines = src.split("\n")

AP = chr(39)      # the apostrophe in Tz'arkan
CONT = chr(92)    # a single backslash: the Python line continuation

NOTE = [
    "",
    "ROUND v105 (2026-10-17): TZ" + AP + "ARKAN ON A LOW-HEALTH TRIGGER + THE TRANSFORMS SKIPPED.",
    "(A) TZ" + AP + "ARKAN. The user" + AP + "s rule: \"activate Tz" + AP + "arkan when caster health is below",
    "    15%\". ONE new entry (\"tzarkan\") carries all FIVE Tz" + AP + "arkan keys (base, _mp,",
    "    _snikch, _spite, _spite_mp) on ONE new trigger family, health_below_15:",
    "    the owner is ALIVE, NOT routing, and its health - through FOURTH.health_pct,",
    "    the ONE 0-100 reader, NEVER raw HealthPercent - is BELOW 15. The cast is on",
    "    the OWNER ITSELF through the unit form, with the caster" + AP + "s controller",
    "    re-fetched FRESH that tick; no range bound is read (a self cast has no",
    "    distance). The exact percentage is logged at the decision and again at the",
    "    PRE-CAST RE-CHECK, which SKIPS the cast when the unit died or rose above",
    "    the line inside the wind-up. The in-flight and charge gates apply through",
    "    the shared tables (3.0 s wind-up on four keys, 1.5 s on Snikch).",
    "    THE THRESHOLD IS DELIBERATE and ONE constant (FOURTH.TZARKAN_PCT = 15): the",
    "    transform is likely one-way and the wind-up can let a 14% caster die before",
    "    it resolves - raise the constant if field tests show that.",
    "    Counts: 642 -> 643 entries, 682 -> 687 keys, 42 -> 43 evaluators.",
    "(B) THE REST OF THE TRANSFORMS ARE SKIPPED BY THE USER" + AP + "S DECISION (no",
    "    automation wanted): Formless Horror x4, Transformation of the Dragon x6,",
    "    Burrow and Surface - 12 keys, NONE of them implemented, so NOTHING is in",
    "    this pack for them. The tracker and the master spreadsheet record",
    "    \"skipped (user decision 2026-10-17: no automation wanted)\".",
]
idx = None
for i, l in enumerate(lines):
    if l.startswith("    standing 70% rule (aura_real/ally_range_real"):
        assert lines[i + 1] == '"""', repr(lines[i + 1])
        idx = i + 1
        break
assert idx is not None, "the v104 note's end was not found"
lines[idx:idx] = NOTE
src = "\n".join(lines)

# ---------------------------------------------------------------- size gates
old = 'assert script_txt.count("\\t{ marker = ") == 642, "the abilities table is not 642 entries"'
assert src.count(old) == 5, src.count(old)
src = src.replace(old, 'assert script_txt.count("\\t{ marker = ") == 643, "the abilities table is not 643 entries"')

# ---------------------------------------------------------------- the new gates
g = []
g.append("")
g.append("# ROUND v105 (2026-10-17): TZ" + AP + "ARKAN ON THE NEW LOW-HEALTH TRIGGER - ONE entry,")
g.append("# FIVE keys, below 15% of the ONE health reader, cast on SELF, with a pre-cast")
g.append("# re-check that logs the exact percentage and skips a dead or risen caster.")
g.append("# Nothing above is loosened.")
g.append("TZ_KEYS = [")
for k in ("wh2_dlc14_lord_abilities_tzarkan",
          "wh2_dlc14_lord_abilities_tzarkan_mp",
          "wh2_dlc14_lord_abilities_tzarkan_snikch",
          "wh2_dlc14_lord_abilities_tzarkan_spite",
          "wh2_dlc14_lord_abilities_tzarkan_spite_mp"):
    g.append('    "%s",' % k)
g.append("]")
g.append('assert script_txt.count(' + chr(39) + 'marker = "tzarkan"' + chr(39) + ') == 1, "the tzarkan entry is missing (or duplicated)"')
g.append('assert ' + chr(39) + 'name = "Tz' + CONT + AP + 'arkan", trigger = "health_below_15",' + chr(39) + ' in script_txt, ' + CONT)
g.append('    "the tzarkan entry is not on the new low-health trigger"')
g.append('assert ' + chr(39) + 'badge = "zz_auto_badge_tzarkan"' + chr(39) + ' in script_txt, "the tzarkan badge id is missing"')
g.append("for _k in TZ_KEYS:")
g.append('    assert ' + chr(39) + '"%s"' + chr(39) + ' % _k in script_txt, "a Tz' + AP + 'arkan key is missing: " + _k')
g.append('assert "FOURTH.TZARKAN_PCT = 15" in script_txt, "the 15% threshold constant is missing"')
g.append('assert "function FOURTH.evaluate_tzarkan_low_health(unit, routing)" in script_txt, ' + CONT)
g.append('    "the tzarkan evaluator is missing"')
g.append('assert "health_below_15 = FOURTH.evaluate_tzarkan_low_health," in script_txt, ' + CONT)
g.append('    "the tzarkan trigger is not wired in the evaluator map"')
g.append('assert ' + chr(39) + 'health_below_15 = "When armed, fires when this unit is below 15% health"' + chr(39) + ' in script_txt, ' + CONT)
g.append('    "the tzarkan tooltip sentence is missing"')
g.append('_TZ_EV = script_txt[script_txt.find("function FOURTH.evaluate_tzarkan_low_health(unit, routing)"):]')
g.append('_TZ_EV = _TZ_EV[:_TZ_EV.find("' + CONT + 'nend")]')
g.append('assert "FOURTH.health_pct(unit)" in _TZ_EV, "the evaluator does not use the ONE health reader"')
g.append('assert "HealthPercent" not in _TZ_EV, "the evaluator reads raw HealthPercent (the 0..1 fraction trap)"')
g.append('assert script_txt.count("if FOURTH.tz_self then") == 2, ' + CONT)
g.append('    "the tzarkan cast handle and pre-cast re-check are not both present"')
g.append('assert "FOURTH.tz_self = nil" in script_txt and "FOURTH.tz_caster_su = nil" in script_txt, ' + CONT)
g.append('    "the tzarkan cast slots are not declared"')
g.append('assert "tzarkan SKIPPED: the caster lapsed before the cast" in script_txt, ' + CONT)
g.append('    "the pre-cast skip line is missing"')
g.append('assert "tzarkan pre-cast re-check: the caster is still below the line" in script_txt, ' + CONT)
g.append('    "the pre-cast re-check line is missing"')
g.append('assert ' + chr(39) + '["wh2_dlc14_lord_abilities_tzarkan"] = 3,' + chr(39) + ' in script_txt, ' + CONT)
g.append('    "Tz' + AP + 'arkan' + AP + 's own 3 s wind-up is missing from the in-flight gate"')
g.append('assert ' + chr(39) + '["wh2_dlc14_lord_abilities_tzarkan_snikch"] = 1.5,' + chr(39) + ' in script_txt, ' + CONT)
g.append('    "the Snikch key' + AP + 's 1.5 s wind-up is missing from the in-flight gate"')
g.append('assert "BELOW the %d%% line" in script_txt, "the decision reason does not carry the exact percentage"')
g.append("")
g.append("# THE 12 TRANSFORMS THE USER SKIPPED ARE NOT AUTOMATED - no key of theirs may")
g.append("# appear in the shipped script at all (they were never in the ABILITIES table).")
g.append("SKIPPED_TRANSFORMS = [")
for k in ("wh3_dlc24_lord_abilities_formless_horror",
          "wh3_dlc24_lord_abilities_formless_horror_changeling",
          "wh3_dlc24_lord_abilities_formless_horror_quest_battle",
          "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form",
          "wh3_dlc24_lord_abilities_jade_dragon_dragon_form",
          "wh3_dlc24_lord_abilities_jade_dragon_human_form",
          "wh3_main_lord_abilities_iron_dragon_dragon_form",
          "wh3_main_lord_abilities_iron_dragon_human_form",
          "wh3_main_lord_abilities_storm_dragon_dragon_form",
          "wh3_main_lord_abilities_storm_dragon_human_form",
          "wh3_dlc27_unit_abilities_dread_maw_underground",
          "wh3_dlc27_unit_abilities_dread_maw_surface"):
    g.append('    "%s",' % k)
g.append("]")
g.append("for _k in SKIPPED_TRANSFORMS:")
g.append('    assert ' + chr(39) + '"%s"' + chr(39) + ' % _k not in script_txt, "a user-skipped transform key is in the mod: " + _k')
g.append("")
GATES = "\n".join(g) + "\n"

anchor2 = "# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the"
assert src.count(anchor2) == 1
src = src.replace(anchor2, GATES + anchor2)

dst = os.path.join(DST_DIR, "build_and_install105.py")
open(dst, "wb").write(src.encode("utf-8"))
print("wrote", dst, len(src.encode("utf-8")), "bytes")
