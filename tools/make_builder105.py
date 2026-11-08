"""Clone build_and_install104.py into the round-105 release builder.

Adds the round note and the round's content gates, and re-pins the five
table-size gates 642 -> 643 (Tz'arkan is ONE new entry, FIVE new keys).
"""
import os
import re
import shutil

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
SRC_DIR = os.path.join(ROOT, "mod_source", "releases", "20261017_nurgling_star_harness104")
DST_DIR = os.path.join(ROOT, "mod_source", "releases", "20261017_tzarkan_harness105")
os.makedirs(DST_DIR, exist_ok=True)

src = open(os.path.join(SRC_DIR, "build_and_install104.py"), encoding="utf-8").read()

# ---------------------------------------------------------------- the note
NOTE = """
ROUND v105 (2026-10-17): TZ'ARKAN ON A LOW-HEALTH TRIGGER + THE TRANSFORMS SKIPPED.
(A) TZ'ARKAN. The user's rule: "activate Tz'arkan when caster health is below
    15%". ONE new entry ("tzarkan") carries all FIVE Tz'arkan keys (base, _mp,
    _snikch, _spite, _spite_mp) on ONE new trigger family, health_below_15:
    the owner is ALIVE, NOT routing, and its health - through FOURTH.health_pct,
    the ONE 0-100 reader, NEVER raw HealthPercent - is BELOW 15. The cast is on
    the OWNER ITSELF through the unit form, with the caster's controller
    re-fetched FRESH that tick; no range bound is read (a self cast has no
    distance). The exact percentage is logged at the decision and again at the
    PRE-CAST RE-CHECK, which SKIPS the cast when the unit died or rose above
    the line inside the wind-up. The in-flight and charge gates apply through
    the shared tables (3.0 s wind-up on four keys, 1.5 s on Snikch).
    THE THRESHOLD IS DELIBERATE and ONE constant (FOURTH.TZARKAN_PCT = 15): the
    transform is likely one-way and the wind-up can let a 14% caster die before
    it resolves - raise the constant if field tests show that.
    Counts: 642 -> 643 entries, 682 -> 687 keys, 42 -> 43 evaluators.
(B) THE REST OF THE TRANSFORMS ARE SKIPPED BY THE USER'S DECISION (no
    automation wanted): Formless Horror x4, Transformation of the Dragon x6,
    Burrow and Surface - 12 keys, NONE of them implemented, so NOTHING is in
    this pack for them. The tracker and the master spreadsheet record
    "skipped (user decision 2026-10-17: no automation wanted)".
"""
anchor = '    inside the wind-up.\n"""\n'
assert src.count(anchor) == 1
src = src.replace(anchor, '    inside the wind-up.\n' + NOTE + '"""\n')

# ---------------------------------------------------------------- size gates
old = 'assert script_txt.count("\\t{ marker = ") == 642, "the abilities table is not 642 entries"'
assert src.count(old) == 5, src.count(old)
src = src.replace(old, 'assert script_txt.count("\\t{ marker = ") == 643, "the abilities table is not 643 entries"')

# ---------------------------------------------------------------- the new gates
GATES = '''
# ROUND v105 (2026-10-17): TZ'ARKAN ON THE NEW LOW-HEALTH TRIGGER - ONE entry,
# FIVE keys, below 15% of the ONE health reader, cast on SELF, with a pre-cast
# re-check that logs the exact percentage and skips a dead or risen caster.
# Nothing above is loosened.
TZ_KEYS = [
    "wh2_dlc14_lord_abilities_tzarkan",
    "wh2_dlc14_lord_abilities_tzarkan_mp",
    "wh2_dlc14_lord_abilities_tzarkan_snikch",
    "wh2_dlc14_lord_abilities_tzarkan_spite",
    "wh2_dlc14_lord_abilities_tzarkan_spite_mp",
]
assert script_txt.count('marker = "tzarkan"') == 1, "the tzarkan entry is missing (or duplicated)"
assert 'name = "Tz\\'arkan", trigger = "health_below_15",' in script_txt, \\
    "the tzarkan entry is not on the new low-health trigger"
assert 'badge = "zz_auto_badge_tzarkan"' in script_txt, "the tzarkan badge id is missing"
for _k in TZ_KEYS:
    assert '"%s"' % _k in script_txt, "a Tz'arkan key is missing: " + _k
assert "FOURTH.TZARKAN_PCT = 15" in script_txt, "the 15% threshold constant is missing"
assert "function FOURTH.evaluate_tzarkan_low_health(unit, routing)" in script_txt, \\
    "the tzarkan evaluator is missing"
assert "health_below_15 = FOURTH.evaluate_tzarkan_low_health," in script_txt, \\
    "the tzarkan trigger is not wired in the evaluator map"
assert 'health_below_15 = "When armed, fires when this unit is below 15% health"' in script_txt, \\
    "the tzarkan tooltip sentence is missing"
_TZ_EV = script_txt[script_txt.find("function FOURTH.evaluate_tzarkan_low_health(unit, routing)"):]
_TZ_EV = _TZ_EV[:_TZ_EV.find("\\nend")]
assert "FOURTH.health_pct(unit)" in _TZ_EV, "the evaluator does not use the ONE health reader"
assert "HealthPercent" not in _TZ_EV, "the evaluator reads raw HealthPercent (the 0..1 fraction trap)"
assert script_txt.count("if FOURTH.tz_self then") == 2, \\
    "the tzarkan cast handle and pre-cast re-check are not both present"
assert "FOURTH.tz_self = nil" in script_txt and "FOURTH.tz_caster_su = nil" in script_txt, \\
    "the tzarkan cast slots are not declared"
assert "tzarkan SKIPPED: the caster lapsed before the cast" in script_txt, \\
    "the pre-cast skip line is missing"
assert "tzarkan pre-cast re-check: the caster is still below the line" in script_txt, \\
    "the pre-cast re-check line is missing"
assert '["wh2_dlc14_lord_abilities_tzarkan"] = 3,' in script_txt, \\
    "Tz'arkan's own 3 s wind-up is missing from the in-flight gate"
assert '["wh2_dlc14_lord_abilities_tzarkan_snikch"] = 1.5,' in script_txt, \\
    "the Snikch key's 1.5 s wind-up is missing from the in-flight gate"
assert "BELOW the %d%% line" in script_txt, "the decision reason does not carry the exact percentage"

# THE 12 TRANSFORMS THE USER SKIPPED ARE NOT AUTOMATED - no key of theirs may
# appear in the shipped script at all (they were never in the ABILITIES table).
SKIPPED_TRANSFORMS = [
    "wh3_dlc24_lord_abilities_formless_horror",
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
    "wh3_dlc27_unit_abilities_dread_maw_surface",
]
for _k in SKIPPED_TRANSFORMS:
    assert '"%s"' % _k not in script_txt, "a user-skipped transform key is in the mod: " + _k

'''
anchor2 = "# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the"
assert src.count(anchor2) == 1
src = src.replace(anchor2, GATES + anchor2)

dst = os.path.join(DST_DIR, "build_and_install105.py")
open(dst, "wb").write(src.encode("utf-8"))
print("wrote", dst, len(src.encode("utf-8")), "bytes")
