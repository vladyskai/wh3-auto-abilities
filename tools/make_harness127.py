#!/usr/bin/env python3
"""Build harness127.lua from harness126.lua for round 128 (fix A for dropped
multi-use casts; the read-only NOT FIRING snapshot). No pin moves: harness126
runs 5,472 / 0 on the round-128 source. Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_off_window_target_lost_harness126\harness126.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_ready_on_screen_harness127\harness127.lua"

BANNER = """-- ============================================================================
-- HARNESS 127 - ROUND 128: FIX A AND THE NOT FIRING SNAPSHOT.
--   (A) a charge hold is released when the caster is the SELECTED unit, at
--       least wind-up + 3 s after the cast, and the ability's own button reads
--       'active' / 'hover' (READY): the cast did not take (Isha's Rain, field
--       battle 2026-11-03). (B) a read-only NOT FIRING line per idle ranged unit,
--       logged only when its readable reasons change.
--   Edited vs harness126: this banner, run_h127 and its call. No pin moves.
--   RED control: H127_LIVE / H127_ANN on docs/backups/round128/pre128_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 127 (round 128): FIX A AND THE NOT FIRING SNAPSHOT.
--   0x: tokens (the release helper, its settle constant, the hold branch in both
--       files; the snapshot function, its cadence and its call in the live file).
--   H1 Null Stone (3 uses, 120 s hold), unit SELECTED, its button stays 'active'
--      (READY) after the cast -> the hold is released ~3 s later and it casts
--      again: 2 casts in 5 s, the release logged.
--   H2 the same, button 'inactive' (recharging, the cast took) -> ONE cast.
--   H3 the same, button 'active' but ANOTHER unit selected -> ONE cast.
--   H4 the same, button 'active' and NOTHING selected -> ONE cast (the mod's
--      tracker keeps the last unit; only the engine's live selection is trusted).
--   N1 an idle crossbow unit: target OUT of range, then in range -> exactly two
--      NOT FIRING lines (one per change), the first naming the distance.
--   N2 a firing unit logs no NOT FIRING line after its FIRING ON.
--   RED (H127_LIVE/H127_ANN on the pre-128 build = round 127): H1 casts only
--   ONCE (the field bug); N1 logs nothing (live).
-- ============================================================================
function run_h127()
  local L127 = os.getenv("H127_LIVE") or LIVE
  local A127 = os.getenv("H127_ANN") or ANN
  local RED127 = (os.getenv("H127_LIVE") ~= nil) or (os.getenv("H127_ANN") ~= nil)
  local NS = "wh3_dlc27_item_abilities_null_stone"
  local pre127 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 127 - section 0x: fix A and NOT FIRING tokens ==")
  for _, f in ipairs({ { name = "live", path = L127 }, { name = "ann", path = A127 } }) do
    local s = read_file(f.path)
    check("0x " .. f.name .. ": the release helper and its 3 s settle exist",
      raw_find(s, "function FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)", 1, true) ~= nil
      and raw_find(s, "FOURTH.CHARGE_RELEASE_SETTLE_S = 3", 1, true) ~= nil
      and raw_find(s, "return (s == \"active\" or s == \"hover\"), s, since_s", 1, true) ~= nil)
    check("0x " .. f.name .. ": only the button of the ONE unit the engine reports selected is trusted",
      raw_find(s, "if #selected_ui_ids ~= 1 or tostring(selected_ui_ids[1]) ~= tostring(ui_id) then return false end", 1, true) ~= nil)
  end
  do
    local s = read_file(L127)
    check("0x live: the NOT FIRING snapshot exists, once a second, and is called for non-firing units",
      raw_find(s, "function FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)", 1, true) ~= nil
      and raw_find(s, "FOURTH.NOT_FIRING_EVERY_N_POLLS = 4", 1, true) ~= nil
      and raw_find(s, "if not st.firing and (tick_count % FOURTH.NOT_FIRING_EVERY_N_POLLS) == 0 then", 1, true) ~= nil)
    local a = read_file(A127)
    local n, at = 0, 1
    while true do local i = raw_find(a, "log(", at, true); if i == nil then break end; n = n + 1; at = i + 1 end
    check("0x ann: the reading copy stays log-free (" .. n .. ")", n == 0)
  end

  local FILES = { { path = A127, tag = "[annotated] " }, { path = L127, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end

  -- H: Null Stone under a charge hold, the button state set by the world
  local function h_world(PATH, TAG, uid, button_state, deselect, wname)
    -- deselect: ANOTHER unit (uid + 5, owning nothing of ours) is selected after arming
    local units = { { name = "lord", uid = uid, owns = { NS }, melee = true } }
    local cards = { { id = tostring(uid), state = "active", vis = true } }
    if deselect == "other" then
      units[2] = { name = "other", uid = uid + 5, owns = {}, melee = false }
      cards[2] = { id = tostring(uid + 5), state = "active", vis = true }
    end
    local W = make_world({ can_perform = true, units = units, cards = cards,
      bar = { { id = "b1", key = NS } } })
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_null_stone"); ui(W)
    if deselect == "none" then
      sel_event(W, uid, false); ui(W); ui(W)
    elseif deselect == "other" then
      sel_event(W, uid, false)
      W.card_comps[tostring(uid)].state = "active"
      W.card_comps[tostring(uid + 5)].state = "selected"
      sel_event(W, uid + 5, true); ui(W); ui(W)
    end
    W.button_parent._kids[1].state = button_state
    W.conflict = true
    polln(W, 20)   -- 5 s
    return W
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    print("== " .. TAG .. "H1. Null Stone, selected, button stays READY after the cast -> the hold is released ==")
    local W = h_world(f.path, TAG, 12801, "active", false, "H1")
    if W ~= nil then
      if RED127 then
        local rep = (#W.fires == 1)
        check(TAG .. "H1-RED: the pre-128 build holds the full 120 s - ONE cast (" .. #W.fires .. ")", rep)
        done(rep)
      else
        local a = (#W.fires == 2)
        check(TAG .. "H1a: two casts in 5 s - the dropped cast is retried (" .. #W.fires .. ")", a)
        local b = (count_log(W, "charge gate null_stone: unit 12801 is selected and its button reads 'active' (READY)") == 1
          and count_log(W, "after the last cast - that cast did not take; the hold is released") == 1)
        check(TAG .. "H1b: the release is logged once [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(W)
    end

    if not RED127 then
      print("== " .. TAG .. "H2. button 'inactive' (the cast took) -> the hold stays ==")
      local W2 = h_world(f.path, TAG, 12811, "inactive", false, "H2")
      if W2 ~= nil then
        local a = (#W2.fires == 1 and count_log(W2, "the hold is released") == 0)
        check(TAG .. "H2a: ONE cast, no release (" .. #W2.fires .. ")", a)
        done(a)
        tally(W2)
      end
      print("== " .. TAG .. "H3. button 'active' but the unit NOT selected -> the hold stays ==")
      local W3 = h_world(f.path, TAG, 12821, "active", "other", "H3")
      if W3 ~= nil then
        local a = (#W3.fires == 1 and count_log(W3, "the hold is released") == 0)
        check(TAG .. "H3a: ONE cast - with another unit selected the button is not trusted (" .. #W3.fires .. ")", a)
        done(a)
        tally(W3)
      end
      print("== " .. TAG .. "H4. button 'active' but NOTHING selected (the tracker keeps the last unit) -> the hold stays ==")
      local W4 = h_world(f.path, TAG, 12826, "active", "none", "H4")
      if W4 ~= nil then
        local a = (#W4.fires == 1 and count_log(W4, "the hold is released") == 0)
        check(TAG .. "H4a: ONE cast - with nothing selected the button is not trusted (" .. #W4.fires .. ")", a)
        done(a)
        tally(W4)
      end
    end

    -- N1: an idle crossbow unit, target out of range then in range
    local dist = {}
    for r = 1, 60 do dist[r] = (r <= 20) and 200 or 120 end
    local n1 = { name = "wh_main_emp_inf_crossbowmen", uid = 12831, owns = {}, melee = false,
                 ammo_start = 1980, ammo_seq = { 1980 },
                 ammo_target = { type = "wh_main_vmp_inf_zombie", melee = true },
                 missile_range = 150, dist_seq = dist }
    local WN = make_world({ can_perform = true, units = { n1 },
      cards = { { id = "12831", state = "active", vis = true } }, bar = {} })
    print("== " .. TAG .. "N1. an idle crossbow unit: one NOT FIRING line per change of reasons ==")
    local okn = pcall(load_world, WN, f.path)
    check(TAG .. "N1: the file loads", okn)
    if okn then
      deploy_phases(WN); ui(WN)
      WN.conflict = true
      polln(WN, 40)
      local n = count_log(WN, "NOT FIRING unit 12831")
      if RED127 then
        local rep = (TAG ~= "[live] ") or n == 0
        check(TAG .. "N1-RED: the pre-128 build says nothing about why (" .. n .. " lines) [live log]", rep)
        done(rep)
      else
        local a = (n == 2
          and count_log(WN, "target=wh_main_vmp_inf_zombie (OUT of range) target_in_melee=yes") == 1
          and count_log(WN, "[distance 200.0m, range 150.0m]") == 1
          and count_log(WN, "target=wh_main_vmp_inf_zombie (in range) target_in_melee=yes") == 1)
        check(TAG .. "N1a: exactly two lines: OUT of range (200 m vs 150 m), then in range (" .. n .. ") [live log]", lg(TAG, a))
        local b = (#WN.fires == 0)
        check(TAG .. "N1b: nothing is cast (" .. #WN.fires .. ")", b)
        done(lg(TAG, a) and b)
      end
      tally(WN)
    end

    if not RED127 then
      -- N2: a firing unit stays quiet after FIRING ON
      local seq = {}
      for r = 1, 60 do seq[r] = 1980 - 2 * (r - 1) end
      local n2 = { name = "wh_main_emp_inf_handgunners", uid = 12841, owns = {}, melee = false,
                   ammo_start = 1980, ammo_seq = seq }
      local W2n = make_world({ can_perform = true, units = { n2 },
        cards = { { id = "12841", state = "active", vis = true } }, bar = {} })
      print("== " .. TAG .. "N2. a firing unit logs no NOT FIRING line after FIRING ON ==")
      local ok2 = pcall(load_world, W2n, f.path)
      check(TAG .. "N2: the file loads", ok2)
      if ok2 then
        deploy_phases(W2n); ui(W2n)
        W2n.conflict = true
        polln(W2n, 40)
        local on_at, late = nil, 0
        for i = 1, #W2n.log_lines do
          local l = W2n.log_lines[i]
          if on_at == nil and raw_find(l, "FIRING ON unit 12841", 1, true) then on_at = i end
          if on_at ~= nil and raw_find(l, "NOT FIRING unit 12841", 1, true) then late = late + 1 end
        end
        local a = (on_at ~= nil and late == 0)
        check(TAG .. "N2a: no NOT FIRING line after FIRING ON (" .. late .. ") [live log]", lg(TAG, a))
        done(lg(TAG, a))
        tally(W2n)
      end
    end
  end

  if RED127 then
    check("RED CONTROL (harness 127): the pre-128 build holds a dropped cast for the full recharge - "
      .. n_ok .. "/" .. n_all, n_all == 4 and n_ok == 4)
  else
    check("HARNESS 127: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  end
  print("== HARNESS 127 done: " .. (checks - pre127) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h125()\nrun_h126()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h127()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
