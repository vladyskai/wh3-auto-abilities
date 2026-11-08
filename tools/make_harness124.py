#!/usr/bin/env python3
"""Build harness124.lua from harness123.lua for round 125.

  1. prepends the round-125 banner;
  2. adds OPT-IN ammunition to the mock unit (def.ammo_start / def.ammo_seq: the
     n-th ammo_left() read answers the n-th entry, the last repeats) and an opt-in
     shooting target (def.ammo_target = { type = ..., melee = bool }); a unit
     without these fields is byte-identical to before;
  3. RETIRES run_h123 from the runner (the function stays in the file as history):
     it tested the round-124 spell-bar badge PLACEMENT, which the user's ruling of
     2026-11-03 removes - spell-bar buttons now get no badge at all. Run on the
     round-125 source it fails exactly its own 19 placement checks and nothing else;
  4. appends run_h124 (the spell-bar rule + the ammo probe) and calls it.
No count pin moves (no ABILITIES entry changes). Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_spellbar_test_harness123\harness123.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_spellbar_rule_ammo_probe_harness124\harness124.lua"

BANNER = """-- ============================================================================
-- HARNESS 124 - ROUND 125: THE SPELL-BAR RULE AND THE AMMO PROBE.
--   (A) User ruling 2026-11-03: the right-hand bar (spells, and the runes the
--       game also puts there) gets no letter and no trigger; the left-hand wheel
--       stays ours, a rune on the wheel included. A 'button_spell...' button is
--       never claimed. The round-124 placement test is removed from the source.
--   (B) The read-only ammo probe: ammo_left() drop -> FIRING ON; no drop for
--       1.25 x the unit's own measured volley gap (10 s default) -> FIRING OFF.
--   Edited vs harness123: this banner, opt-in ammo on the mock unit, run_h123
--   RETIRED from the runner (it tested the removed placement), run_h124 added.
--   RED control: H124_LIVE / H124_ANN on docs/backups/round125/pre125_*.lua.
-- ============================================================================
"""

UNIT_ANCHOR = "    function u:current_target() touch(); return def.target end\n"
UNIT_ADD = """    -- HARNESS 124: OPT-IN ammunition and a shooting target. def.ammo_start ->
    -- starting_ammo(); def.ammo_seq -> the n-th ammo_left() read answers entry n
    -- (the last repeats). def.ammo_target = { type = ..., melee = bool } makes
    -- current_target() answer an object with type() and is_in_melee(). Units
    -- without these fields get NO new methods (byte-identical to before).
    if def.ammo_start ~= nil then
      function u:starting_ammo() touch(); return def.ammo_start end
      function u:ammo_left()
        touch()
        def.ammo_reads = (def.ammo_reads or 0) + 1
        local v = def.ammo_seq[def.ammo_reads]
        if v == nil then v = def.ammo_seq[#def.ammo_seq] end
        return v
      end
    end
    if def.ammo_target ~= nil then
      local tg = def.ammo_target
      local tobj = {}
      function tobj:type() return tg.type end
      function tobj:is_in_melee() return tg.melee == true end
      function u:current_target() touch(); return tobj end
    end
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 124 (round 125): THE SPELL-BAR RULE AND THE AMMO PROBE.
--   0u: tokens in BOTH files; the round-124 placement code is GONE.
--   P1 THE FIELD CASE: Hammer on the wheel, Rune of Slowness on 'button_spell4':
--      the Hammer badge on wheel slot 1, NO rune badge at all, the skip logged
--      ONCE however many scans run.
--   P2 the CAVEAT: the same rune key on a WHEEL button is claimed and badged.
--   A1 one archer unit: a drop -> FIRING ON (target in melee reported); a second
--      volley 2.00 s later sets the window to 2.50 s; 2.75 s with no drop ->
--      FIRING OFF; a rise -> RESUPPLIED. Exactly ONE FIRING ON (no flicker).
--   A2 two drops one poll apart are ONE volley: no gap measured, the 10 s
--      default window holds, the flag stays ON.
--   A3 a unit with no ammunition: starting_ammo read once, ammo_left NEVER read.
--   RED (H124_LIVE/H124_ANN on the pre-125 build = round 124): P1's rune DOES
--   get a badge (the letter on the right-hand bar the user asked to remove).
-- ============================================================================
function run_h124()
  local L124 = os.getenv("H124_LIVE") or LIVE
  local A124 = os.getenv("H124_ANN") or ANN
  local RED124 = (os.getenv("H124_LIVE") ~= nil) or (os.getenv("H124_ANN") ~= nil)
  local HAMMER = "wh_main_weapon_abilities_the_hammer_of_karak_drazh"
  local RUNE = "wh2_dlc17_rune_abilities_rune_of_slowness"
  local B_HAM = "zz_auto_badge_the_hammer_of_karak_drazh"
  local B_RUNE = "zz_auto_badge_rune_of_slowness"
  local pre124 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function rec_of(W, name)
    local hit = nil
    for i = 1, #(W.created or {}) do
      local r = W.created[i]
      if r.name == name and not r.destroyed then hit = r end
    end
    return hit
  end
  local function at(r, x, y) return r ~= nil and r.offset[1] == x and r.offset[2] == y end
  local function cnt(s, tok)
    local n, a = 0, 1
    while true do
      local i = raw_find(s, tok, a, true)
      if i == nil then return n end
      n = n + 1
      a = i + 1
    end
  end

  print("== HARNESS 124 - section 0u: the spell-bar rule + ammo probe tokens ==")
  for _, f in ipairs({ { name = "live", path = L124 }, { name = "ann", path = A124 } }) do
    local s = read_file(f.path)
    check("0u " .. f.name .. ": a 'button_spell...' button is never claimed",
      raw_find(s, "FOURTH.spell_bar_noted = {}", 1, true) ~= nil
      and raw_find(s, "if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then", 1, true) ~= nil)
    check("0u " .. f.name .. ": the round-124 placement test is GONE (no SPELLBAR_BADGES / spellbar_id)",
      cnt(s, "SPELLBAR_BADGES") == 0 and cnt(s, "spellbar_id") == 0)
    check("0u " .. f.name .. ": the ammo probe exists, its constants are named, and the poll calls it in its own pcall",
      raw_find(s, "function FOURTH.ammo_probe(units)", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_WINDOW_DEFAULT_S = 10", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_WINDOW_FACTOR = 1.25", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_SAME_VOLLEY_S = 1.0", 1, true) ~= nil
      and cnt(s, "pcall(FOURTH.ammo_probe, tracked_units)") == 1)
    check("0u " .. f.name .. ": the probe never casts (no perform_special_ability inside it)",
      (function()
        local a = raw_find(s, "function FOURTH.ammo_probe(units)", 1, true)
        local b = a and raw_find(s, "\nlocal function poll_body()", a, true)
        return a ~= nil and b ~= nil and raw_find(string.sub(s, a, b), "perform_special_ability", 1, true) == nil
      end)())
  end
  do
    local a = read_file(A124)
    check("0u ann: the reading copy stays log-free (" .. cnt(a, "log(") .. " 'log(')", cnt(a, "log(") == 0)
  end

  local FILES = { { path = A124, tag = "[annotated] " }, { path = L124, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function boot(W, PATH, TAG, uid, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true)
    for _ = 1, 4 do ui(W) end
    return true
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- P1: the field case
    local W = make_world({ can_perform = true,
      units = { { name = "rune_smith", uid = 12501, owns = { HAMMER, RUNE }, melee = false } },
      cards = { { id = "12501", state = "selected", vis = true } },
      bar = { { id = "button_order1", key = HAMMER } },
      spellbar = { { id = "button_spell4", key = RUNE, x = 1300, y = 1000 } } })
    print("== " .. TAG .. "P1. Rune Smith: Hammer on the wheel, Rune of Slowness on the spell bar ==")
    if boot(W, f.path, TAG, 12501, "P1") then
      for _ = 1, 6 do ui(W) end
      local h, r = rec_of(W, B_HAM), rec_of(W, B_RUNE)
      if RED124 then
        local rep = (r ~= nil)
        check(TAG .. "P1-RED: the pre-125 build DOES put a letter on the right-hand bar (rune badge created)", rep)
        done(rep)
      else
        local a = at(h, -865, -209)
        check(TAG .. "P1a: the Hammer badge is on wheel slot 1 (-865,-209)", a)
        local b = (r == nil)
        check(TAG .. "P1b: the rune on the spell bar gets NO badge (no letter on the right-hand bar)", b)
        local c = (count_log(W, "scan: rune_of_slowness is on the right-hand SPELL bar ('button_spell4') - not claimed") == 1)
        check(TAG .. "P1c: the skip is logged exactly ONCE over every scan [live log]", lg(TAG, c))
        done(a and b and lg(TAG, c))
      end
      check(TAG .. "P1: every ui tick ran clean (" .. (W.ui_failures or 0) .. ")", (W.ui_failures or 0) == 0)
      tally(W)
    end

    if not RED124 then
      -- P2: the caveat - the same rune key on a WHEEL button stays ours
      local W2 = make_world({ can_perform = true,
        units = { { name = "thane", uid = 12511, owns = { RUNE }, melee = false } },
        cards = { { id = "12511", state = "selected", vis = true } },
        bar = { { id = "button_order1", key = RUNE } } })
      print("== " .. TAG .. "P2. the same rune on a WHEEL button is claimed and badged ==")
      if boot(W2, f.path, TAG, 12511, "P2") then
        local r = rec_of(W2, B_RUNE)
        local a = at(r, -865, -209)
        check(TAG .. "P2a: a rune on the left-hand wheel gets its badge on its wheel slot", a)
        local b = (count_log(W2, "SPELL bar") == 0)
        check(TAG .. "P2b: no spell-bar skip for a wheel button [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
        tally(W2)
      end

      -- A1: one archer unit through a whole firing cycle
      local seq = { 30, 30, 29 }
      for _ = 1, 7 do seq[#seq + 1] = 29 end
      seq[#seq + 1] = 28
      for _ = 1, 11 do seq[#seq + 1] = 28 end
      seq[#seq + 1] = 30
      local def = { name = "archers", uid = 12521, owns = {}, melee = false,
                    ammo_start = 30, ammo_seq = seq, ammo_target = { type = "orc_boyz", melee = true } }
      local W3 = make_world({ can_perform = true, units = { def },
        cards = { { id = "12521", state = "active", vis = true } }, bar = {} })
      print("== " .. TAG .. "A1. archers: drop -> ON, second volley 2.00 s later, 2.75 s quiet -> OFF, resupply ==")
      local okl = pcall(load_world, W3, f.path)
      check(TAG .. "A1: the file loads", okl)
      if okl then
        deploy_phases(W3); ui(W3)
        W3.conflict = true
        polln(W3, 30)
        local a = (def.ammo_reads ~= nil and def.ammo_reads >= 23)
        check(TAG .. "A1a: ammo_left was read once per poll (" .. tostring(def.ammo_reads) .. " reads)", a)
        local b = (count_log(W3, "FIRING ON unit 12521 'archers'") == 1
          and count_log(W3, "target='orc_boyz' target_in_melee=true") >= 1)
        check(TAG .. "A1b: exactly ONE FIRING ON, naming the target and that it is in melee [live log]", lg(TAG, b))
        local c = (count_log(W3, ": 29 -> 28 of 30 at t=") == 1
          and count_log(W3, "(gap 2.00s, window 2.50s measured)") == 1)
        check(TAG .. "A1c: the second volley measures the gap 2.00 s and the window 1.25 x 2.00 = 2.50 s [live log]", lg(TAG, c))
        local d = (count_log(W3, "FIRING OFF unit 12521 'archers'") == 1
          and count_log(W3, "(no drop for 2.75s > window 2.50s)") == 1)
        check(TAG .. "A1d: 2.75 s with no drop > 2.50 s window -> exactly ONE FIRING OFF [live log]", lg(TAG, d))
        local e = (count_log(W3, ": 28 -> 30 of 30 - RESUPPLIED (not a shot)") == 1)
        check(TAG .. "A1e: the rise is a resupply, never a shot [live log]", lg(TAG, e))
        local g = (#W3.fires == 0)
        check(TAG .. "A1f: the probe casts NOTHING (" .. #W3.fires .. " fires)", g)
        done(a and lg(TAG, b) and lg(TAG, c) and lg(TAG, d) and lg(TAG, e) and g)
        tally(W3)
      end

      -- A2: two drops one poll apart = one volley
      local def2 = { name = "handgunners", uid = 12531, owns = {}, melee = false,
                     ammo_start = 20, ammo_seq = { 20, 20, 19, 18 } }
      local W4 = make_world({ can_perform = true, units = { def2 },
        cards = { { id = "12531", state = "active", vis = true } }, bar = {} })
      print("== " .. TAG .. "A2. two drops 0.25 s apart are ONE volley: the default window holds ==")
      okl = pcall(load_world, W4, f.path)
      check(TAG .. "A2: the file loads", okl)
      if okl then
        deploy_phases(W4); ui(W4)
        W4.conflict = true
        polln(W4, 16)   -- 3 s after the last drop: inside the 10 s default
        local a = (count_log(W4, ": 19 -> 18 of 20 at t=") == 1
          and count_log(W4, "(gap 0.25s, window 10s default)") == 1)
        check(TAG .. "A2a: the 0.25 s gap does NOT set the window (still the 10 s default) [live log]", lg(TAG, a))
        local b = (count_log(W4, "FIRING ON unit 12531") == 1 and count_log(W4, "FIRING OFF unit 12531") == 0)
        check(TAG .. "A2b: still FIRING, no OFF inside the default window [live log]", lg(TAG, b))
        done(lg(TAG, a) and lg(TAG, b))
        tally(W4)
      end

      -- A3: no ammunition -> read once, never again
      local def3 = { name = "swordsmen", uid = 12541, owns = {}, melee = false, ammo_start = 0, ammo_seq = { 0 } }
      local W5 = make_world({ can_perform = true, units = { def3 },
        cards = { { id = "12541", state = "active", vis = true } }, bar = {} })
      print("== " .. TAG .. "A3. a unit with no ammunition: ammo_left is never read ==")
      okl = pcall(load_world, W5, f.path)
      check(TAG .. "A3: the file loads", okl)
      if okl then
        deploy_phases(W5); ui(W5)
        W5.conflict = true
        polln(W5, 20)
        local a = (def3.ammo_reads == nil)
        check(TAG .. "A3a: ammo_left was never read (" .. tostring(def3.ammo_reads) .. ")", a)
        local b = (count_log(W5, "AMMO ") == 0 and count_log(W5, "FIRING ") == 0)
        check(TAG .. "A3b: no AMMO / FIRING line for it [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
        tally(W5)
      end
    end
  end

  if RED124 then
    check("RED CONTROL (harness 124): the pre-125 build puts a letter on the right-hand bar in both files - "
      .. n_ok .. "/" .. n_all, n_all == 2 and n_ok == 2)
  else
    check("HARNESS 124: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  end
  print("== HARNESS 124 done: " .. (checks - pre124) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
assert src.count(UNIT_ANCHOR) == 1, src.count(UNIT_ANCHOR)
src = src.replace(UNIT_ANCHOR, UNIT_ANCHOR + UNIT_ADD)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h122()\nrun_h123()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, "run_h122()\n"
                        "-- run_h123() RETIRED in round 125: it tested the round-124 spell-bar badge\n"
                        "-- PLACEMENT, removed by the user's ruling of 2026-11-03 (spell-bar buttons get no\n"
                        "-- badge at all). On the round-125 source it fails exactly its own 19 placement\n"
                        "-- checks; run_h124 proves the rule that replaced it. The function stays above.\n"
                        "run_h124()\n")
src = BANNER + src
assert "\u2014" not in BANNER + UNIT_ADD + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
