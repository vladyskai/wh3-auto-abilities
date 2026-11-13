#!/usr/bin/env python3
"""Build harness142.lua from harness141.lua for round 143 (open batch 2: the ground curses, Curse of Djaf, the
Handmaidens' Soulblight, Squig Thinkin' and the two fanatic releases). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched; a rule with a guard only touches lines holding the guard):
  entries 703 -> 712, keys 756 -> 767 (9 entries / 11 keys added), full-table iterations 1406 -> 1424,
  multi-use charge-gate keys 169 -> 173, melee_unwavering 306 -> 307 (the Handmaidens' Soulblight),
  enemy_ground_melee 67 -> 74 (seven entries); the harness-93 tooltip mirror gains the new wording.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch1_harness141\harness141.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch2_harness142\harness142.lua"

BANNER = """-- ============================================================================
-- HARNESS 142 - ROUND 143: OPEN BATCH 2 (GROUND CURSES, CURSE OF DJAF,
--   SOULBLIGHT, SQUIG THINKIN', THE FANATIC RELEASES).
--   9 new entries / 11 keys. NEW family enemy_ground_shooting; the new 25 m
--   bound FOURTH.ENEMY_CAST_R25 = 17.
--   Edited vs harness141: this banner, the pin rebases listed in
--   tools/make_harness142.py, the tooltip mirror, run_h142 and its call.
--   RED control: H142_LIVE / H142_ANN on docs/backups/round143/pre143_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 142 (round 143): OPEN BATCH 2.
--   AN1 The Curse of Anraheir: an enemy in melee 30 m away -> ONE GROUND cast
--   under it. AN2 the enemy is not fighting -> none. TL1 Transmutation of Lead,
--   SB1 Soulblight (Doomfire), SS1 The Soulstealer, SQ1 Squig Thinkin': an
--   enemy in melee inside the bound -> ONE ground cast under it.
--   DJ1 Curse of Djaf: enemy handgunners shooting 30 m away -> ONE ground cast
--   under them. DJ2 a fighting non-missile enemy -> none.
--   HM1 Soulblight (Handmaidens): the unit in melee -> ONE cast on self. HM2 not
--   in melee -> none.
--   LO1 Spinning Loons: an enemy in melee 10 m away (bound 17 m) -> ONE ground
--   cast. LO2 the enemy 25 m away -> none. LO3 the enemy is flying -> none.
--   LE1 The Loons of Eight Peaks = LO1.
--   RED (pre-143 = round 142): AN1, DJ1, HM1, LO1 cast nothing.
-- ============================================================================
function run_h142()
  local L142 = os.getenv("H142_LIVE") or LIVE
  local A142 = os.getenv("H142_ANN") or ANN
  local RED142 = (os.getenv("H142_LIVE") ~= nil) or (os.getenv("H142_ANN") ~= nil)
  local AN = "wh3_main_spell_bound_the_curse_of_anraheir"
  local TL = "wh3_main_spell_bound_transmutation_of_lead"
  local SB = "wh2_dlc10_spell_bound_soulblight"
  local SS = "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer"
  local DJ = "wh2_dlc09_character_abilities_curse_of_djaf"
  local HM = "wh3_dlc29_spell_bound_soulblight"
  local SQ = "wh3_dlc26_character_abilities_squig_thinkin"
  local LO = "wh_main_unit_abilities_spinning_loons"
  local LE = "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local LIVING = "wh_main_emp_inf_swordsmen"
  local GUNS = "wh_main_emp_inf_handgunners"
  local pre142 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 142 - section 0zn: the round-143 tokens ==")
  if not RED142 then
    for _, f in ipairs({ { name = "live", path = L142 }, { name = "ann", path = A142 } }) do
      local s = read_file(f.path)
      check("0zn " .. f.name .. ": 712 entries; the 9 new markers; the 25 m bound; the new family wired",
        cp(s, "\t{ marker = ") == 712
        and raw_find(s, '{ marker = "curse_of_anraheir", name = "The Curse of Anraheir", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "transmutation_of_lead", name = "Transmutation of Lead", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "soulblight", name = "Soulblight", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "the_soulstealer", name = "The Soulstealer", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "curse_of_djaf", name = "Curse of Djaf", trigger = "enemy_ground_shooting",', 1, true) ~= nil
        and raw_find(s, '{ marker = "soulblight_handmaidens", name = "Soulblight", trigger = "melee_unwavering",', 1, true) ~= nil
        and raw_find(s, '{ marker = "squig_thinkin", name = "Squig Thinkin\'", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, '{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_ground_melee",', 1, true) ~= nil
        and raw_find(s, "FOURTH.ENEMY_CAST_R25  = 17", 1, true) ~= nil
        and raw_find(s, "\t[25]  = FOURTH.ENEMY_CAST_R25,", 1, true) ~= nil
        and raw_find(s, "function FOURTH.evaluate_enemy_ground_shooting(unit, routing)", 1, true) ~= nil
        and raw_find(s, "enemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting,", 1, true) ~= nil
        and raw_find(s, '["wh2_dlc09_character_abilities_curse_of_djaf"] = true,', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A142, tag = "[annotated] " }, { path = L142, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function enemy_unit(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG, fly)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for _, e in ipairs(enemies or {}) do
      local u = enemy_unit(W, e.uid)
      if u ~= nil then
        local b = (fly == true)
        u.is_currently_flying = function() return b end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- the caster at cdist from one enemy (edef overrides the enemy's fields)
  local function one(b, key, cdist, edef)
    local e = { uid = b + 5, name = LIVING, melee = true }
    for k, v in pairs(edef or {}) do e[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = cdist } }, { e }
  end
  local DROPS = { 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80 }
  -- name, builder(b), marker, key, GREEN casts, RED (nil = not RED), flying enemy, where: ground / self / nil
  local WORLDS = {
    { "AN1. The Curse of Anraheir: an enemy in melee 30 m away -> ONE ground cast under it",
      function(b) return one(b, AN, 30) end, "curse_of_anraheir", AN, 1, 0, false, "ground" },
    { "AN2. The Curse of Anraheir: the enemy is not fighting -> no cast",
      function(b) return one(b, AN, 30, { melee = false }) end, "curse_of_anraheir", AN, 0, nil, false, nil },
    { "TL1. Transmutation of Lead: an enemy in melee 30 m away -> ONE ground cast under it",
      function(b) return one(b, TL, 30) end, "transmutation_of_lead", TL, 1, nil, false, "ground" },
    { "SB1. Soulblight (Doomfire): an enemy in melee 30 m away -> ONE ground cast under it",
      function(b) return one(b, SB, 30) end, "soulblight", SB, 1, nil, false, "ground" },
    { "SS1. The Soulstealer: an enemy in melee 30 m away (bound 70 m) -> ONE ground cast under it",
      function(b) return one(b, SS, 30) end, "the_soulstealer", SS, 1, nil, false, "ground" },
    { "SQ1. Squig Thinkin': an enemy in melee 30 m away (bound 52 m) -> ONE ground cast under it",
      function(b) return one(b, SQ, 30) end, "squig_thinkin", SQ, 1, nil, false, "ground" },
    { "DJ1. Curse of Djaf: enemy handgunners shooting 30 m away, not in melee -> ONE ground cast under them",
      function(b) return one(b, DJ, 30, { name = GUNS, melee = false, ammo_start = 100, ammo_seq = DROPS }) end,
      "curse_of_djaf", DJ, 1, 0, false, "ground" },
    { "DJ2. Curse of Djaf: a fighting enemy that is not a missile unit -> no cast",
      function(b) return one(b, DJ, 30) end, "curse_of_djaf", DJ, 0, nil, false, nil },
    { "HM1. Soulblight (Handmaidens): the unit in melee -> ONE cast on self",
      function(b) return { { name = CASTER, uid = b, owns = { HM }, melee = true, dist = 1 } },
        { { uid = b + 5, name = LIVING, melee = true } } end, "soulblight_handmaidens", HM, 1, 0, false, "self" },
    { "HM2. Soulblight (Handmaidens): not in melee -> no cast",
      function(b) return one(b, HM, 30) end, "soulblight_handmaidens", HM, 0, nil, false, nil },
    { "LO1. Spinning Loons: an enemy in melee 10 m away (bound 17 m) -> ONE ground cast under it",
      function(b) return one(b, LO, 10) end, "spinning_loons", LO, 1, 0, false, "ground" },
    { "LO2. Spinning Loons: the enemy is 25 m away (beyond 17 m) -> no cast",
      function(b) return one(b, LO, 25) end, "spinning_loons", LO, 0, nil, false, nil },
    { "LO3. Spinning Loons: the enemy is flying -> no cast",
      function(b) return one(b, LO, 10) end, "spinning_loons", LO, 0, nil, true, nil },
    { "LE1. The Loons of Eight Peaks: an enemy in melee 10 m away -> ONE ground cast under it",
      function(b) return one(b, LE, 10) end, "loons_of_eight_peaks", LE, 1, nil, false, "ground" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED142 then want = w[6] end
      if want ~= nil then
        local base = 14800 + i * 20
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, w[7])
        if W ~= nil then
          local got, gground, last = 0, 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then gground = gground + 1; last = x end end
          local total = got + gground
          local a = (total == want)
          if a and not RED142 and total >= 1 and w[8] == "ground" then
            a = (gground == 1 and last.pos ~= nil and last.pos.marker == ("pos:" .. tostring(base + 5)))
          elseif a and not RED142 and total >= 1 and w[8] == "self" then
            a = (got == 1 and gground == 0)
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED142 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. total .. ((w[8] ~= nil and not RED142) and (" (" .. w[8] .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED142 then
    check("RED CONTROL (harness 142): the pre-143 build has none of the batch-2 entries - "
      .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 142: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 28 and n_ok == 28)
  end
  print("== HARNESS 142 done: " .. (checks - pre142) .. " checks in this section ==")
end
'''

# (regex, replacement, guard substring or None)
PIN_RULES = [
    (r"== 703\b", "== 712", None),
    (r"== 756\b", "== 767", None),
    (r"it == 1406\b", "it == 1424", None),
    (r"entries = 703, keys = 756", "entries = 712, keys = 767", None),
    (r"want 703\b", "want 712", None),
    (r"FULL 703-entry table", "FULL 712-entry table", None),
    (r"703 abilities per pass", "712 abilities per pass", None),
    (r"table of 703 after round 142", "table of 712 after round 143", None),
    (r"\(12 air-drop entries of 703\)", "(12 air-drop entries of 712)", None),
    (r"\(RED_MODE and 0 or 169\)", "(RED_MODE and 0 or 173)", None),
    (r"\) == 306\b", ") == 307", "melee_unwavering"),
    (r"mu == 306\b", "mu == 307", None),
    (r"== 67\b", "== 74", "trigger = \"enemy_ground_melee\"') =="),
    (r"\(RED_MODE and 1 or 67\)", "(RED_MODE and 1 or 74)", "enemy_ground_melee"),
    (r"(EXP\.sum and )67( or 1\))", r"\g<1>74\2", None),
    (r"== 207\)", "== 215)", "range_real = \")"),
    (r"\(EXP\.sum and 207 or 96\)", "(EXP.sum and 215 or 96)", None),
    (r"== 21\)", "== 24)", "target_class = \")"),
    (r"nkeys == 162\b", "nkeys == 166", None),
    (r"mu = 306,", "mu = 307,", "EXP = { entries = 712"),
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
TIP_OLD = '    self_moving = "When armed, fires when this unit is moving",\n'
TIP_NEW = TIP_OLD + ('    enemy_ground_shooting = "When armed, fires on the ground under the closest enemy missile unit in range '
                     'that is shooting",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h140()\nrun_h141()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h142()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
