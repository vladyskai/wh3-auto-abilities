#!/usr/bin/env python3
"""Build harness128.lua from harness127.lua for round 129 (the unit cards veto a
ghost selection). No pin moves expected. Older harnesses are never edited."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_ready_on_screen_harness127\harness127.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_card_veto_harness128\harness128.lua"

BANNER = """-- ============================================================================
-- HARNESS 128 - ROUND 129: THE UNIT CARDS VETO A GHOST SELECTION.
--   After a box selection the engine may never send the "deselected" events, so
--   units stay in selected_ui_ids for the rest of the battle and fix A never sees
--   "exactly one selected" (field battle 3, 2026-11-03). A unit whose own card
--   reads unselected for 2 polls is now dropped from the set.
--   Edited vs harness127: this banner, run_h128 and its call. No pin moves.
--   RED control: H128_LIVE / H128_ANN on docs/backups/round129/pre129_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 128 (round 129): THE UNIT CARDS VETO A GHOST SELECTION.
--   0x: tokens (the constants, the veto loop in both files, the log line live).
--   G1 the field case: Null Stone lord + two other units box-selected (three
--      selection events), then the lord clicked alone - NO deselection events
--      arrive, the two other cards read 'active'. The button stays READY after
--      the cast -> the ghosts are dropped, fix A releases: 2 casts in 5 s.
--   G2 a TRUE group selection (all three cards keep reading 'selected') ->
--      nothing is dropped, fix A stays off: ONE cast.
--   G3 a fresh selection whose card lags for ONE poll ('active', then
--      'selected') -> it is kept (the 2-poll confirmation).
--   RED (pre-129 build = round 128): G1 casts only ONCE (the field bug).
-- ============================================================================
function run_h128()
  local L128 = os.getenv("H128_LIVE") or LIVE
  local A128 = os.getenv("H128_ANN") or ANN
  local RED128 = (os.getenv("H128_LIVE") ~= nil) or (os.getenv("H128_ANN") ~= nil)
  local NS = "wh3_dlc27_item_abilities_null_stone"
  local pre128 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 128 - section 0x: the card veto tokens ==")
  if not RED128 then
    for _, f in ipairs({ { name = "live", path = L128 }, { name = "ann", path = A128 } }) do
      local s = read_file(f.path)
      check("0x " .. f.name .. ": the 2-poll confirmation and its memory exist",
        raw_find(s, "FOURTH.CARD_DESELECT_CONFIRM_POLLS = 2", 1, true) ~= nil
        and raw_find(s, "FOURTH.card_unselected_since = {}", 1, true) ~= nil)
      check("0x " .. f.name .. ": only a KNOWN unselected card state is evidence",
        raw_find(s, "FOURTH.CARD_UNSELECTED_STATES = { active = true, hover = true, inactive = true, taking_damage = true, wavering = true }", 1, true) ~= nil
        and raw_find(s, "if st ~= nil and FOURTH.CARD_UNSELECTED_STATES[st] == true then", 1, true) ~= nil
        and raw_find(s, "elseif (tick_count - since) >= FOURTH.CARD_DESELECT_CONFIRM_POLLS then", 1, true) ~= nil)
    end
    local s = read_file(L128)
    check("0x live: the drop is logged",
      raw_find(s, "the game never sent its deselection; dropped from the selected set", 1, true) ~= nil)
  end
  do
    local a = read_file(A128)
    local n, at = 0, 1
    while true do local i = raw_find(a, "log(", at, true); if i == nil then break end; n = n + 1; at = i + 1 end
    check("0x ann: the reading copy stays log-free (" .. n .. ")", n == 0)
  end

  local FILES = { { path = A128, tag = "[annotated] " }, { path = L128, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end

  -- uid owns Null Stone; uid+1 and uid+2 own nothing of ours
  local function g_world(PATH, TAG, uid, mode, wname)
    local units = { { name = "lord", uid = uid, owns = { NS }, melee = true },
                    { name = "g1", uid = uid + 1, owns = {}, melee = false },
                    { name = "g2", uid = uid + 2, owns = {}, melee = false } }
    local cards = { { id = tostring(uid), state = "active", vis = true },
                    { id = tostring(uid + 1), state = "active", vis = true },
                    { id = tostring(uid + 2), state = "active", vis = true } }
    local W = make_world({ can_perform = true, units = units, cards = cards,
      bar = { { id = "b1", key = NS } } })
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    -- arm the lord alone first
    W.card_comps[tostring(uid)].state = "selected"
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_null_stone"); ui(W)
    if mode == "lag" then
      -- G3: the lord deselected, then selected again; its card lags one poll
      sel_event(W, uid, false); W.card_comps[tostring(uid)].state = "active"; ui(W); ui(W)
      sel_event(W, uid, true)
      W.button_parent._kids[1].state = "active"
      W.conflict = true
      polln(W, 1); ui(W)                                    -- card still 'active'
      W.card_comps[tostring(uid)].state = "selected"
      for _ = 1, 20 do polln(W, 1); ui(W) end
      return W
    end
    -- the box selection: all three cards and all three events
    for k = 0, 2 do
      W.card_comps[tostring(uid + k)].state = "selected"
      sel_event(W, uid + k, true)
    end
    ui(W); ui(W)
    if mode == "ghost" then
      -- the lord clicked alone: the cards change, NO deselection events arrive
      W.card_comps[tostring(uid + 1)].state = "active"
      W.card_comps[tostring(uid + 2)].state = "active"
      sel_event(W, uid, true)
    end
    W.button_parent._kids[1].state = "active"
    W.conflict = true
    for _ = 1, 20 do polln(W, 1); ui(W) end   -- 5 s, a ui tick after every poll
    return W
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    print("== " .. TAG .. "G1. box-select three, click the lord alone, no deselection events -> the ghosts go, fix A works ==")
    local W = g_world(f.path, TAG, 12901, "ghost", "G1")
    if W ~= nil then
      if RED128 then
        local rep = (#W.fires == 1)
        check(TAG .. "G1-RED: the pre-129 build keeps the ghosts - ONE cast, the hold never released (" .. #W.fires .. ")", rep)
        done(rep)
      else
        local a = (#W.fires == 2)
        check(TAG .. "G1a: two casts in 5 s - the ghosts are dropped and the hold is released (" .. #W.fires .. ")", a)
        local b = (count_log(W, "selection: card 12902 reads 'active' - the game never sent its deselection") == 1
          and count_log(W, "selection: card 12903 reads 'active' - the game never sent its deselection") == 1
          and count_log(W, "selection: card 12901 reads") == 0
          and count_log(W, "charge gate null_stone: unit 12901 is selected and its button reads 'active' (READY)") == 1)
        check(TAG .. "G1b: each ghost dropped once, the lord never, the release logged once [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(W)
    end

    if not RED128 then
      print("== " .. TAG .. "G2. a TRUE group selection (all cards keep 'selected') -> nothing dropped, the hold stays ==")
      local W2 = g_world(f.path, TAG, 12911, "group", "G2")
      if W2 ~= nil then
        local a = (#W2.fires == 1 and count_log(W2, "the hold is released") == 0
          and count_log(W2, "the game never sent its deselection") == 0)
        check(TAG .. "G2a: ONE cast, nothing dropped (" .. #W2.fires .. ")", a)
        done(a)
        tally(W2)
      end
      print("== " .. TAG .. "G3. a fresh selection whose card lags one poll -> kept ==")
      local W3 = g_world(f.path, TAG, 12921, "lag", "G3")
      if W3 ~= nil then
        local drops = count_log(W3, "selection: card 12921 reads")
        local a = (drops == 0 and #W3.fires >= 1)
        check(TAG .. "G3a: the lagging card does not drop the lord (" .. drops .. " drops, " .. #W3.fires .. " casts)", a)
        done(a)
        tally(W3)
      end
    end
  end

  if RED128 then
    check("RED CONTROL (harness 128): the pre-129 build keeps the ghost selection - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 128: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 128 done: " .. (checks - pre128) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h126()\nrun_h127()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h128()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
