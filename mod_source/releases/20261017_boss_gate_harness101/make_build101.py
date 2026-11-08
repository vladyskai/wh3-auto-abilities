# -*- coding: utf-8 -*-
"""Create build_and_install101.py from the round-100 builder.

Changes:
  * round-101 header paragraph (boss-only removal + Gate of Khorne)
  * every CURRENT-table pin re-based inside assertions: 577 -> 573,
    603 -> 599, 362 -> 360, enemy_engaged_or_shot 89 -> 86
  * the five boss-only entries dropped from the presence lists
    (BLOCK789 67/71 -> 66/70, AUTO327 311/327 -> 307/323)
  * removal asserts (absence) + Gate of Khorne's own gates
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261017_remove_army_two_harness100\build_and_install100.py"
OUT = os.path.join(HERE, "build_and_install101.py")

s = io.open(SRC, encoding="utf-8", newline="").read()

# ---------------------------------------------------------------- header
old_tail = '''ROUND v100 (2026-10-17): REMOVAL. Meat Feast (wh3_main_prisoners_butcher)
and Massacre (wh3_main_prisoners_massacre) were implemented but sit OUTSIDE
the single in-wheel rule (both source_type = army). Per the user's decision
of 2026-10-17 they are REMOVED from the ABILITIES table: 579 -> 577 entries,
605 -> 603 keys, melee_unwavering 363 -> 362, ushoran_health 34 -> 33.
Grut's Sickle and every other ability are untouched.
"""'''
new_tail = '''ROUND v100 (2026-10-17): REMOVAL. Meat Feast (wh3_main_prisoners_butcher)
and Massacre (wh3_main_prisoners_massacre) were implemented but sit OUTSIDE
the single in-wheel rule (both source_type = army). Per the user's decision
of 2026-10-17 they are REMOVED from the ABILITIES table: 579 -> 577 entries,
605 -> 603 keys, melee_unwavering 363 -> 362, ushoran_health 34 -> 33.
Grut's Sickle and every other ability are untouched.

ROUND v101 (2026-10-17): BOSS-ONLY EXCLUSION + GATE OF KHORNE.
(A) Every active ability whose only grant path is a `_boss` unit is excluded.
    Five were IMPLEMENTED and are REMOVED: Greater Faith Bastion
    (wh_dlc06_quest_abilities_grand_faiths_bastion), Bitter Sting
    (wh3_dlc27_qb_unit_abilities_bitter_sting), Frenzied Challenge
    (wh3_dlc27_qb_unit_abilities_frenzied_challenge), Visions of Madness
    (wh3_dlc27_qb_unit_abilities_visions_of_madness) and Guttural Roar
    (wh3_dlc27_qb_unit_abilities_guttural_roar). 577 -> 573 entries,
    603 -> 599 keys, melee_unwavering 362 -> 360, enemy_engaged_or_shot
    89 -> 86.
(B) Gate of Khorne (wh3_main_character_abilities_gate_of_khorne) is ADDED:
    its own `enemy_ground_melee` trigger - among enemies within its 70% bound
    (50 m -> 35 m) keep those FIGHTING (in melee), take the CLOSEST and place
    the summon on THAT ENEMY's ground via perform_special_ability_ground with
    the fresh caster controller. Its own reason string names the enemy type
    and the REAL distance; the cast target is never the caster.
    melee_unwavering self-cast and every other ability are untouched.
