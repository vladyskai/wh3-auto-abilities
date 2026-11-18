#!/usr/bin/env python3
"""Build harness173.lua from harness172.lua for round 174 (the score 1-2 review, rows 24-50). Older harnesses are
never edited.

Rebases (every one follows the user's 'You may implement items 24 to 50'; old -> new, why):
  * family counts moved by the 27 entries: enemy_engaged_or_shot 46 -> 37 (9 left), enemy_ground_area 9 -> 6 (3 left),
    ally_melee_buff 14 -> 11, enemy_melee 35 -> 34 (Transfix), target_class fields 56 -> 58 (Silence the Prey, Power
    Siphon), enemy_blob 77 -> 71, enemy_large_shot 5 -> 7, enemy_single_drain 10 -> 12, enemy_commander_value 3 -> 5,
    ally_overseer / ally_beast / ally_broken 1 -> 0 and ally_missile 3 -> 0 (their entries moved);
  * h93 TIP mirror: the 13 round-174 labels;
  * h97 FAM 'INSIDE/BEYOND r500' (Trickster's Shard): the enemy is a spellcaster (Arkhan) since the shard now targets
    enemy spellcasters;
  * h99 CG1 Whiplash: the beast ally has just made contact; CG4 Overseer: the ally is in melee at 40% health; CG9 Inspired
    Marksmanship: a missile ally that is NOT shooting now stays silent (the shooting world is h173 IM1); RM1 Fury of
    Khaine: the ally has just made contact; RM2 Verminous Fury: the ally is in melee and wavering;
  * h122 E-worlds: Transfix left enemy_melee (its worlds are h173 TX1/TX2): 66 worlds instead of 76; its 0s token check
    reads its new family;
  * h131 O2 Overseer: the eligible ally is in melee and wavering;
  * h165 SC2: Helping Hand's card is 'Fires on the nearest ally in melee; Lord or Hero allies only'.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_close_two_harness172\harness172.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_review_rows_harness173\harness173.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h173_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 173 - ROUND 174: THE SCORE 1-2 REVIEW, ROWS 24-50 (13 new families, the
--   spellcaster class, 27 entries moved).
--   Edited vs harness172: this banner, the rebases listed in tools/make_harness173.py,
--   run_h173 and its call.
--   RED control: H173_LIVE / H173_ANN on docs/backups/round174/pre174_*.lua.
-- ============================================================================
"""
LABELS = (
    '    enemy_large_value_shot = "When armed, fires at the most valuable large enemy, else at the most valuable enemy infantry per soldier",\n'
    '    enemy_spellcaster = "When armed, fires at the most valuable visible enemy spellcaster in range",\n'
    '    enemy_ground_spellcasters = "When armed, fires on the ground under the enemy spellcaster with the most other spellcasters near it",\n'
    '    enemy_missile_value = "When armed, fires at the most valuable enemy missile unit that is shooting",\n'
    '    enemy_ground_shooters = "When armed, fires on the ground under the shooting enemy with the most shooting value near it",\n'
    '    enemy_commander_wavering = "When armed, fires at a wavering or routing enemy Lord or Hero, one in melee first",\n'
    '    ally_charge_melee = "When armed, fires on the nearest charging ally, else one that just made contact, never a missile unit",\n'
    '    ally_wavering_melee = "When armed, fires on the most valuable wavering ally in melee, never a missile unit",\n'
    '    ally_lord_melee = "When armed, fires on the nearest Lord or Hero ally in melee",\n'
    '    ally_missile_shooting = "When armed, fires on the most valuable missile ally that is shooting",\n'
    '    ally_melee_risk = "When armed, fires on the most valuable ally in melee that wavers or is at or below 50% health",\n'
    '    ally_beast_charge = "When armed, fires on the nearest charging beast ally, else one that just made contact",\n'
    '    ally_routing = "When armed, fires on the most valuable routing ally",\n')
