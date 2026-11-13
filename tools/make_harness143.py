#!/usr/bin/env python3
"""Build harness143.lua from harness142.lua for round 144 (open batch 3: the rest of group C). Older harnesses are
never edited.

Pin rebases (code lines only; comment lines untouched; a rule with a guard only touches lines holding the guard):
  entries 712 -> 722, keys 767 -> 777 (10 entries / 10 keys), full-table iterations 1424 -> 1444,
  multi-use charge-gate keys 173 -> 176, wind-up keys 166 -> 169, melee_unwavering 307 -> 309,
  range_real fields 215 -> 217, ally_range_real 56 -> 57, enemy_fast_near_ally 7 -> 8; the tooltip mirror gains the
  five new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch2_harness142\harness142.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch3_harness143\harness143.lua"

BANNER = """-- ============================================================================
-- HARNESS 143 - ROUND 144: OPEN BATCH 3 (THE REST OF GROUP C).
--   10 new entries / 10 keys. NEW families self_last_stand, self_out_of_ammo,
--   health_aura_self_undead, ally_hurt_melee, enemy_wavering.
--   Edited vs harness142: this banner, the pin rebases listed in
--   tools/make_harness143.py, the tooltip mirror, run_h143 and its call.
--   RED control: H143_LIVE / H143_ANN on docs/backups/round144/pre144_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 143 (round 144): OPEN BATCH 3.
--   HD1 Hag's Denial at 8% health in melee -> ONE cast on self. HD2 at 8% neither
--   in melee nor under fire -> none. HD3 at 20% in melee -> none. HD4 at 8% under
--   missile fire -> ONE cast.
--   RS1 Ruinshelter in melee -> ONE cast. BH1 Banner of Hellfire in melee -> ONE.
--   RB1 Rock Bottom with no ammunition left -> ONE cast. RB2 with 5 left -> none.
--   MK1 Morikhane under fire -> ONE cast. MK2 not under fire -> none.
--   HC1 Hunter's Call: an ally 20 m away in melee (bound 24 m) -> ONE cast on self.
--   IK1 Icon of the King: an UNDEAD ally 20 m away at 50% -> ONE cast on self.
--   IK2 a LIVING ally at 50% -> none.
--   GS1 The Gold Standard: an ally 30 m away at 50% IN MELEE -> ONE cast ON it.
--   GS2 the same ally not in melee -> none.
--   GH1 Ghostly Howl: a WAVERING enemy 30 m away -> ONE cast on it. GH2 the
--   enemy is not wavering -> none.
--   PG1 Petrifying Gaze: an enemy moving at 8 m/s, 20 m away -> ONE cast on it.
--   RED (pre-144 = round 143): HD1, RB1, IK1, GS1, GH1 cast nothing.
-- ============================================================================
function run_h143()
  local L143 = os.getenv("H143_LIVE") or LIVE
  local A143 = os.getenv("H143_ANN") or ANN
  local RED143 = (os.getenv("H143_LIVE") ~= nil) or (os.getenv("H143_ANN") ~= nil)
  local HD = "wh3_dlc24_unit_abilities_hags_denial"
  local RS = "wh2_dlc15_unit_abilities_mimic_ruinshelter"
  local RB = "wh2_dlc15_unit_abilities_rock_bottom"
  local MK = "wh3_dlc29_item_abilities_morikhane_the_black_armour"
  local HC = "wh2_dlc13_character_ability_hunters_call"
  local IK = "wh3_dlc29_item_abilities_icon_of_the_king"
  local GS = "wh3_dlc25_item_abilities_the_gold_standard"
  local BH = "wh3_main_banner_abilities_banner_of_hellfire"
  local GH = "wh3_dlc29_hero_active_ghostly_howl"
  local PG = "wh3_dlc24_unit_passive_petrifying_gaze"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local LIVING = "wh_main_emp_inf_swordsmen"
  local ZOMB = "wh_main_vmp_inf_zombie"
  local pre143 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 143 - section 0zo: the round-144 tokens ==")
  if not RED143 then
    for _, f in ipairs({ { name = "live", path = L143 }, { name = "ann", path = A143 } }) do
      local s = read_file(f.path)
      check("0zo " .. f.name .. ": 722 entries; the 10 new markers; the five new families and both re-check modes",
        cp(s, "\t{ marker = ") == 722
        and raw_find(s, '{ marker = "hags_denial", name = "Hag\'s Denial", trigger = "self_last_stand",', 1, true) ~= nil
        and raw_find(s, '{ marker = "ruinshelter", name = "Ruinshelter", trigger = "melee_unwavering",', 1, true) ~= nil
        and raw_find(s, '{ marker = "rock_bottom", name = "Rock Bottom", trigger = "self_out_of_ammo",', 1, true) ~= nil
        and raw_find(s, '{ marker = "morikhane", name = "Morikhane, the Black Armour", trigger = "under_fire",', 1, true) ~= nil
        and raw_find(s, '{ marker = "hunters_call", name = "Hunter\'s Call", trigger = "melee_or_wavering_aura",', 1, true) ~= nil
        and raw_find(s, '{ marker = "icon_of_the_king", name = "Icon of the King", trigger = "health_aura_self_undead",', 1, true) ~= nil
        and raw_find(s, '{ marker = "the_gold_standard", name = "The Gold Standard", trigger = "ally_hurt_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "banner_of_hellfire", name = "Banner of Hellfire", trigger = "melee_unwavering",', 1, true) ~= nil
        and raw_find(s, '{ marker = "ghostly_howl", name = "Ghostly Howl", trigger = "enemy_wavering",', 1, true) ~= nil
        and raw_find(s, '{ marker = "petrifying_gaze", name = "Petrifying Gaze", trigger = "enemy_fast_near_ally",', 1, true) ~= nil
        and raw_find(s, "FOURTH.LAST_STAND_PCT = 10", 1, true) ~= nil
        and raw_find(s, 'elseif eg_mode_now == "wavering" then', 1, true) ~= nil
        and raw_find(s, 'if FOURTH.ah_mode == "melee" then', 1, true) ~= nil
        and raw_find(s, 'if FOURTH.ah_mode == "undead" then', 1, true) ~= nil
        and raw_find(s, "self_last_stand = FOURTH.evaluate_self_last_stand,", 1, true) ~= nil
        and raw_find(s, "self_out_of_ammo = FOURTH.evaluate_self_out_of_ammo,", 1, true) ~= nil
        and raw_find(s, "health_aura_self_undead = FOURTH.evaluate_health_aura_self_undead,", 1, true) ~= nil
        and raw_find(s, "ally_hurt_melee = FOURTH.evaluate_ally_hurt_melee,", 1, true) ~= nil
        and raw_find(s, "enemy_wavering = FOURTH.evaluate_enemy_wavering,", 1, true) ~= nil
        and raw_find(s, "wh2_dlc15_unit_abilities_rock_bottom", 1, true) ~= nil
        and raw_find(s, "wh_dlc05_unit_abilities_storm_of_blades", 1, true) == nil
        and raw_find(s, "wh2_dlc16_unit_abilities_whirling_death", 1, true) == nil
        and raw_find(s, "wh2_dlc09_item_abilities_cloak_of_the_dunes", 1, true) == nil)
    end
  end

  local FILES = { { path = A143, tag = "[annotated] " }, { path = L143, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, arm, key, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- the caster alone (cdef overrides its fields), one idle enemy far away
  local function solo(b, key, cdef)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 300 }
    for k, v in pairs(cdef or {}) do c[k] = v end
    return { c }, { { uid = b + 5, name = LIVING, melee = false } }
  end
  -- the caster and one ally adef at gap metres
  local function pair(b, key, gap, adef)
    local a = { uid = b + 1, name = LIVING, owns = {}, melee = false }
    for k, v in pairs(adef or {}) do a[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = 300, dist_by_target = { [b + 1] = gap } }, a },
      { { uid = b + 5, name = LIVING, melee = false } }
  end
  -- the caster at cdist from one enemy edef
  local function foe(b, key, cdist, edef)
    local e = { uid = b + 5, name = LIVING, melee = false }
    for k, v in pairs(edef or {}) do e[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = cdist } }, { e }
  end
  -- name, builder(b), marker, key, GREEN casts, RED (nil = not RED), target: self / ally / enemy / nil
  local WORLDS = {
    { "HD1. Hag's Denial: 8% health in melee -> ONE cast on self",
      function(b) return solo(b, HD, { health_percent = 8, melee = true }) end, "hags_denial", HD, 1, 0, "self" },
    { "HD2. Hag's Denial: 8% health, neither in melee nor under fire -> no cast",
      function(b) return solo(b, HD, { health_percent = 8 }) end, "hags_denial", HD, 0, nil, nil },
    { "HD3. Hag's Denial: 20% health in melee -> no cast",
      function(b) return solo(b, HD, { health_percent = 20, melee = true }) end, "hags_denial", HD, 0, nil, nil },
    { "HD4. Hag's Denial: 8% health under missile fire -> ONE cast on self",
      function(b) return solo(b, HD, { health_percent = 8, missile = true }) end, "hags_denial", HD, 1, nil, "self" },
    { "RS1. Ruinshelter: in melee -> ONE cast on self",
      function(b) return solo(b, RS, { melee = true }) end, "ruinshelter", RS, 1, nil, "self" },
    { "BH1. Banner of Hellfire: in melee -> ONE cast on self",
      function(b) return solo(b, BH, { melee = true }) end, "banner_of_hellfire", BH, 1, nil, "self" },
    { "RB1. Rock Bottom: no ammunition left -> ONE cast on self",
      function(b) return solo(b, RB, { ammo_start = 20, ammo_seq = { 0 } }) end, "rock_bottom", RB, 1, 0, "self" },
    { "RB2. Rock Bottom: 5 shots left -> no cast",
      function(b) return solo(b, RB, { ammo_start = 20, ammo_seq = { 5 } }) end, "rock_bottom", RB, 0, nil, nil },
    { "MK1. Morikhane: under missile fire -> ONE cast on self",
      function(b) return solo(b, MK, { missile = true }) end, "morikhane", MK, 1, nil, "self" },
    { "MK2. Morikhane: not under fire -> no cast",
      function(b) return solo(b, MK, {}) end, "morikhane", MK, 0, nil, nil },
    { "HC1. Hunter's Call: an ally 20 m away in melee (bound 24 m) -> ONE cast on self",
      function(b) return pair(b, HC, 20, { melee = true }) end, "hunters_call", HC, 1, nil, "self" },
    { "IK1. Icon of the King: an UNDEAD ally 20 m away at 50% -> ONE cast on self",
      function(b) return pair(b, IK, 20, { name = ZOMB, health_percent = 50 }) end, "icon_of_the_king", IK, 1, 0, "self" },
    { "IK2. Icon of the King: a LIVING ally at 50% -> no cast",
      function(b) return pair(b, IK, 20, { health_percent = 50 }) end, "icon_of_the_king", IK, 0, nil, nil },
    { "GS1. The Gold Standard: an ally 30 m away at 50% IN MELEE -> ONE cast ON it",
      function(b) return pair(b, GS, 30, { health_percent = 50, melee = true }) end, "the_gold_standard", GS, 1, 0, "ally" },
    { "GS2. The Gold Standard: the hurt ally is not in melee -> no cast",
      function(b) return pair(b, GS, 30, { health_percent = 50 }) end, "the_gold_standard", GS, 0, nil, nil },
    { "GH1. Ghostly Howl: a WAVERING enemy 30 m away -> ONE cast on it",
      function(b) return foe(b, GH, 30, { wavering = true }) end, "ghostly_howl", GH, 1, 0, "enemy" },
    { "GH2. Ghostly Howl: the enemy is not wavering -> no cast",
      function(b) return foe(b, GH, 30, { wavering = false }) end, "ghostly_howl", GH, 0, nil, nil },
    { "PG1. Petrifying Gaze: an enemy moving at 8 m/s 20 m away -> ONE cast on it",
      function(b) return foe(b, PG, 20, { moving = true, fast_speed = 8 }) end, "petrifying_gaze", PG, 1, nil, "enemy" },
    { "PG2. Petrifying Gaze: the enemy stands still -> no cast",
      function(b) return foe(b, PG, 20, { moving = false, fast_speed = 8 }) end, "petrifying_gaze", PG, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED143 then want = w[6] end
      if want ~= nil then
        local base = 15300 + i * 20
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG)
        if W ~= nil then
          local got, gground, last = 0, 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then gground = gground + 1 end end
          local total = got + gground
          local a = (total == want)
          if a and not RED143 and total >= 1 then
            local tid = nil
            if last ~= nil and last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
            if w[7] == "ally" then
              a = (gground == 0 and tid == tostring(base + 1))
            elseif w[7] == "enemy" then
              a = (gground == 0 and tid == tostring(base + 5))
            elseif w[7] == "self" then
              a = (gground == 0 and (tid == nil or tid == tostring(base)))
            end
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED143 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. total .. ((w[7] ~= nil and not RED143) and (" (on " .. w[7] .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED143 then
    check("RED CONTROL (harness 143): the pre-144 build has none of the batch-3 entries - "
      .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  else
    check("HARNESS 143: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 38 and n_ok == 38)
  end
  print("== HARNESS 143 done: " .. (checks - pre143) .. " checks in this section ==")
end
'''

# (regex, replacement, guard substring or None)
PIN_RULES = [
    (r"== 712\b", "== 722", None),
    (r"== 767\b", "== 777", None),
    (r"it == 1424\b", "it == 1444", None),
    (r"entries = 712, keys = 767", "entries = 722, keys = 777", None),
    (r"want 712\b", "want 722", None),
    (r"FULL 712-entry table", "FULL 722-entry table", None),
    (r"712 abilities per pass", "722 abilities per pass", None),
    (r"table of 712 after round 143", "table of 722 after round 144", None),
    (r"\(12 air-drop entries of 712\)", "(12 air-drop entries of 722)", None),
    (r"\(RED_MODE and 0 or 173\)", "(RED_MODE and 0 or 176)", None),
    (r"\) == 307\b", ") == 309", "melee_unwavering"),
    (r"mu == 307\b", "mu == 309", None),
    (r"mu = 307,", "mu = 309,", "EXP = { entries = 722"),
    (r"entries = 712, keys = 767,", "entries = 722, keys = 777,", "EXP = {"),
    (r"== 215\)", "== 217)", "range_real = \")"),
    (r"\(EXP\.sum and 215 or 96\)", "(EXP.sum and 217 or 96)", None),
    (r"nkeys == 166\b", "nkeys == 169", None),
    (r"== 56\b", "== 57", "ally_range_real = \")"),
    (r"== 7\b", "== 8", "trigger = \"enemy_fast_near_ally\"') =="),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b, guard in PIN_RULES:
        if guard is not None and guard not in new:
            continue
        new2, n = re.subn(a, b, new)
        if n:
            hits[a] += n
            new = new2
    if new != ln:
        changed.append(i + 1)
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
TIP_OLD = ('    enemy_ground_shooting = "When armed, fires on the ground under the closest enemy missile unit in range '
           'that is shooting",\n')
TIP_NEW = TIP_OLD + (
    '    self_last_stand = "When armed, fires when this unit is at 10% health or less while in melee or under fire",\n'
    '    self_out_of_ammo = "When armed, fires when this unit has no ammunition left",\n'
    '    health_aura_self_undead = "When armed, fires when this unit or a non-living friendly unit in its aura is hurt",\n'
    '    ally_hurt_melee = "When armed, fires on the most hurt friendly unit in range that is in melee",\n'
    '    enemy_wavering = "When armed, fires on the closest wavering enemy in range",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h141()\nrun_h142()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h143()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