"""'''
assert s.count(old_tail) == 1
s = s.replace(old_tail, new_tail, 1)

# ---------------------------------------------------------------- remove the five list rows
ROWS = [
    '    ("grand_faiths_bastion", { "wh_dlc06_quest_abilities_grand_faiths_bastion" }),\n',
    '    ("bitter_sting", { "wh3_dlc27_qb_unit_abilities_bitter_sting" }),\n',
    '    ("frenzied_challenge", { "wh3_dlc27_qb_unit_abilities_frenzied_challenge" }),\n',
    '    ("visions_of_madness", { "wh3_dlc27_qb_unit_abilities_visions_of_madness" }),\n',
    '    ("guttural_roar", { "wh3_dlc27_qb_unit_abilities_guttural_roar" }),\n',
]
for r in ROWS:
    assert s.count(r) == 1, r
    s = s.replace(r, "", 1)
print("removed 5 list rows")

# ---------------------------------------------------------------- list counts
for old, new in (
        ('assert len(BLOCK789) == 67, "the block-7-9 entry list is not 67 (Meat Feast + Massacre removed)"',
         'assert len(BLOCK789) == 66, "the block-7-9 entry list is not 66 (Greater Faith Bastion removed in 101)"'),
        ('assert _nk789 == 71, "the block-7-9 key count is not 71 (got %d)" % _nk789',
         'assert _nk789 == 70, "the block-7-9 key count is not 70 (got %d)" % _nk789'),
        ('assert len(AUTO327) == 311, "the auto-327 entry list is not 311"',
         'assert len(AUTO327) == 307, "the auto-327 entry list is not 307 (4 boss-only removed in 101)"'),
        ('assert _nk327 == 327, "the auto-327 key count is not 327 (got %d)" % _nk327',
         'assert _nk327 == 323, "the auto-327 key count is not 323 (got %d)" % _nk327'),
):
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)
print("list counts re-based")

# ---------------------------------------------------------------- numeric re-base (assert lines only)
lines = s.split("\n")
n = {577: 0, 603: 0, 362: 0, 89: 0}
for i, ln in enumerate(lines):
    if not ("assert" in ln or "count(" in ln or "==" in ln):
        continue
    if re.search(r"(?<!\d)577(?!\d)", ln):
        n[577] += 1; ln = re.sub(r"(?<!\d)577(?!\d)", "573", ln)
    if re.search(r"(?<!\d)603(?!\d)", ln):
        n[603] += 1; ln = re.sub(r"(?<!\d)603(?!\d)", "599", ln)
    if re.search(r"(?<!\d)362(?!\d)", ln):
        n[362] += 1; ln = re.sub(r"(?<!\d)362(?!\d)", "360", ln)
    lines[i] = ln
s = "\n".join(lines)
print("re-based 577 x%d, 603 x%d, 362 x%d" % (n[577], n[603], n[362]))

for old, new in (
    ("""assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 89, \\""",
     """assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 86, \\"""),
):
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)

# ---------------------------------------------------------------- the new gates
anchor = "# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the"
assert s.count(anchor) == 1
GATE = '''# ---------------------------------------------------------------------------
# ROUND v101: the five boss-only removals and GATE OF KHORNE.
# ---------------------------------------------------------------------------
for _mk, _ky in (("grand_faiths_bastion", "wh_dlc06_quest_abilities_grand_faiths_bastion"),
                 ("bitter_sting", "wh3_dlc27_qb_unit_abilities_bitter_sting"),
                 ("frenzied_challenge", "wh3_dlc27_qb_unit_abilities_frenzied_challenge"),
                 ("visions_of_madness", "wh3_dlc27_qb_unit_abilities_visions_of_madness"),
                 ("guttural_roar", "wh3_dlc27_qb_unit_abilities_guttural_roar")):
    assert 'marker = "%s"' % _mk not in script_txt, "the boss-only marker is still in the table: " + _mk
    assert _ky not in script_txt, "the boss-only key is still in the script: " + _ky
    assert 'zz_auto_badge_%s"' % _mk not in script_txt, "the boss-only badge id is still in the script: " + _mk
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 86, \\
    "the enemy_engaged_or_shot count is not 86 (3 boss-only removed)"
assert script_txt.count('trigger = "melee_unwavering"') == 360, \\
    "the melee_unwavering count is not 360 (2 boss-only removed)"
assert script_txt.count("\\t{ marker = ") == 573, "the abilities table is not 573 entries"
# the ten boss-only keys that never shipped stay absent
for _ky in ("wh2_dlc10_quest_abilities_fiery_head", "wh2_dlc10_quest_abilities_regenerating_head",
            "wh_dlc08_quest_abilities_howling_winter", "wh_dlc08_quest_abilities_master_of_souls",
            "wh_dlc04_quest_abilities_servant_of_nagash", "wh3_dlc27_qb_unit_abilities_dissolving_bone",
            "wh3_dlc27_qb_unit_abilities_terrible_malice", "wh3_dlc27_qb_unit_abilities_copious_phlegm",
            "wh2_dlc10_quest_abilities_magic_fiery_convocation", "wh2_dlc10_quest_abilities_flame_storm"):
    assert _ky not in script_txt, "an excluded boss-only key is in the mod: " + _ky
# GATE OF KHORNE
GATE_KEY = "wh3_main_character_abilities_gate_of_khorne"
assert 'marker = "gate_of_khorne"' in script_txt, "the Gate of Khorne entry is missing"
assert 'trigger = "enemy_ground_melee"' in script_txt, "Gate of Khorne's trigger is missing"
assert '"%s"' % GATE_KEY in script_txt, "Gate of Khorne's key is missing"
assert '["%s"] = true,' % GATE_KEY in script_txt, "Gate of Khorne is not in enemy_ground_keys"
assert 'range_real = 50,' in script_txt, "Gate of Khorne's real 50 m range is missing"
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt, "the 70% 50 m constant (35) is missing"
assert "function FOURTH.evaluate_enemy_ground_melee(unit, routing)" in script_txt, \\
    "the melee-only enemy-ground evaluator is missing"
assert "enemy_ground_melee = FOURTH.evaluate_enemy_ground_melee," in script_txt, \\
    "the Gate of Khorne evaluator map entry is missing"
assert 'enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee' in script_txt, \\
    "the Gate of Khorne tooltip wording is missing"
assert "FOURTH.eg_melee_only = nil" in script_txt, "the melee-only flag slot/clear is missing"
assert script_txt.count("FOURTH.eg_melee_only = nil") >= 2, "the melee-only flag is not cleared in the poll"
assert "local melee_only = (FOURTH.eg_melee_only == true)" in script_txt, \\
    "the picker does not read the melee-only flag"
assert "local eg_melee_only_now = (FOURTH.eg_melee_only == true)" in script_txt, \\
    "the pre-cast re-check does not read the melee-only flag"
assert 'reason = "closest fighting (in-melee) enemy within bound (targeting "' in script_txt, \\
    "Gate of Khorne's own reason string is missing"
assert 'FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)' in script_txt, \\
    "the enemy-ground cast route is missing"
assert "unit_in_range(" not in script_txt, "a unit_in_range call is back in the script"

''' + anchor
s = s.replace(anchor, GATE, 1)
for old, new in (
    ("\"the melee_unwavering entry count is not 362 (Massacre removed)\"",
     "\"the melee_unwavering entry count is not 360 (Massacre + 2 boss-only removed)\""),
    ("\"the melee_unwavering count is not 362 (Massacre removed)\"",
     "\"the melee_unwavering count is not 360 (Massacre + 2 boss-only removed)\""),
    ("\"the enemy trigger count is not 89\"",
     "\"the enemy trigger count is not 86 (3 boss-only removed)\""),
    ("script_txt.count(\"\\t\\trange_real = \") == 98",
     "script_txt.count(\"\\t\\trange_real = \") == 96"),
    ("the 98 range_real fields", "the 96 range_real fields"),
    ("the range_real fields are not 98", "the range_real fields are not 96"),
    ("assert script_txt.count(\"\\t\\trange_real = \") == 98, \"the range_real fields are not 98\"",
     "assert script_txt.count(\"\\t\\trange_real = \") == 96, \"the range_real fields are not 96\""),
):
    s = s.replace(old, new)
print("messages updated")

io.open(OUT, "w", encoding="utf-8", newline="").write(s)
print("wrote", OUT, len(s), "bytes")
