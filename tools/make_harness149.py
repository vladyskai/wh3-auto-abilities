#!/usr/bin/env python3
"""Build harness149.lua from harness148.lua for round 150 (value-destroyed blob targets, the standstill gate, the Winds
of Magic abilities on when_ready, the WINDS map row). Older harnesses are never edited.

Pin rebases (documented in docs/WH3_round150_value_target.md):
  melee_unwavering 309 -> 288 (the 21 Winds of Magic abilities moved to when_ready);
  the harness-91 O1/O2 worlds used Black Periapt as their in-melee example; it is now a when_ready ability, so they use
    Runefang (still melee_unwavering, self-cast, no wind-up) - the worlds' meaning is unchanged;
  the round-149 revert check (0zu) compared the CURRENT source with round 146; it now compares the pre-150 snapshot
    (docs/backups/round150) with round 146 - the revert still proven, the source free to change;
  the tooltip mirror: the enemy_blob wording changed, when_ready added.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_revert_probes_harness148\harness148.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_value_target_harness149\harness149.lua"

BANNER = """-- ============================================================================
-- HARNESS 149 - ROUND 150: THE BLOB TARGET DESTROYS THE MOST VALUE; NEVER WHILE
--   MOVING; THE 21 WINDS OF MAGIC ABILITIES FIRE WHEN READY; THE WINDS ROW.
--   Edited vs harness148: this banner, the pin rebases listed in
--   tools/make_harness149.py, the tooltip mirror, run_h149 and its call.
--   RED control: H149_LIVE / H149_ANN on docs/backups/round150/pre150_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 149 (round 150).
--   Fireball (5 m, 144 base / 0 AP per soldier) and Volley of High Arrows (4 m,
--   0 base / 150 AP: AP-heavy); the caster 100 m from the enemy, standing.
--   VD1 a Tithe block (armour 15, value 1 per soldier) listed FIRST and a Grave
--   Guard block (armour 90, value about 7 per soldier), equally dense, both safe:
--   Fireball goes at the GRAVE GUARD (the round-146 rule took the first, Tithe).
--   VD2 Volley with only Tithe in range (armour 15 < 50): no cast.
--   VD3 Volley with Grave Guard: ONE cast at it.
--   MV1 Fireball while the caster MOVES: no cast.
--   WR1 Book of Hoeth NOT in melee: ONE cast (when ready).
--   WL1 (live) a WINDS row every snapshot: our army's current / reserve / rate.
--   RED (pre-150 = round 146 source): VD1 hits the Tithe, VD2 casts, MV1 casts,
--   WR1 stays silent.
-- ============================================================================
function run_h149()
  local L149 = os.getenv("H149_LIVE") or LIVE
  local A149 = os.getenv("H149_ANN") or ANN
  local RED149 = (os.getenv("H149_LIVE") ~= nil) or (os.getenv("H149_ANN") ~= nil)
  local FB = "wh_main_spell_bound_fireball"
  local VO = "wh2_main_character_abilities_volley_of_high_arrows"
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local TI = "wh_dlc04_vmp_inf_tithe_0"
  local pre149 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 149 - section 0zv: the round-150 tokens ==")
  if not RED149 then
    for _, f in ipairs({ { name = "live", path = L149 }, { name = "ann", path = A149 } }) do
      local s = read_file(f.path)
      check("0zv " .. f.name .. ": value rule, armour rule 50, standstill gate, 21 on when_ready, the WINDS row, the tables",
        cp(s, 'trigger = "when_ready"') == 21 and cp(s, 'trigger = "melee_unwavering"') == 288
        and raw_find(s, "FOURTH.BLOB_AP_ARMOUR_MIN = 50 ", 1, true) ~= nil
        and raw_find(s, "function FOURTH.blob_value(tgt, m, r, dmg)", 1, true) ~= nil
        and raw_find(s, "function FOURTH.blob_still(unit)", 1, true) ~= nil
        and raw_find(s, "when_ready = FOURTH.evaluate_when_ready,", 1, true) ~= nil
        and raw_find(s, '"WINDS t=" .. t', 1, true) ~= nil
        and raw_find(s, "wh2_main_character_abilities_volley_of_high_arrows=0,150,1;", 1, true) ~= nil
        and raw_find(s, "wh_main_vmp_inf_grave_guard_0=90,82;", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A149, tag = "[annotated] " }, { path = L149, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, arm, key, PATH, TAG, sv, army)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    if army ~= nil then W.bm.get_player_army = function() return army end end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        if sv ~= nil and sv[id] ~= nil then
          local v = sv[id]
          pr.unit.strategic_value = function(self) return v end
        end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, key, moving)
    return { name = CASTER, uid = b, owns = { key }, melee = false, dist = 100, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com", moving = moving }
  end
  local function block(uid, name, men, x, z)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = men,
             initial_men = men, unit_class = "inf_mel" }
  end
  -- name, builder(b) -> units, enemies, values; marker; key; GREEN casts; RED casts (nil = not RED);
  -- GREEN target offset; RED target offset
  local WORLDS = {
    { "VD1. Fireball: two Tithe blocks stacked (twice the soldiers) and one Grave Guard block -> ONE cast at the GRAVE GUARD",
      function(b) return { caster(b, FB) }, { block(b + 5, TI, 120, 60, 150), block(b + 6, GG, 120, -60, 150),
          block(b + 7, TI, 120, 60, 150) },
        { [tostring(b + 5)] = 120, [tostring(b + 6)] = 850, [tostring(b + 7)] = 120 } end,
      "spell_bound_fireball", FB, 1, 1, 6, 5 },
    { "VD2. Volley of High Arrows: only Tithe in range (armour 15) -> no cast",
      function(b) return { caster(b, VO) }, { block(b + 5, TI, 120, 0, 150) }, { [tostring(b + 5)] = 120 } end,
      "character_abilities_volley_of_high_arrows", VO, 0, 1, nil, 5 },
    { "VD3. Volley of High Arrows: a Grave Guard block -> ONE cast at it",
      function(b) return { caster(b, VO) }, { block(b + 5, GG, 120, 0, 150) }, { [tostring(b + 5)] = 850 } end,
      "character_abilities_volley_of_high_arrows", VO, 1, nil, 5, nil },
    { "MV1. Fireball while the caster MOVES -> no cast",
      function(b) return { caster(b, FB, true) }, { block(b + 5, GG, 120, 0, 150) }, { [tostring(b + 5)] = 850 } end,
      "spell_bound_fireball", FB, 0, 1, nil, 5 },
    { "WR1. Book of Hoeth, the owner NOT in melee -> ONE cast (when ready)",
      function(b) return { { name = CASTER, uid = b, owns = { BH }, melee = false, dist = 300 } }, nil, nil end,
      "book_of_hoeth", BH, 1, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED149 then want = w[6] end
      if want ~= nil then
        local base = 16400 + i * 20
        local units, enemies, sv = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, sv, nil)
        if W ~= nil then
          local got, last = 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          local a = (got == want)
          local off = RED149 and w[8] or w[7]
          local tid = nil
          if last ~= nil and last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
          if a and got >= 1 and off ~= nil then
            a = (tid == tostring(base + off))
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED149 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. got .. ((off ~= nil) and (" (want target +" .. off .. ", got " .. tostring(tid and (tonumber(tid) - base)) .. ")") or ""), a)
          done(a)
          if TAG == "[live] " and not RED149 and got >= 1 and w[4] ~= BH then
            local seen = false
            for _, l in ipairs(W.log_lines or {}) do
              if raw_find(l, "infantry blob (targeting", 1, true) ~= nil and raw_find(l, "value destroyed", 1, true) ~= nil then seen = true end
            end
            check(TAG .. w[1]:sub(1, 3) .. "b: the reason names the value destroyed", seen)
          end
          tally(W)
        end
      end
    end
    -- WL1: the WINDS row (live only; the reading copy keeps no log)
    if TAG == "[live] " and not RED149 then
      local army = {}
      function army:winds_of_magic_current() return 12 end
      function army:winds_of_magic_reserve() return 68 end
      function army:winds_of_magic_remaining_recharge_rate() return 0 end
      local W = world("WL1. the WINDS row with our army's winds", { { name = CASTER, uid = 16590, owns = {}, melee = false } },
        nil, { 16590, "book_of_hoeth" }, BH, f.path, TAG, nil, army)
      if W ~= nil then
        polln(W, 12)
        local n = 0
        for _, l in ipairs(W.log_lines or {}) do
          if raw_find(l, "WINDS t=", 1, true) ~= nil and raw_find(l, " current=12.0 reserve=68.0 recharge_rate=0.000", 1, true) ~= nil then n = n + 1 end
        end
        check(TAG .. "WL1a: the WINDS row reads our army's winds (" .. n .. " rows)", n >= 1)
        done(n >= 1)
        tally(W)
      end
    end
  end
  if RED149 then
    check("RED CONTROL (harness 149): the pre-150 build picks the Tithe, fires the Volley at it, casts while moving and "
      .. "keeps Book of Hoeth for melee - " .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 149: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 11 and n_ok == 11)
  end
  print("== HARNESS 149 done: " .. (checks - pre149) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"\) == 309\b", ") == 288", "melee_unwavering"),
    (r"mu == 309\b", "mu == 288", None),
    (r"mu = 309,", "mu = 288,", "EXP = {"),
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
R = [
    ('  local M_MU1  = "wh_main_item_abilities_black_periapt"          -- melee_unwavering (Whip of Agony)\n',
     '  local M_MU1  = "wh_main_weapon_abilities_runefang"   -- ROUND 150: was Black Periapt (now when_ready); melee_unwavering\n'),
    ('    if not boot(W, PATH, TAG, 9201, "black_periapt", "O1") then return nil end\n',
     '    if not boot(W, PATH, TAG, 9201, "runefang", "O1") then return nil end\n'),
    ('    if not boot(W, PATH, TAG, 9202, "black_periapt", "O2") then return nil end\n',
     '    if not boot(W, PATH, TAG, 9202, "runefang", "O2") then return nil end\n'),
    ('  for _, f in ipairs({ { name = "live", path = L148, base = B146_LIVE }, { name = "ann", path = A148, base = B146_ANN } }) do\n',
     '  -- ROUND 150: the revert is proven on the pre-150 snapshot (the source itself moves on)\n'
     '  for _, f in ipairs({ { name = "live", path = L148, base = B146_LIVE, pre = "C:/Users/vlady/Desktop/WH3_mod/docs/backups/round150/pre150_zz_test_deadly_onslaught.lua" },\n'
     '                      { name = "ann", path = A148, base = B146_ANN, pre = "C:/Users/vlady/Desktop/WH3_mod/docs/backups/round150/pre150_WH3_auto_ability_annotated.lua" } }) do\n'),
    ('    local a = (s == read_file(f.base))\n',
     '    local a = (read_file(f.pre) == read_file(f.base))\n'),
    ('    enemy_blob = "When armed, fires at the densest enemy infantry in range when the blast hits enough soldiers and none of ours are near",\n',
     '    enemy_blob = "When armed and standing still, fires at the enemy infantry where the blast destroys the most value, when it hits enough soldiers and none of ours are near",\n'
     '    when_ready = "When armed, fires as soon as it is ready",\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h148()\n") == 1
src = src.replace("\nrun_h148()\n", "\nrun_h148()\nrun_h149()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
