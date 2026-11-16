#!/usr/bin/env python3
"""Build harness164.lua from harness163.lua for round 165 (the night audit). Older harnesses are never edited.

Rebases (each one a world the round-165 rules now treat differently, as the game does):
  * harness 83 S1 (the 27 simple in-melee entries): the Eye of the Storm unit is now the Storm Dragon
    (wh3_main_cth_cha_storm_dragon_1, its real owner): the game refuses the ability unless the caster is large
    (unit_is_not_large), and a mock unit named 'b2_eye_of_the_storm' is not in the large set.
  * harness 142 DJ1 (Curse of Djaf): the caster stands at 40% health: the game refuses the curse above 50%
    (health_above_50%), so a full-health caster no longer casts.
  * harness 160 HH1 (Helping Hand, default armed): its only ally is a Swordsmen block; the game allows only a Lord or
    Hero as the target (unit_is_not_commander_class): GREEN 1 -> 0. The positive case is harness 164 AT2.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_breaths_harness163\harness163.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\harness164.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h164_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 164 - ROUND 165: THE NIGHT AUDIT (the card on every M/A badge, the
--   game's caster and ally target rules, the WW ground cast).
--   Edited vs harness163: this banner, the three world rebases listed in
--   tools/make_harness164.py (S1 Eye of the Storm, DJ1, HH1), run_h164 and its
--   call. RED control: H164_LIVE / H164_ANN on docs/backups/round165/pre165_*.lua.
-- ============================================================================
"""
R = [
    ('      units[i] = { name = "b2_" .. marker, uid = 9100 + i, owns = { key }, melee = true, wavering = false }\n',
     '      -- HARNESS 164: Eye of the Storm needs a large caster (the game\'s unit_is_not_large rule): its real owner\n'
     '      units[i] = { name = (key == "wh3_main_lord_abilities_eye_of_the_storm") and "wh3_main_cth_cha_storm_dragon_1"\n'
     '        or ("b2_" .. marker), uid = 9100 + i, owns = { key }, melee = true, wavering = false }\n'),
    ('    { "DJ1. Curse of Djaf: enemy handgunners shooting 30 m away, not in melee -> ONE ground cast under them",\n'
     '      function(b) return one(b, DJ, 30, { name = GUNS, melee = false, ammo_start = 100, ammo_seq = DROPS }) end,\n',
     '    { "DJ1. Curse of Djaf (caster at 40%: refused above 50%): enemy handgunners shooting 30 m away -> ONE ground cast",\n'
     '      function(b)\n'
     '        local u, e = one(b, DJ, 30, { name = GUNS, melee = false, ammo_start = 100, ammo_seq = DROPS })\n'
     '        u[1].hp_frac = 0.4   -- HARNESS 164: the game refuses the curse above 50% health\n'
     '        return u, e\n'
     '      end,\n'),
    ('    { "HH1. Helping Hand, no badge click, in melee with an ally -> ONE cast", HH, "helping_hand", 0, 1, 0 },\n',
     '    { "HH1. Helping Hand, no badge click, in melee with a Swordsmen ally -> no cast (Lords and Heroes only, round 165)",\n'
     '      HH, "helping_hand", 0, 0, 0 },\n'),
]
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h163()\n") == 1
src = src.replace("\nrun_h163()\n", "\nrun_h163()\nrun_h164()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
