#!/usr/bin/env python3
"""Build harness126.lua from harness125.lua for round 127 (OFF window
max(2 x reload, 20 s); the target-lost fix).

  1. prepends the round-127 banner;
  2. adds an opt-in def.target_lost_after_poll to the mock unit: current_target()
     answers nil once W.poll_ticks passes it (a target that disappears);
  3. REBASES the pins the round moves, in this file's copies of the earlier
     sections (old -> new, why: the user approved max(2 x reload, 20 s)):
       constant tokens  AMMO_OFF_FACTOR = 1.25 -> = 2;  AMMO_WINDOW_DEFAULT_S = 10
                        -> AMMO_OFF_MIN_S = 20 (the default is deleted)
       F1c  OFF after 16.25 s (1.25 x 13) -> after 26 s (2 x 13); the world runs
            140 polls instead of 101 so the later OFF falls inside it
       F3b  the 10 s default -> the 20 s minimum; 95 polls instead of 50
     Run on the round-127 source, harness125 fails exactly these 7 checks (two
     token checks per section in two files, F1c, F3b, the summary) and nothing else;
  4. appends run_h126 and calls it after run_h125.
No count pin moves. Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_firing_reload_table_harness125\harness125.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_off_window_target_lost_harness126\harness126.lua"

BANNER = """-- ============================================================================
-- HARNESS 126 - ROUND 127: THE OFF WINDOW AND THE TARGET-LOST FIX (user approval
-- 2026-11-03, "Yes, both").
--   FIRING OFF after max(2 x reload, 20 s) - Land Ships, Steam Tanks and hunter
--   characters fire slower than their table reload; a unit missing from the
--   table uses the 20 s minimum. OUT OF RANGE for a target that DISAPPEARED
--   logs "target lost" instead of raising (which lost the line and skipped the
--   rest of the army for that poll).
--   Edited vs harness125: this banner, an opt-in disappearing target on the mock
--   unit, the rebased pins (see tools/make_harness126.py), run_h126 added.
--   RED control: H126_LIVE / H126_ANN on docs/backups/round127/pre127_*.lua.
-- ============================================================================
"""

MOCK_OLD = "      function u:current_target() touch(); return tobj end\n"
MOCK_NEW = """      function u:current_target()
        touch()
        -- HARNESS 126: opt-in disappearing target
        if def.target_lost_after_poll ~= nil and (W.poll_ticks or 0) > def.target_lost_after_poll then
          return nil
        end
        return tobj
      end