R = [
    # h93 TIP mirror: the 13 round-174 labels
    ('    aura_charge = "When armed, fires when this unit or a unit in its aura charges, has just made contact, or wavers",\n',
     '    aura_charge = "When armed, fires when this unit or a unit in its aura charges, has just made contact, or wavers",\n'
     '    -- HARNESS 173: the round-174 labels\n' + LABELS, 1),
    # the family counts
    ("""'trigger = "enemy_engaged_or_shot"') == 46""", """'trigger = "enemy_engaged_or_shot"') == 37""", 5),
    ("mu = 280, es = 46,", "mu = 280, es = 37,", 1),
    ("""'trigger = "enemy_ground_area"') == 9""", """'trigger = "enemy_ground_area"') == 6""", 3),
    ("""'trigger = "ally_melee_buff"') == 14""", """'trigger = "ally_melee_buff"') == 11""", 2),
    ("""'trigger = "enemy_melee"') == 35""", """'trigger = "enemy_melee"') == 34""", 3),
    ('"\\t\\ttarget_class = ") == 56', '"\\t\\ttarget_class = ") == 58', 3),
    ("""'trigger = "enemy_blob"') == 77""", """'trigger = "enemy_blob"') == 71""", 1),
    ("""'trigger = "enemy_large_shot"') == 5""", """'trigger = "enemy_large_shot"') == 7""", 1),
    ("""'trigger = "enemy_single_drain"') == 10""", """'trigger = "enemy_single_drain"') == 12""", 1),
    ("""'trigger = "enemy_commander_value"') == 3""", """'trigger = "enemy_commander_value"') == 5""", 2),
    ("""cp99(s, 'trigger = "ally_overseer"') == 1""", """cp99(s, 'trigger = "ally_overseer"') == 0""", 1),
    ("""cp99(s, 'trigger = "ally_beast"') == 1""", """cp99(s, 'trigger = "ally_beast"') == 0""", 1),
    ("""cp99(s, 'trigger = "ally_broken"') == 1""", """cp99(s, 'trigger = "ally_broken"') == 0""", 1),
    ("""cp99(s, 'trigger = "ally_missile"') == 3""", """cp99(s, 'trigger = "ally_missile"') == 0""", 1),
    # h97: the Trickster's Shard targets enemy spellcasters now
    ('      enemies = { { name = (FAM_.marker == "headhunt") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true,\n',
     '      -- HARNESS 173: the Trickster\'s Shard targets enemy spellcasters (round 174): Arkhan is one\n'
     '      enemies = { { name = (FAM_.marker == "headhunt" or FAM_.marker == "tricksters_shard") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true,\n', 1),
    ('      enemies = { { name = (FAM_.marker == "headhunt" or FAM_.marker == "tricksters_shard") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true,\n',
     '      enemies = { { name = (FAM_.marker == "headhunt" or FAM_.marker == "tricksters_shard") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true,\n'
     '                    pos = (FAM_.marker == "tricksters_shard") and { 0, 0, 100 } or nil,   -- HARNESS 173: the map needs a position\n'
     '                    width = (FAM_.marker == "tricksters_shard") and 6 or nil,\n', 1),
    ('    if FAM_.marker == "entangle" then\n      local e = enemy_of97(W, euid)\n',
     '    if FAM_.marker == "tricksters_shard" then   -- HARNESS 173: the enemy map reads only visible enemies\n'
     '      W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end\n'
     '      local e = enemy_of97(W, euid)\n'
     '      if e ~= nil then e.is_visible_to_alliance = function() return true end end\n'
     '    end\n'
     '    if FAM_.marker == "entangle" then\n      local e = enemy_of97(W, euid)\n', 1),
    # the suite boundaries after h99: CG9 now makes ONE check per file instead of two (2 fewer in all)
    ('.. pre102 .. ", want 3435)", pre102 == 3435)', '.. pre102 .. ", want 3433)", pre102 == 3433)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre103 .. ", want 3518)", pre103 == 3518)', '.. pre103 .. ", want 3516)", pre103 == 3516)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre104 .. ", want 3562)", pre104 == 3562)', '.. pre104 .. ", want 3560)", pre104 == 3560)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre105 .. ", want 3643)", pre105 == 3643)', '.. pre105 .. ", want 3641)", pre105 == 3641)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre106 .. ", want 3695)", pre106 == 3695)', '.. pre106 .. ", want 3693)", pre106 == 3693)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre107 .. ", want 3805)", pre107 == 3805)', '.. pre107 .. ", want 3803)", pre107 == 3803)   -- HARNESS 173: CG9 -2', 1),
    ('.. pre114 .. ", want 4482)", pre114 == 4482)', '.. pre114 .. ", want 4480)", pre114 == 4480)   -- HARNESS 173: CG9 -2', 1),
    ('      .. pre115 .. ")", pre115 == 4604)', '      .. pre115 .. ")", pre115 == 4602)   -- HARNESS 173: CG9 -2', 1),
    ("(pre116 == 4676))", "(pre116 == 4674))   -- HARNESS 173: CG9 -2", 1),
    ("(pre117 == 4692))", "(pre117 == 4690))   -- HARNESS 173: CG9 -2", 1),
    ("(pre118 == 4708))", "(pre118 == 4706))   -- HARNESS 173: CG9 -2", 1),
    # h149 0zr: Shem's Burning Gaze (the blast table's last row) left enemy_blob; Fireball is now the last row
    ('        and raw_find(s, "wh_main_spell_bound_fireball=5;", 1, true) ~= nil\n',
     '        and raw_find(s, "wh_main_spell_bound_fireball=5\\"", 1, true) ~= nil   -- HARNESS 173: now the last row\n', 1),
    # h99: the moved ally entries' worlds meet their new rules
    ('    key = K.whip, marker = "whiplash", cuid = 9701, allies = { { name = BEAST, uid = 9702, dist = 30 } },\n',
     '    key = K.whip, marker = "whiplash", cuid = 9701, allies = { { name = BEAST, uid = 9702, dist = 30, melee = true } },   -- HARNESS 173: just made contact\n', 1),
    ('    key = K.over, marker = "overseer_of_the_unseen", cuid = 9707, allies = { { name = PLAIN, uid = 9708, dist = 30 } },\n',
     '    key = K.over, marker = "overseer_of_the_unseen", cuid = 9707, allies = { { name = PLAIN, uid = 9708, dist = 30, melee = true, hp = 40 } },   -- HARNESS 173: in melee at 40%\n', 1),
    ('  add(function(P, T) return world_cg(P, T, { wname = "CG9: Inspired Marksmanship CASTS ON A MISSILE-CAPABLE ally",\n'
     '    key = K.mark, marker = "inspired_marksmanship_i", cuid = 9717, allies = { { name = MISS, uid = 9718, dist = 30 } },\n'
     '    expect = "fire_ally", target = 9718 }) end)\n',
     '  -- HARNESS 173: Inspired Marksmanship waits for a SHOOTING missile ally (round 174); the firing world is h173 IM1\n'
     '  add(function(P, T) return world_cg(P, T, { wname = "CG9: Inspired Marksmanship stays SILENT on a missile ally that is not shooting",\n'
     '    key = K.mark, marker = "inspired_marksmanship_i", cuid = 9717, allies = { { name = MISS, uid = 9718, dist = 30 } },\n'
     '    expect = "silent" }) end)\n', 1),
    ('    allies = { { name = PLAIN, uid = 9740, dist = 20 } }, expect = "fire_ally", target = 9740 }) end)\n',
     '    allies = { { name = PLAIN, uid = 9740, dist = 20, melee = true } }, expect = "fire_ally", target = 9740 }) end)   -- HARNESS 173: just made contact\n', 1),
    ('    allies = { { name = PLAIN, uid = 9742, dist = 60 } }, expect = "fire_ally", target = 9742 }) end)\n',
     '    allies = { { name = PLAIN, uid = 9742, dist = 60, melee = true, wavering = true } }, expect = "fire_ally", target = 9742 }) end)   -- HARNESS 173: wavering in melee\n', 1),
    # h122: Transfix left enemy_melee
    ('      check("0s " .. nm .. ": " .. b[1] .. " is on enemy_melee with its badge and key", entry_ok(b[1], b[2], "enemy_melee"))\n',
     '      -- HARNESS 173: Transfix rides enemy_commander_wavering since round 174\n'
     '      local trig173 = (b[1] == "transfix_hex") and "enemy_commander_wavering" or "enemy_melee"\n'
     '      check("0s " .. nm .. ": " .. b[1] .. " is on " .. trig173 .. " with its badge and key", entry_ok(b[1], b[2], trig173))\n', 1),
    ('  -- E: enemy_melee, cast at the enemy\n  for i, b in ipairs(EM) do\n',
     '  -- E: enemy_melee, cast at the enemy\n'
     '  -- HARNESS 173: Transfix left enemy_melee (round 174); its worlds are run_h173\'s TX1 / TX2\n'
     '  local EMW = {}\n'
     '  for _, b in ipairs(EM) do if b[1] ~= "transfix_hex" then EMW[#EMW + 1] = b end end\n'
     '  for i, b in ipairs(EMW) do\n', 1),
    ('    check("HARNESS 122: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 76 and n_ok == 76)\n',
     '    check("HARNESS 122: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 66 and n_ok == 66)   -- HARNESS 173: 76 - Transfix\'s 10\n', 1),
    # h131 O2: the Overseer's ally is in melee and wavering
    ('      local Wo2 = world("O2. Overseer of the Unseen: the eligible ally is not flying -> ONE cast on it",\n'
     '        { caster(13321, OK_), { name = PLAIN, uid = 13322, owns = {}, melee = false, dist = 30 } },\n',
     '      -- HARNESS 173: the Overseer waits for an ally in melee that wavers or is hurt (round 174)\n'
     '      local Wo2 = world("O2. Overseer of the Unseen: the eligible ally is not flying -> ONE cast on it",\n'
     '        { caster(13321, OK_), { name = PLAIN, uid = 13322, owns = {}, melee = true, wavering = true, dist = 30 } },\n', 1),
    # h165 SC2: Helping Hand's card
    ('        and by.helping_hand == "Fires in melee unless wavering, on the nearest ally in range; Lord or Hero allies only"\n',
     '        and by.helping_hand == "Fires on the nearest ally in melee; Lord or Hero allies only"   -- HARNESS 173\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h172()\n") == 1
src = src.replace("\nrun_h172()\n", "\nrun_h172()\nrun_h173()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
