#!/usr/bin/env python3
"""Build harness141.lua from harness140.lua for round 142 (open batch 1: More Powder!, Restock! (gunnery school),
Master of Mists, Of Warp and Ruin, Ominous Powder; Blooood! on self_moving). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched):
  entries 698 -> 703, keys 750 -> 756 (5 entries / 6 keys added), full-table iterations 1396 -> 1406,
  multi-use charge-gate keys 165 -> 169, ally_range_real fields 53 -> 56;
  the harness-139 token check: Blooood! rides self_moving (round 142), not self_running;
  the harness-93 tooltip mirror gains the four new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_recharge_reducers_harness140\harness140.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch1_harness141\harness141.lua"

BANNER = """-- ============================================================================
-- HARNESS 141 - ROUND 142: OPEN BATCH 1 AND BLOOOOD! WHEN MOVING.
--   5 new entries / 6 keys: More Powder!, Restock! (gunnery school), Master of
--   Mists, Of Warp and Ruin, Ominous Powder. Blooood! on self_moving.
--   Edited vs harness140: this banner, the pin rebases listed in
--   tools/make_harness141.py, the tooltip mirror, run_h141 and its call.
--   RED control: H141_LIVE / H141_ANN on docs/backups/round142/pre142_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 141 (round 142): OPEN BATCH 1 AND BLOOOOD!.
--   MP1 More Powder!: Handgunners 30 m away shooting at 60% ammunition -> ONE
--   cast ON them. MP2 at 90% -> none. RG1 Restock! (gunnery school) = MP1.
--   MM1 Master of Mists: Handgunners 60 m away, range 150 m, nearest enemy 190 m
--   (<= 202.5 m) -> ONE GROUND cast under them. MM2 nearest enemy 140 m (in
--   range) -> none. MM3 nearest enemy 220 m -> none.
--   WR1 Of Warp and Ruin: the cannon shooting at a target not in melee -> a
--   cast. WR2 its target in melee -> none.
--   OP1 Ominous Powder: shooting at 80% health -> a cast. OP2 at 40% -> none.
--   BL1 Blooood!: the Hellcannon walking (not running) -> ONE cast.
--   RED (pre-142 = round 141): MP1, MM1, WR1, OP1 and BL1 cast nothing.
-- ============================================================================
function run_h141()
  local L141 = os.getenv("H141_LIVE") or LIVE
  local A141 = os.getenv("H141_ANN") or ANN
  local RED141 = (os.getenv("H141_LIVE") ~= nil) or (os.getenv("H141_ANN") ~= nil)
  local MP = "wh2_dlc11_hero_abilities_more_powder"
  local RG = "wh3_dlc25_abilities_restock_gunnery_school"
  local MM = "wh3_dlc27_character_abilities_master_of_mists_custom"
  local WR = "wh3_dlc29_unit_abilities_of_warp_and_ruin"
  local OP = "wh3_dlc25_item_abilities_ominous_powder"
  local BL = "wh_main_unit_abilities_blooood"
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local HG = "wh_main_emp_inf_handgunners"          -- reload 13 s: cast point at poll 2 + 26
  local CANNON = "wh3_dlc29_skv_art_warp_doom_magma_cannon"   -- reload 21 s: cast point at poll 2 + 42
  local HC = "wh_main_chs_art_hellcannon"
  local ZOMB = "wh_main_vmp_inf_zombie"
  local pre141 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 141 - section 0zm: the round-142 tokens ==")
  if not RED141 then
    for _, f in ipairs({ { name = "live", path = L141 }, { name = "ann", path = A141 } }) do
      local s = read_file(f.path)
      check("0zm " .. f.name .. ": 703 entries; the 5 new markers; Blooood! on self_moving; the 250 m bound; Mist band 1.35",
        cp(s, "\t{ marker = ") == 703
        and raw_find(s, '{ marker = "more_powder", name = "More Powder!", trigger = "ally_ammo_low",', 1, true) ~= nil
        and raw_find(s, '{ marker = "restock_gunnery_school", name = "Restock!", trigger = "ally_ammo_low",', 1, true) ~= nil
        and raw_find(s, '{ marker = "master_of_mists", name = "Master of Mists", trigger = "ground_ally_before_range",', 1, true) ~= nil
        and raw_find(s, '{ marker = "of_warp_and_ruin", name = "Of Warp and Ruin", trigger = "self_shooting_clear",', 1, true) ~= nil
        and raw_find(s, '{ marker = "ominous_powder", name = "Ominous Powder", trigger = "self_shooting_healthy",', 1, true) ~= nil
        and raw_find(s, 'name = "Blooood!", trigger = "self_moving",', 1, true) ~= nil
        and raw_find(s, "FOURTH.ALLY_CAST_R250 = 175", 1, true) ~= nil
        and raw_find(s, "FOURTH.MIST_BAND = 1 + FOURTH.MIST_BONUS * FOURTH.RANGE_FRACTION", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A141, tag = "[annotated] " }, { path = L141, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, arm, key, PATH, TAG, polls)
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
    polln(W, polls)
    return W
  end
  local function refill(b, key, frac)
    return { { name = LORD, uid = b, owns = { key }, melee = false, dist = 30 },
      { name = HG, uid = b + 1, owns = {}, melee = false, ammo_start = 100, ammo_seq = { 100, frac }, dist = 30 } }, nil
  end
  local function mist(b, gap)
    return { { name = LORD, uid = b, owns = { MM }, melee = false, dist_by_target = { [b + 1] = 60 } },
      { name = HG, uid = b + 1, owns = {}, melee = false, ammo_start = 100, ammo_seq = { 100 }, missile_range = 150,
        dist_by_target = { [b + 11] = gap } } },
      { { name = ZOMB, uid = b + 11, owns = {}, melee = false } }
  end
  local function cannon(b, tmelee)
    return { { name = CANNON, uid = b, owns = { WR }, melee = false, ammo_start = 20, ammo_seq = { 20, 19 },
      ammo_target = { type = ZOMB, melee = tmelee } } }, nil
  end
  local function powder(b, hp)
    return { { name = HG, uid = b, owns = { OP }, melee = false, ammo_start = 100, ammo_seq = { 100, 99 },
      health_percent = hp } }, nil
  end
  -- name, builder(b), marker, key, polls, GREEN casts (exact; "1+" = at least one), RED (nil = not RED), target: ally / ground / self
  local WORLDS = {
    { "MP1. More Powder!: Handgunners 30 m away shooting at 60% ammunition -> ONE cast ON them",
      function(b) return refill(b, MP, 60) end, "more_powder", MP, 4, 1, 0, "ally" },
    { "MP2. More Powder!: the Handgunners still have 90% -> no cast",
      function(b) return refill(b, MP, 90) end, "more_powder", MP, 4, 0, nil, nil },
    { "RG1. Restock! (gunnery school): Handgunners at 60% -> ONE cast ON them",
      function(b) return refill(b, RG, 60) end, "restock_gunnery_school", RG, 4, 1, nil, "ally" },
    { "MM1. Master of Mists: Handgunners 60 m away, range 150 m, nearest enemy 190 m -> ONE ground cast under them",
      function(b) return mist(b, 190) end, "master_of_mists", MM, 4, 1, 0, "ground" },
    { "MM2. Master of Mists: the nearest enemy is 140 m away (in range) -> no cast",
      function(b) return mist(b, 140) end, "master_of_mists", MM, 4, 0, nil, nil },
    { "MM3. Master of Mists: the nearest enemy is 220 m away (beyond 202.5 m) -> no cast",
      function(b) return mist(b, 220) end, "master_of_mists", MM, 4, 0, nil, nil },
    { "WR1. Of Warp and Ruin: shooting at a target not in melee -> a cast",
      function(b) return cannon(b, false) end, "of_warp_and_ruin", WR, 46, "1+", 0, "self" },
    { "WR2. Of Warp and Ruin: its target is in melee -> no cast",
      function(b) return cannon(b, true) end, "of_warp_and_ruin", WR, 46, 0, nil, nil },
    { "OP1. Ominous Powder: shooting at 80% health -> a cast",
      function(b) return powder(b, 80) end, "ominous_powder", OP, 30, "1+", 0, "self" },
    { "OP2. Ominous Powder: shooting at 40% health -> no cast",
      function(b) return powder(b, 40) end, "ominous_powder", OP, 30, 0, nil, nil },
    { "BL1. Blooood!: the Hellcannon walking, not running -> ONE cast",
      function(b) return { { name = HC, uid = b, owns = { BL }, melee = false, moving = true, fast = false } }, nil end,
      "blooood", BL, 4, 1, 0, "self" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[6]
      if RED141 then want = w[7] end
      if want ~= nil then
        local base = 14400 + i * 20
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, w[5])
        if W ~= nil then
          local got, last = 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          local gground = 0
          for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then gground = gground + 1; last = x end end
          local total = got + gground
          local a
          if want == "1+" then a = (total >= 1) else a = (total == want) end
          if a and not RED141 and total >= 1 and w[8] == "ally" then
            local tid = nil
            if last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
            a = (tid == tostring(base + 1))
          elseif a and not RED141 and total >= 1 and w[8] == "ground" then
            a = (gground == 1 and last.pos ~= nil and last.pos.marker == ("pos:" .. tostring(base + 1)))
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED141 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. total .. ((w[8] ~= nil and not RED141) and (" (on the " .. w[8] .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED141 then
    check("RED CONTROL (harness 141): the pre-142 build has none of the new entries and no walking trigger - "
      .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  else
    check("HARNESS 141: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 22 and n_ok == 22)
  end
  print("== HARNESS 141 done: " .. (checks - pre141) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"== 698\b", "== 703"),
    (r"== 750\b", "== 756"),
    (r"it == 1396\b", "it == 1406"),
    (r"entries = 698, keys = 750", "entries = 703, keys = 756"),
    (r"want 698\b", "want 703"),
    (r"FULL 698-entry table", "FULL 703-entry table"),
    (r"698 abilities per pass", "703 abilities per pass"),
    (r"table of 698 after round 134", "table of 703 after round 142"),
    (r"\(12 air-drop entries of 698\)", "(12 air-drop entries of 703)"),
    (r"\(RED_MODE and 0 or 165\)", "(RED_MODE and 0 or 169)"),
    (r"(ally_range_real = \"\)) == 53\b", r"\1 == 56"),
    (r"name = \"Blooood!\", trigger = \"self_running\",", 'name = "Blooood!", trigger = "self_moving",'),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        new2, n = re.subn(a, b, new)
        if n:
            hits[a] += n
            new = new2
    if new != ln:
        changed.append(i + 1)
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
TIP_OLD = '    melee_self_or_ally = "When armed, fires when this unit or a friendly unit near it is in melee",\n'
TIP_NEW = TIP_OLD + (
    '    ground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range",\n'
    '    self_shooting_clear = "When armed, fires when this unit is shooting at a target that is not in melee",\n'
    '    self_shooting_healthy = "When armed, fires when this unit is shooting and above half health",\n'
    '    self_moving = "When armed, fires when this unit is moving",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h139()\nrun_h140()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h141()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