"""

REBASE = [
    ('"FOURTH.AMMO_OFF_FACTOR = 1.25"', '"FOURTH.AMMO_OFF_FACTOR = 2"', 2),
    ('"FOURTH.AMMO_WINDOW_DEFAULT_S = 10"', '"FOURTH.AMMO_OFF_MIN_S = 20"', 2),
    ("    local W = run(d1, f.path, TAG, 101)\n", "    local W = run(d1, f.path, TAG, 140)  -- HARNESS 126: was 101 (OFF now after 26 s)\n", 1),
    ('"(no drop for 16.50s > window 16.25s = 1.25 x reload 13s)"', '"(no drop for 26.25s > window 26.00s = 2 x reload 13s)"', 1),
    ("      local W3 = run(d3, f.path, TAG, 50)\n", "      local W3 = run(d3, f.path, TAG, 95)  -- HARNESS 126: was 50 (OFF now after 20 s)\n", 1),
    ('"(no drop for 10.25s > window 10.00s, no reload in the table: default)"',
     '"(no drop for 20.25s > window 20.00s, no reload in the table: the 20 s minimum)"', 1),
]

SECTION = r'''
-- ============================================================================
-- HARNESS 126 (round 127): THE OFF WINDOW AND THE TARGET-LOST FIX.
--   0w: tokens (OFF_FACTOR 2, OFF_MIN_S 20, the max() window, the deleted default
--       gone; the live "target lost" branch; the annotated copy log-free).
--   G1 the Land Ship's field rhythm (table 10 s, real 13.25 s): ONE episode
--      (window max(20, 20) = 20 s); round 126 split it into one per shot.
--   G2 the 20 s minimum: Witch Hunter (4 s) with shots 16 s apart: ONE episode,
--      and its OFF line names "the 20 s minimum (2 x reload 4s is shorter)".
--   G3 a target that DISAPPEARS: "OUT OF RANGE ... target lost" is logged, and the
--      unit listed AFTER it is still read on that same poll (no skipped poll).
--   RED (H126_LIVE/H126_ANN on the pre-127 build = round 126): G1 flickers and
--   G3 skips a poll (both live-log or live-read effects; the annotated copy has
--   no logging, so it neither raises nor flickers in a countable way - N/A).
-- ============================================================================
function run_h126()
  local L126 = os.getenv("H126_LIVE") or LIVE
  local A126 = os.getenv("H126_ANN") or ANN
  local RED126 = (os.getenv("H126_LIVE") ~= nil) or (os.getenv("H126_ANN") ~= nil)
  local pre126 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function cnt(s, tok)
    local n, a = 0, 1
    while true do
      local i = raw_find(s, tok, a, true)
      if i == nil then return n end
      n = n + 1
      a = i + 1
    end
  end
  local function seq_drops_every(start, first, every, count, n)
    local s, v, nxt, left = {}, start, first, count
    for r = 1, n do
      if r == nxt and left > 0 then v = v - 1; nxt = nxt + every; left = left - 1 end
      s[r] = v
    end
    return s
  end

  print("== HARNESS 126 - section 0w: the OFF window and target-lost tokens ==")
  for _, f in ipairs({ { name = "live", path = L126 }, { name = "ann", path = A126 } }) do
    local s = read_file(f.path)
    check("0w " .. f.name .. ": OFF = max(2 x reload, 20 s); the 10 s default is gone",
      raw_find(s, "FOURTH.AMMO_OFF_FACTOR = 2 ", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_OFF_MIN_S = 20 ", 1, true) ~= nil
      and raw_find(s, "if st.reload ~= nil and FOURTH.AMMO_OFF_FACTOR * st.reload > window then", 1, true) ~= nil
      and cnt(s, "AMMO_WINDOW_DEFAULT_S") == 0)
  end
  check("0w live: a disappeared target logs 'target lost' instead of formatting nil",
    raw_find(read_file(L126), "OUT OF RANGE %s at t=%.2fs: target lost (no current target)", 1, true) ~= nil)
  check("0w ann: the reading copy stays log-free", cnt(read_file(A126), "log(") == 0)

  local FILES = { { path = A126, tag = "[annotated] " }, { path = L126, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(units, PATH, TAG, polls)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = {} })
    local ok = pcall(load_world, W, PATH)
    check(TAG .. units[1].name .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.conflict = true
    polln(W, polls)
    return W
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- G1: the Land Ship's field rhythm
    local g1 = { name = "wh3_dlc25_emp_veh_marienburg_land_ship", uid = 12701, owns = {}, melee = false,
                 ammo_start = 30, ammo_seq = seq_drops_every(30, 3, 53, 4, 250) }
    print("== " .. TAG .. "G1. Land Ship (table 10 s) firing every 13.25 s: ONE episode ==")
    local W = world({ g1 }, f.path, TAG, 200)
    if W ~= nil then
      local ons = count_log(W, "FIRING ON unit 12701")
      if RED126 then
        local rep = (TAG ~= "[live] ") or ons >= 2
        check(TAG .. "G1-RED: the pre-127 build splits the Land Ship (" .. ons .. " FIRING ON) [live log]", rep)
        done(rep)
      else
        local a = (ons == 1 and count_log(W, "FIRING OFF unit 12701") == 0)
        check(TAG .. "G1a: ONE episode across four shots 13.25 s apart (" .. ons .. " FIRING ON) [live log]", lg(TAG, a))
        done(lg(TAG, a))
      end
      tally(W)
    end

    if not RED126 then
      -- G2: the 20 s minimum
      local g2 = { name = "wh_main_emp_cha_witch_hunter", uid = 12711, owns = {}, melee = false,
                   ammo_start = 50, ammo_seq = seq_drops_every(50, 3, 64, 2, 200) }
      print("== " .. TAG .. "G2. Witch Hunter (4 s) with shots 16 s apart: the 20 s minimum keeps ONE episode ==")
      local W2 = world({ g2 }, f.path, TAG, 160)
      if W2 ~= nil then
        local a = (count_log(W2, "FIRING ON unit 12711") == 1
          and count_log(W2, "(no drop for 20.25s > window 20.00s, the 20 s minimum (2 x reload 4s is shorter))") == 1)
        check(TAG .. "G2a: one episode, and OFF names the 20 s minimum [live log]", lg(TAG, a))
        done(lg(TAG, a))
        tally(W2)
      end
    end

    -- G3: a target that disappears
    local g3a = { name = "wh_main_emp_inf_handgunners", uid = 12721, owns = {}, melee = false,
                  ammo_start = 1980, ammo_seq = { 1980 },
                  ammo_target = { type = "wh_main_vmp_inf_zombie", melee = false },
                  missile_range = 150, dist = 120, target_lost_after_poll = 10 }
    local g3b = { name = "wh_main_emp_inf_crossbowmen", uid = 12722, owns = {}, melee = false,
                  ammo_start = 1980, ammo_seq = { 1980 } }
    print("== " .. TAG .. "G3. the target disappears: 'target lost', and the next unit is still read that poll ==")
    -- the control: the same two units, the target never disappears -> how many
    -- probe reads the second unit gets in 20 polls when nothing is skipped
    local c3a = { name = "wh_main_emp_inf_handgunners", uid = 12723, owns = {}, melee = false,
                  ammo_start = 1980, ammo_seq = { 1980 },
                  ammo_target = { type = "wh_main_vmp_inf_zombie", melee = false },
                  missile_range = 150, dist = 120 }
    local c3b = { name = "wh_main_emp_inf_crossbowmen", uid = 12724, owns = {}, melee = false,
                  ammo_start = 1980, ammo_seq = { 1980 } }
    local WC = world({ c3a, c3b }, f.path, TAG, 20)
    local want = (WC ~= nil) and (c3b.ammo_reads or 0) or -1
    if WC ~= nil then tally(WC) end
    local W3 = world({ g3a, g3b }, f.path, TAG, 20)
    if W3 ~= nil then
      local reads = g3b.ammo_reads or 0
      if RED126 then
        local rep = (TAG ~= "[live] ") or reads == want - 1
        check(TAG .. "G3-RED: the pre-127 build skips the next unit for one poll (" .. reads .. " reads, control "
          .. want .. ") [live]", rep)
        done(rep)
      else
        local a = (count_log(W3, "OUT OF RANGE unit 12721") == 1
          and count_log(W3, ": target lost (no current target)") == 1)
        check(TAG .. "G3a: 'target lost' is logged once [live log]", lg(TAG, a))
        local b = (want > 0 and reads == want)
        check(TAG .. "G3b: the unit after it was read on every probe poll (" .. reads .. ", control " .. want .. ")", b)
        done(lg(TAG, a) and b)
      end
      tally(W3)
    end
  end

  if RED126 then
    check("RED CONTROL (harness 126): the pre-127 build flickers on the Land Ship and skips a poll on a lost target - "
      .. n_ok .. "/" .. n_all, n_all == 4 and n_ok == 4)
  else
    check("HARNESS 126: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 126 done: " .. (checks - pre126) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
assert src.count(MOCK_OLD) == 1
src = src.replace(MOCK_OLD, MOCK_NEW)
for a, b, want in REBASE:
    n = src.count(a)
    assert n == want, (a[:60], n, want)
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h124()\nrun_h125()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h126()\n")
src = BANNER + src
assert "\u2014" not in BANNER + MOCK_NEW + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
