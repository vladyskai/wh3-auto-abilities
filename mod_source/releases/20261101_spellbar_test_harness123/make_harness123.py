#!/usr/bin/env python3
"""Build harness123.lua from harness122.lua for round 124 (the spell-bar badge test).

  1. prepends the round-124 banner;
  2. adds an OPT-IN spell bar to the mock world (opts.spellbar): each button
     alone under its own parent - the in-game shape the field log showed - with
     a readable Position() ONLY on these components, so every earlier world's
     tree, visit counts and reads stay byte-identical;
  3. points the two earlier sections that read army_spec.tsv at the project's
     gamedata\\wh3 copy instead of %LOCALAPPDATA%\\Temp (Temp gets cleaned);
  4. appends run_h123 and calls it after run_h122.
No count pin moves: the round adds no ABILITIES entry (harness 122 ran 5,359 / 0
on the round-124 source before this file existed). Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_hex_batch_harness122\harness122.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_spellbar_test_harness123\harness123.lua"
OLD_ARMY = "C:/Users/vlady/AppData/Local/Temp/wh3/army_spec.tsv"
NEW_ARMY = "C:/Users/vlady/Desktop/WH3_mod/gamedata/wh3/army_spec.tsv"

BANNER = """-- ============================================================================
-- HARNESS 123 - ROUND 124, THE SPELL-BAR BADGE TEST (user request 2026-11-01:
-- "is it possible to add this letter on the right side or not?").
--   Field bug (2026-10-28): a Rune Smith's runes sit on the SPELL bar
--   (button_spell, button_spell2, ...), each alone under its own parent, so the
--   bar ordinal said 1 for every rune and all rune badges were drawn on WHEEL
--   SLOT 1 - on top of the Hammer of Karak Drazh's badge ('M' under 'A').
--   The test: a spell-bar button gets no wheel slot; its badge offset comes from
--   the button's own Position() (the wheel-slot formula), plus a read-only
--   SPELLBAR line per spell-bar ability in the inventory sweep.
--   Edited vs harness122: this banner, the opt-in spell bar in make_world, the
--   army_spec path (now gamedata\\wh3), run_h123 and its call. No pin moves.
--   RED control: H123_LIVE / H123_ANN on docs/backups/round124/pre124_*.lua.
-- ============================================================================
"""

WORLD_ANCHOR = "  W.wheel_kids = wheel_kids\n"
WORLD_ADD = """
  -- HARNESS 123: an OPT-IN SPELL BAR - each button alone under its own parent
  -- (the in-game shape: button_spell, button_spell2, ... each the only
  -- key-bearing child of its parent), with Position() defined ONLY on these
  -- components (e.x / e.parent_x), so no earlier world changes at all.
  W.spell_kids = {}
  if opts.spellbar and #opts.spellbar > 0 then
    local spell_root = make_comp({ id = "spell_bar_root" })
    local spell_parents = {}
    for i, e in ipairs(opts.spellbar) do
      local p = make_comp({ id = "spell_slot_" .. i, px = e.parent_x, py = e.parent_y })
      local c = make_comp({ id = e.id, vis = e.vis, px = e.x, py = e.y })
      if e.x ~= nil then function c:Position() return c.px, c.py end end
      if e.parent_x ~= nil then function p:Position() return p.px, p.py end end
      if e.key ~= nil then W.ability_keys[e.id] = e.key end
      p._kids = { c }
      c.parent = p
      p.parent = spell_root
      spell_parents[i] = p
      W.spell_kids[i] = c
    end
    spell_root._kids = spell_parents
    spell_root.parent = battle_orders
    battle_orders._kids[#battle_orders._kids + 1] = spell_root
  end
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 123 (round 124): THE SPELL-BAR BADGE TEST.
--   0t: tokens in BOTH files (the switch, the spell-bar map, the offset branch,
--       the claim branch); the SPELLBAR sweep line in the live file; the
--       annotated copy stays log-free.
--   S1 THE FIELD CASE: a Rune Smith with the Hammer (wheel, bar position 1) and
--      Rune of Slowness on 'button_spell4' at (1300,1000). The Hammer badge keeps
--      wheel slot 1 (-865,-209); the rune badge gets (-865+1300-96, -209+1000-845)
--      = (339,-54): the two NO LONGER share a spot.
--   S2 the bar moves to (1400,1000) -> the rune badge follows: (439,-54).
--   S3 Position() unreadable -> the fallback offset, logged as such.
--   S4 the read-only SPELLBAR line (button, visibility, position, parent).
--   S5 a wheel-only Rune Smith: exactly the old wheel behaviour, no spell lines.
--   RED (H123_LIVE/H123_ANN on the pre-124 snapshot): S1 reproduces the field
--   bug - the rune badge is placed on the Hammer's own offset (-865,-209).
-- ============================================================================
function run_h123()
  local L123 = os.getenv("H123_LIVE") or LIVE
  local A123 = os.getenv("H123_ANN") or ANN
  local RED123 = (os.getenv("H123_LIVE") ~= nil) or (os.getenv("H123_ANN") ~= nil)
  local HAMMER = "wh_main_weapon_abilities_the_hammer_of_karak_drazh"
  local RUNE = "wh2_dlc17_rune_abilities_rune_of_slowness"
  local B_HAM = "zz_auto_badge_the_hammer_of_karak_drazh"
  local B_RUNE = "zz_auto_badge_rune_of_slowness"
  local pre123 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function rec_of(W, name)
    local hit = nil
    for i = 1, #(W.created or {}) do
      local r = W.created[i]
      if r.name == name and not r.destroyed then hit = r end
    end
    return hit
  end
  local function off(r) if r == nil then return "nil" end return "(" .. tostring(r.offset[1]) .. "," .. tostring(r.offset[2]) .. ")" end
  local function at(r, x, y) return r ~= nil and r.offset[1] == x and r.offset[2] == y end

  -- ------------------------------------------------------------------ 0t
  print("== HARNESS 123 - section 0t: the spell-bar badge test tokens ==")
  for _, f in ipairs({ { name = "live", path = L123 }, { name = "ann", path = A123 } }) do
    local s = read_file(f.path)
    check("0t " .. f.name .. ": the test switch and the spell-bar map exist",
      raw_find(s, "FOURTH.SPELLBAR_BADGES = true", 1, true) ~= nil
      and raw_find(s, "FOURTH.spellbar_id = {}", 1, true) ~= nil)
    check("0t " .. f.name .. ": the offset comes from the spell button's own Position (the wheel-slot formula)",
      raw_find(s, "return BADGE_X + (px - WHEEL_TOP_X), BADGE_Y + (py - WHEEL_TOP_Y), \"spell\", px, py", 1, true) ~= nil)
    check("0t " .. f.name .. ": a 'button_spell...' claim takes no wheel slot",
      raw_find(s, "string.sub(id, 1, 12) == \"button_spell\"", 1, true) ~= nil
      and raw_find(s, "if spell_id == nil then k = bar_ordinal_for(uic, ability) end", 1, true) ~= nil)
  end
  do
    local s = read_file(L123)
    check("0t live: the read-only SPELLBAR sweep line exists",
      raw_find(s, "log(\"SPELLBAR \" .. ability.marker .. \": button='\" .. sid", 1, true) ~= nil)
    local a = read_file(A123)
    local n = 0
    local at0 = 1
    while true do
      local i = raw_find(a, "log(", at0, true)
      if i == nil then break end
      n = n + 1
      at0 = i + 1
    end
    check("0t ann: the reading copy stays log-free (" .. n .. " 'log(' found)", n == 0)
  end

  local FILES = { { path = A123, tag = "[annotated] " }, { path = L123, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function boot(W, PATH, TAG, uid, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true)
    for _ = 1, 4 do ui(W) end
    return true
  end
  local function world_rs(opts_spell, bar)
    return make_world({ can_perform = true,
      units = { { name = "rune_smith", uid = 12401, owns = { HAMMER, RUNE }, melee = false } },
      cards = { { id = "12401", state = "selected", vis = true } },
      bar = bar or { { id = "button_order1", key = HAMMER } },
      spellbar = opts_spell })
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- S1 + S2 + S4
    local W = world_rs({ { id = "button_spell4", key = RUNE, x = 1300, y = 1000, parent_x = 1290, parent_y = 990 } })
    print("== " .. TAG .. "S1. Rune Smith: Hammer on the wheel, Rune of Slowness on the spell bar ==")
    if boot(W, f.path, TAG, 12401, "S1") then
      local h, r = rec_of(W, B_HAM), rec_of(W, B_RUNE)
      if RED123 then
        local rep = at(h, -865, -209) and at(r, -865, -209)
        check(TAG .. "S1-RED: the pre-124 build reproduces the field bug - the rune badge sits ON the Hammer's "
          .. "offset (hammer " .. off(h) .. ", rune " .. off(r) .. ")", rep)
        n_all = n_all + 1
        if rep then n_ok = n_ok + 1 end
      else
        local a = at(h, -865, -209)
        check(TAG .. "S1a: the Hammer badge keeps wheel slot 1 " .. off(h), a)
        local b = at(r, 339, -54)
        check(TAG .. "S1b: the rune badge is placed from the spell button's own position (1300,1000) -> "
          .. off(r) .. " (want (339,-54))", b)
        local c = (h ~= nil and r ~= nil and (h.offset[1] ~= r.offset[1] or h.offset[2] ~= r.offset[2]))
        check(TAG .. "S1c: the two badges NO LONGER share a spot (the 'M' under 'A' is gone)", c)
        local d = (count_log(W, "claim: rune_of_slowness is a SPELL-BAR button ('button_spell4')") >= 1
          and count_log(W, "[SPELL-BAR button 'button_spell4' at (1300,1000)]") >= 1)
        check(TAG .. "S1d: the claim and the placement say SPELL-BAR [live log]", lg(TAG, d))
        local e = (count_log(W, "claim: the_hammer_of_karak_drazh is bar position 1 -> wheel slot (96,845)") >= 1)
        check(TAG .. "S1e: the Hammer's claim is the old wheel claim, unchanged [live log]", lg(TAG, e))
        -- S2: the bar moves; the badge follows on the next ui tick
        W.spell_kids[1].px = 1400
        ui(W)
        local g = at(rec_of(W, B_RUNE), 439, -54)
        check(TAG .. "S2: the spell button moved to (1400,1000) -> the rune badge follows " .. off(rec_of(W, B_RUNE))
          .. " (want (439,-54))", g)
        -- S4: the read-only SPELLBAR line (the sweep runs on the UI tick once
        -- 4 poll ticks have passed since the last one)
        polln(W, 5)
        ui(W)
        local s4 = (count_log(W, "SPELLBAR rune_of_slowness: button='button_spell4' visible=true pos=(1400,1000)") >= 1
          and count_log(W, "parent='spell_slot_1' parent_pos=(1290,990)") >= 1)
        check(TAG .. "S4: the SPELLBAR line reports the button, its position and its parent [live log]", lg(TAG, s4))
        local ok = a and b and c and lg(TAG, d) and lg(TAG, e) and g and lg(TAG, s4)
        n_all = n_all + 1
        if ok then n_ok = n_ok + 1 end
      end
      check(TAG .. "S1: every ui tick ran clean (" .. (W.ui_failures or 0) .. ")", (W.ui_failures or 0) == 0)
      tally(W)
    end

    if not RED123 then
      -- S3: Position() unreadable -> fallback
      local W3 = world_rs({ { id = "button_spell4", key = RUNE } })
      print("== " .. TAG .. "S3. the spell button's Position() cannot be read -> the fallback offset ==")
      if boot(W3, f.path, TAG, 12401, "S3") then
        local r = rec_of(W3, B_RUNE)
        local a = at(r, -865, -209)
        check(TAG .. "S3a: unreadable position -> the rune entry's fallback offset " .. off(r), a)
        local b = (count_log(W3, "badge rune_of_slowness: using fallback offset (-865,-209)") >= 1)
        check(TAG .. "S3b: the fallback is logged as a fallback [live log]", lg(TAG, b))
        n_all = n_all + 1
        if a and lg(TAG, b) then n_ok = n_ok + 1 end
        tally(W3)
      end

      -- S5: wheel only - the old behaviour, nothing spell-bar
      local W5 = make_world({ can_perform = true,
        units = { { name = "rune_smith", uid = 12405, owns = { HAMMER }, melee = false } },
        cards = { { id = "12405", state = "selected", vis = true } },
        bar = { { id = "button_order1", key = HAMMER } } })
      print("== " .. TAG .. "S5. a wheel-only Rune Smith: exactly the old wheel behaviour ==")
      if boot(W5, f.path, TAG, 12405, "S5") then
        local h = rec_of(W5, B_HAM)
        local a = at(h, -865, -209)
        check(TAG .. "S5a: the Hammer badge on wheel slot 1 " .. off(h), a)
        local b = (count_log(W5, "SPELL-BAR") == 0 and count_log(W5, "SPELLBAR ") == 0)
        check(TAG .. "S5b: no spell-bar line at all in a wheel-only world [live log]", lg(TAG, b))
        n_all = n_all + 1
        if a and lg(TAG, b) then n_ok = n_ok + 1 end
        tally(W5)
      end
    end
  end

  if RED123 then
    check("RED CONTROL (harness 123): the pre-124 build reproduces the overlap in both files - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 123: every spell-bar world behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 123 done: " .. (checks - pre123) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
assert src.count(WORLD_ANCHOR) == 1, src.count(WORLD_ANCHOR)
src = src.replace(WORLD_ANCHOR, WORLD_ANCHOR + WORLD_ADD)
n_army = src.count(OLD_ARMY)
assert n_army == 2, n_army
src = src.replace(OLD_ARMY, NEW_ARMY)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h121()\nrun_h122()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, "run_h121()\nrun_h122()\nrun_h123()\n")
src = BANNER + src
assert "\u2014" not in BANNER + WORLD_ADD + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes; army_spec path repointed x%d" % n_army)
