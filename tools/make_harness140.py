#!/usr/bin/env python3
"""Build harness140.lua from harness139.lua for round 141 (the nine recharge reducers). Older harnesses are never
edited.

Pin rebases (code lines only; comment lines untouched):
  melee_unwavering 314 -> 306 (8 reducers moved), ushoran_health 20 -> 19 (Scroll of Power moved),
  ally_range_real fields 51 -> 53 (Terrorgheist Skull, Spell-Wrought Sceptre);
  the harness-93 tooltip mirror gains the four new wordings;
  harness 131 A1 (Aken-seth's charge hold): Aken-seth now needs another of the caster's abilities recharging, so the
  caster also owns and arms Strike of Tombs; the mod casts that first, then Aken-seth (14 polls instead of 4, for
  the per-unit cast gate).
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_moving_running_harness139\harness139.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_recharge_reducers_harness140\harness140.lua"
SOT = "wh2_dlc09_character_abilities_strike_of_tombs"

BANNER = """-- ============================================================================
-- HARNESS 140 - ROUND 141: THE NINE RECHARGE REDUCERS (user rulings 2026-11-13).
--   self_recharging (5), self_recharging_2 (Scroll of Power), melee_health75
--   (Armour of Caledor), melee_self_or_ally (Terrorgheist Skull),
--   recharging_in_reach (Spell-Wrought Sceptre).
--   Edited vs harness139: this banner, the pin and world rebases listed in
--   tools/make_harness140.py, the tooltip mirror, run_h140 and its call.
--   RED control: H140_LIVE / H140_ANN on docs/backups/round141/pre141_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 140 (round 141): THE NINE RECHARGE REDUCERS.
--   S1 Staff of Tomorrow in melee, nothing recharging -> no cast. S2 the caster
--   also owns Strike of Tombs: the mod casts it, then Staff of Tomorrow fires.
--   P1 Scroll of Power with one ability recharging -> no cast; P2 with two ->
--   ONE cast. C1 Armour of Caledor in melee at 60% health -> ONE cast; C2 in
--   melee at full health -> none. T1 Terrorgheist Skull: the caster idle, an
--   ally 50 m away in melee -> ONE cast ON the ally; T2 the ally 80 m away ->
--   none. W1 Spell-Wrought Sceptre: the caster idle, an ally 30 m away whose
--   Strike of Tombs the mod cast -> ONE cast ON the ally.
--   RED (pre-141 = round 140): S1 and C2 cast (the old melee trigger); T1 casts
--   nothing on the ally.
-- ============================================================================
function run_h140()
  local L140 = os.getenv("H140_LIVE") or LIVE
  local A140 = os.getenv("H140_ANN") or ANN
  local RED140 = (os.getenv("H140_LIVE") ~= nil) or (os.getenv("H140_ANN") ~= nil)
  local TOM = "wh3_main_weapon_abilities_staff_of_tomorrow"
  local SCR = "wh_main_item_abilities_scroll_of_power"
  local CAL = "wh2_dlc15_item_abilities_armour_of_caledor"
  local TER = "wh_dlc08_item_abilities_terrorgheist_skull"
  local SCE = "wh3_dlc23_weapon_abilities_spell_wrought_sceptre"
  local SOT = "wh2_dlc09_character_abilities_strike_of_tombs"
  local BLD = "wh2_dlc09_weapon_abilities_blessed_blade_of_ptra"
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local pre140 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 140 - section 0zl: the round-141 tokens ==")
  if not RED140 then
    for _, f in ipairs({ { name = "live", path = L140 }, { name = "ann", path = A140 } }) do
      local s = read_file(f.path)
      check("0zl " .. f.name .. ": the casts are remembered, the generated lock table loads, the four families are wired",
        raw_find(s, "FOURTH.note_cast(unit, ability_key)", 1, true) ~= nil
        and raw_find(s, "FOURTH.RECHARGE_TEXT = ", 1, true) ~= nil
        and raw_find(s, "FOURTH.load_recharge()\n", 1, true) ~= nil
        and cp(s, 'trigger = "self_recharging"') == 5 and cp(s, 'trigger = "self_recharging_2"') == 1
        and cp(s, 'trigger = "recharging_in_reach"') == 1 and cp(s, 'trigger = "melee_self_or_ally"') == 1)
    end
  end

  local FILES = { { path = A140, tag = "[annotated] " }, { path = L140, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires(W, key)
    local n, last = 0, nil
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1; last = f end end
    return n, last
  end
  -- the mock accepts every repeat cast; here a HELPER ability (not the one under test) is marked not ready after its
  -- first cast, as the game's cooldown would, so it cannot keep taking the caster's cast slot
  local function world(wname, units, arms, keys, PATH, TAG, polls, test_key)
    local cards, bar, can = {}, {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[#bar + 1] = { id = "b" .. i, key = k }; can[k] = true end
    local W = make_world({ can_perform = true, can_keys = can, units = units, cards = cards, bar = bar })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for _, a in ipairs(arms) do
      sel_event(W, a[1], true); ui(W); ui(W)
      click(W, "zz_auto_badge_" .. a[2]); ui(W)
      sel_event(W, a[1], false); ui(W)
    end
    W.conflict = true
    for _ = 1, polls do
      polln(W, 1)
      for _, x in ipairs(W.fires) do
        if x.key ~= test_key then can[x.key] = false end
      end
    end
    return W
  end
  local function unit_id_of(t)
    local id = nil
    if t ~= nil then pcall(function() id = tostring(t:unique_ui_id()) end) end
    return id
  end
  -- name, units(b), arms(b), keys, key under test, polls, GREEN casts, RED casts (nil = not RED), target uid offset (0 self, 1 ally)
  local WORLDS = {
    { "S1. Staff of Tomorrow in melee, nothing recharging -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { TOM }, melee = true } } end,
      function(b) return { { b, "staff_of_tomorrow" } } end, { TOM }, TOM, 6, 0, 1, nil },
    { "S2. Staff of Tomorrow: the mod casts Strike of Tombs first -> ONE cast",
      function(b) return { { name = LORD, uid = b, owns = { TOM, SOT }, melee = true } } end,
      function(b) return { { b, "staff_of_tomorrow" }, { b, "strike_of_tombs" } } end, { TOM, SOT }, TOM, 16, 1, nil, 0 },
    { "P1. Scroll of Power with ONE ability recharging -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { SCR, SOT }, melee = true } } end,
      function(b) return { { b, "scroll_of_power" }, { b, "strike_of_tombs" } } end, { SCR, SOT }, SCR, 16, 0, nil, nil },
    { "P2. Scroll of Power with TWO abilities recharging -> ONE cast",
      function(b) return { { name = LORD, uid = b, owns = { SCR, SOT, BLD }, melee = true } } end,
      function(b) return { { b, "scroll_of_power" }, { b, "strike_of_tombs" }, { b, "blessed_blade_of_ptra" } } end,
      { SCR, SOT, BLD }, SCR, 23, 1, nil, 0 },
    { "C1. Armour of Caledor in melee at 60% health -> ONE cast",
      function(b) return { { name = LORD, uid = b, owns = { CAL }, melee = true, health_percent = 60 } } end,
      function(b) return { { b, "armour_of_caledor" } } end, { CAL }, CAL, 6, 1, nil, 0 },
    { "C2. Armour of Caledor in melee at full health -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { CAL }, melee = true } } end,
      function(b) return { { b, "armour_of_caledor" } } end, { CAL }, CAL, 6, 0, 1, nil },
    { "T1. Terrorgheist Skull: the caster idle, an ally 50 m away in melee -> ONE cast ON the ally",
      function(b) return { { name = LORD, uid = b, owns = { TER }, melee = false },
        { name = PLAIN, uid = b + 1, owns = {}, melee = true, dist = 50 } } end,
      function(b) return { { b, "terrorgheist_skull" } } end, { TER }, TER, 6, 1, 0, 1 },
    { "T2. Terrorgheist Skull: the ally in melee is 80 m away -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { TER }, melee = false },
        { name = PLAIN, uid = b + 1, owns = {}, melee = true, dist = 80 } } end,
      function(b) return { { b, "terrorgheist_skull" } } end, { TER }, TER, 6, 0, nil, nil },
    { "W1. Spell-Wrought Sceptre: an ally 30 m away whose Strike of Tombs the mod cast -> ONE cast ON the ally",
      function(b) return { { name = LORD, uid = b, owns = { SCE }, melee = false },
        { name = LORD, uid = b + 1, owns = { SOT }, melee = true, dist = 30 } } end,
      function(b) return { { b, "spell_wrought_sceptre" }, { b + 1, "strike_of_tombs" } } end, { SCE, SOT }, SCE, 8, 1, nil, 1 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[7]
      if RED140 then want = w[8] end
      if want ~= nil then
        local base = 14300 + i * 10
        local W = world(w[1], w[2](base), w[3](base), w[4], f.path, TAG, w[6], w[5])
        if W ~= nil then
          local got, last = fires(W, w[5])
          local a = (got == want)
          if a and want == 1 and not RED140 and w[9] ~= nil then
            local tid = unit_id_of(last.target)
            if w[9] == 0 then a = (tid == nil or tid == tostring(base)) else a = (tid == tostring(base + 1)) end
          end
          local all = {}
          for _, x in ipairs(W.fires) do all[#all + 1] = tostring(x.key):sub(-18) .. "@" .. tostring(x.tick) end
          check(TAG .. w[1]:sub(1, 2) .. (RED140 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. " (all casts: " .. table.concat(all, ", ") .. ")", a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED140 then
    check("RED CONTROL (harness 140): the pre-141 build fires the reducers in melee and never on an ally - "
      .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  else
    check("HARNESS 140: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 18 and n_ok == 18)
  end
  print("== HARNESS 140 done: " .. (checks - pre140) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"(trigger = \"melee_unwavering\"'\)) == 314\b", r"\1 == 306"),
    (r"\bmu == 314\b", "mu == 306"),
    (r"\bmu = 314\b", "mu = 306"),
    (r"(trigger = \"ushoran_health\"'\)) == 20\b", r"\1 == 19"),
    (r"(ally_range_real = \"\)) == 51\b", r"\1 == 53"),
    (r"mu = 306, ush = 20\b", "mu = 306, ush = 19"),
    (r"(trigger = \"melee_health75\"'\)) == 1\b", r"\1 == 2"),
]
WORLD_RULES = [
    ('{ caster(13301, AK, { melee = true }) }, { { 13301, "aken_seth_the_staff_of_pain" } }, { AK }, f.path, TAG, 4)',
     '{ caster(13301, AK, { melee = true, owns = { AK, "%s" } }) },\n'
     '      { { 13301, "aken_seth_the_staff_of_pain" }, { 13301, "strike_of_tombs" } }, { AK, "%s" }, f.path, TAG, 14)' % (SOT, SOT)),
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
        changed.append((i + 1, ln.strip()[:110], new.strip()[:110]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
for a, b in WORLD_RULES:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
TIP_OLD = '    self_running = "When armed, fires when this unit is running",\n'
TIP_NEW = TIP_OLD + (
    '    self_recharging = "When armed, fires when another ability of this unit is recharging",\n'
    '    self_recharging_2 = "When armed, fires when two other abilities of this unit are recharging",\n'
    '    recharging_in_reach = "When armed, fires when this unit or a friendly unit near it has an ability recharging",\n'
    '    melee_self_or_ally = "When armed, fires when this unit or a friendly unit near it is in melee",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h138()\nrun_h139()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h140()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
