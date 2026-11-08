#!/usr/bin/env python3
"""Build harness125.lua from harness124.lua for round 126 (the firing flag from the
game's reload table, the cast point, the in-range log).

  1. prepends the round-126 banner;
  2. adds an opt-in def.missile_range to the mock unit (missile_range());
  3. in THIS file's copy of run_h124, retires the checks that pinned the deleted
     round-125 window rule (1.25 x the last measured gap; drops < 1 s = one volley):
       0u   the constant tokens -> AMMO_OFF_FACTOR replaces AMMO_WINDOW_FACTOR +
            AMMO_SAME_VOLLEY_S
       A1c  "the second volley measures the gap 2.00 s, window 2.50 s"   -> retired
       A1d  "2.75 s with no drop > 2.50 s window -> one FIRING OFF"       -> retired
       A2a  "the 0.25 s gap does NOT set the window (10 s default)"       -> retired
     Run on the round-126 source, harness124 fails exactly these 6 checks (the two
     0u tokens counted per file, the summary line) and nothing else;
  4. appends run_h125 and calls it after run_h124.
No count pin moves. Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_spellbar_rule_ammo_probe_harness124\harness124.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_firing_reload_table_harness125\harness125.lua"

BANNER = """-- ============================================================================
-- HARNESS 125 - ROUND 126: THE FIRING FLAG FROM THE GAME'S RELOAD TABLE.
--   User rulings 2026-11-03: a baked stat is allowed when the engine has no
--   live read (rule 4 relaxed); reload = base x (1 - reload skill / 100) from a
--   GENERATED table (FOURTH.RELOAD_S); FIRING OFF after 1.25 x reload; a CAST
--   POINT at first shot + 0.5 x reload (logged, nothing cast); the moment the
--   target enters the unit's own missile range is logged, and FIRING ON says how
--   long before the first shot it came.
--   Edited vs harness124: this banner, opt-in missile_range on the mock unit,
--   the round-125 window checks retired in this file's copy of run_h124 (see
--   tools/make_harness125.py), run_h125 added.
--   RED control: H125_LIVE / H125_ANN on docs/backups/round126/pre126_*.lua.
-- ============================================================================
"""

MOCK_ANCHOR = "    if def.ammo_target ~= nil then\n"
MOCK_ADD = """    -- HARNESS 125: opt-in missile range (the in-range predictor reads it).
    if def.missile_range ~= nil then
      function u:missile_range() touch(); return def.missile_range end
    end
"""

RETIRE = [
    ("""      and raw_find(s, "FOURTH.AMMO_WINDOW_FACTOR = 1.25", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_SAME_VOLLEY_S = 1.0", 1, true) ~= nil
""",
     """      -- HARNESS 125: AMMO_WINDOW_FACTOR / AMMO_SAME_VOLLEY_S were deleted in round 126
      and raw_find(s, "FOURTH.AMMO_OFF_FACTOR = 1.25", 1, true) ~= nil
"""),
    ("""        local c = (count_log(W3, ": 29 -> 28 of 30 at t=") == 1
          and count_log(W3, "(gap 2.00s, window 2.50s measured)") == 1)
""",
     """        local c = true  -- A1c RETIRED in round 126: the measured-gap window was deleted
"""),
    ("""        local d = (count_log(W3, "FIRING OFF unit 12521 'archers'") == 1
          and count_log(W3, "(no drop for 2.75s > window 2.50s)") == 1)
""",
     """        local d = true  -- A1d RETIRED in round 126: the measured-gap window was deleted
"""),
    ("""        local a = (count_log(W4, ": 19 -> 18 of 20 at t=") == 1
          and count_log(W4, "(gap 0.25s, window 10s default)") == 1)
""",
     """        local a = true  -- A2a RETIRED in round 126: the measured-gap window was deleted
"""),
]

SECTION = r'''
-- ============================================================================
-- HARNESS 125 (round 126): THE FIRING FLAG FROM THE GAME'S RELOAD TABLE.
--   0v: tokens in BOTH files (the generated table and three of its rows, the
--       constants, the in-range read; the round-125 window rule GONE; the probe
--       never casts; the annotated copy log-free).
--   F1 Crossbowmen (reload 13 s), drops 1 s, 1 s, 2 s, 1 s, 1 s apart - the
--      shape that flickered in the field: exactly ONE FIRING ON (reload 13s), ONE
--      CAST POINT exactly 6.50 s after the first shot, ONE FIRING OFF more than
--      16.25 s (1.25 x 13) after the last drop.
--   F2 the in-range moment: target enters the 150 m missile range 2.00 s before
--      the first shot -> IN RANGE logged, FIRING ON says "in range 2.00s before
--      it"; the target leaves -> OUT OF RANGE.
--   F3 a unit missing from the table: "reload not in the table", NO cast point,
--      FIRING OFF on the 10 s default.
--   F4 reload skill: Blessed Legion of Phakth (8 s base, skill 18 -> 6.56 s):
--      the cast point uses 6.56 s.
--   RED (H125_LIVE/H125_ANN on the pre-126 build = round 125): F1 FLICKERS -
--   the old window turns the flag OFF inside the 2 s gap and ON again.
-- ============================================================================
function run_h125()
  local L125 = os.getenv("H125_LIVE") or LIVE
  local A125 = os.getenv("H125_ANN") or ANN
  local RED125 = (os.getenv("H125_LIVE") ~= nil) or (os.getenv("H125_ANN") ~= nil)
  local pre125 = checks
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
  -- the first log line containing tok, or nil
  local function line_of(W, tok)
    for i = 1, #(W.log_lines or {}) do
      local l = W.log_lines[i]
      if raw_find(l, tok, 1, true) ~= nil then return l end
    end
    return nil
  end
  -- an ammo sequence: one value per probe read; drops (of 2) on the listed reads
  local function seq_with(start, drops, n)
    local s, v, set = {}, start, {}
    for _, r in ipairs(drops) do set[r] = true end
    for r = 1, n do
      if set[r] then v = v - 2 end
      s[r] = v
    end
    return s
  end

  print("== HARNESS 125 - section 0v: the reload table, cast point and in-range tokens ==")
  for _, f in ipairs({ { name = "live", path = L125 }, { name = "ann", path = A125 } }) do
    local s = read_file(f.path)
    check("0v " .. f.name .. ": the GENERATED reload table is in, with its three sample rows",
      raw_find(s, "-- BEGIN GENERATED RELOAD TABLE (tools/gen_reload_table.py; do not edit by hand)", 1, true) ~= nil
      and raw_find(s, '\t["wh_main_emp_inf_crossbowmen"] = 13,', 1, true) ~= nil
      and raw_find(s, '\t["wh_main_emp_art_mortar"] = 19,', 1, true) ~= nil
      and raw_find(s, '\t["wh2_dlc09_tmb_inf_skeleton_archers_ror"] = 6.56,', 1, true) ~= nil)
    check("0v " .. f.name .. ": the constants: OFF 1.25 x reload, CAST POINT 0.5 x reload, 10 s default",
      raw_find(s, "FOURTH.AMMO_OFF_FACTOR = 1.25", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_CAST_FRACTION = 0.5", 1, true) ~= nil
      and raw_find(s, "FOURTH.AMMO_WINDOW_DEFAULT_S = 10", 1, true) ~= nil)
    check("0v " .. f.name .. ": the round-125 measured-gap window is GONE",
      cnt(s, "AMMO_SAME_VOLLEY_S") == 0 and cnt(s, "AMMO_WINDOW_FACTOR") == 0 and cnt(s, "st.gap_s") == 0)
    check("0v " .. f.name .. ": the in-range read uses the unit's own live missile_range and unit_distance",
      raw_find(s, "function FOURTH.ammo_in_range(u)", 1, true) ~= nil
      and raw_find(s, "local ok_r, r = pcall(function() return u:missile_range() end)", 1, true) ~= nil
      and raw_find(s, "local ok_d, d = pcall(function() return u:unit_distance(t) end)", 1, true) ~= nil)
    check("0v " .. f.name .. ": the probe never casts (no perform_special_ability between the probe and poll_body)",
      (function()
        local a = raw_find(s, "function FOURTH.ammo_in_range(u)", 1, true)
        local b = a and raw_find(s, "\nlocal function poll_body()", a, true)
        return a ~= nil and b ~= nil and raw_find(string.sub(s, a, b), "perform_special_ability", 1, true) == nil
      end)())
  end
  check("0v ann: the reading copy stays log-free (" .. cnt(read_file(A125), "log(") .. " 'log(')",
    cnt(read_file(A125), "log(") == 0)

  local FILES = { { path = A125, tag = "[annotated] " }, { path = L125, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function run(def, PATH, TAG, polls)
    local W = make_world({ can_perform = true, units = { def },
      cards = { { id = tostring(def.uid), state = "active", vis = true } }, bar = {} })
    local ok = pcall(load_world, W, PATH)
    check(TAG .. def.name .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.conflict = true
    polln(W, polls)
    return W
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- F1: the field shape - drops 1 s, 1 s, 2 s, 1 s, 1 s apart
    local d1 = { name = "wh_main_emp_inf_crossbowmen", uid = 12601, owns = {}, melee = false,
                 ammo_start = 1980, ammo_seq = seq_with(1980, { 3, 7, 11, 19, 23, 27 }, 110) }
    print("== " .. TAG .. "F1. Crossbowmen (reload 13 s): one episode, cast point at +6.50 s, OFF after 16.25 s ==")
    local W = run(d1, f.path, TAG, 101)
    if W ~= nil then
      local ons = count_log(W, "FIRING ON unit 12601")
      if RED125 then
        -- log-based: the annotated (log-free) copy has nothing to count, so it passes as N/A
        local rep = (TAG ~= "[live] ") or ons >= 2
        check(TAG .. "F1-RED: the pre-126 build FLICKERS on the field shape (" .. ons .. " FIRING ON) [live log]", rep)
        done(rep)
      else
        local a = (ons == 1 and count_log(W, "(first shot; never in range before it; reload 13s)") == 1)
        check(TAG .. "F1a: exactly ONE FIRING ON, naming the 13 s reload (" .. ons .. ") [live log]", lg(TAG, a))
        local cl = line_of(W, "CAST POINT unit 12601")
        local ct, ft = nil, nil
        if cl ~= nil then
          ct = tonumber(string.match(cl, "at t=([%d%.]+)s:"))
          ft = tonumber(string.match(cl, "first shot ([%d%.]+)s"))
        end
        local b = (count_log(W, "CAST POINT unit 12601") == 1 and ct ~= nil and ft ~= nil
          and math.abs((ct - ft) - 6.5) < 0.001
          and count_log(W, "+ 0.5 x reload 13s (nothing is cast in this round)") == 1)
        check(TAG .. "F1b: ONE CAST POINT, exactly 6.50 s after the first shot (" .. tostring(ct and ft and (ct - ft)) .. ") [live log]", lg(TAG, b))
        local c = (count_log(W, "FIRING OFF unit 12601") == 1
          and count_log(W, "(no drop for 16.50s > window 16.25s = 1.25 x reload 13s)") == 1)
        check(TAG .. "F1c: ONE FIRING OFF, the first poll past 16.25 s without a drop [live log]", lg(TAG, c))
        local g = (#W.fires == 0)
        check(TAG .. "F1d: nothing is cast (" .. #W.fires .. " fires)", g)
        done(lg(TAG, a) and lg(TAG, b) and lg(TAG, c) and g)
      end
      tally(W)
    end

    if not RED125 then
      -- F2: the in-range moment, 2.00 s before the first shot
      local dist = {}
      for r = 1, 40 do dist[r] = (r < 5 or r >= 20) and 200 or 120 end
      local d2 = { name = "wh_main_emp_inf_handgunners", uid = 12611, owns = {}, melee = false,
                   ammo_start = 1980, ammo_seq = seq_with(1980, { 13 }, 40),
                   ammo_target = { type = "wh_main_vmp_inf_zombie", melee = false },
                   missile_range = 150, dist_seq = dist }
      print("== " .. TAG .. "F2. the target enters missile range 2.00 s before the first shot ==")
      local W2 = run(d2, f.path, TAG, 30)
      if W2 ~= nil then
        local a = (count_log(W2, "IN RANGE unit 12611 'wh_main_emp_inf_handgunners'") == 1
          and count_log(W2, "target at 120.0m <= missile range 150.0m") == 1)
        check(TAG .. "F2a: IN RANGE logged once with the distance and the live range [live log]", lg(TAG, a))
        local b = (count_log(W2, "(first shot; in range 2.00s before it; reload 13s)") == 1)
        check(TAG .. "F2b: FIRING ON reports the 2.00 s warning [live log]", lg(TAG, b))
        local c = (count_log(W2, "OUT OF RANGE unit 12611") == 1
          and count_log(W2, "target at 200.0m > missile range 150.0m") == 1)
        check(TAG .. "F2c: OUT OF RANGE logged when the target leaves [live log]", lg(TAG, c))
        done(lg(TAG, a) and lg(TAG, b) and lg(TAG, c))
        tally(W2)
      end

      -- F3: a unit missing from the table
      local d3 = { name = "archers_not_in_table", uid = 12621, owns = {}, melee = false,
                   ammo_start = 30, ammo_seq = seq_with(30, { 3 }, 60) }
      print("== " .. TAG .. "F3. a unit missing from the reload table: no cast point, 10 s default OFF ==")
      local W3 = run(d3, f.path, TAG, 50)
      if W3 ~= nil then
        local a = (count_log(W3, "(first shot; never in range before it; reload not in the table)") == 1
          and count_log(W3, "CAST POINT unit 12621") == 0)
        check(TAG .. "F3a: no reload, no cast point [live log]", lg(TAG, a))
        local b = (count_log(W3, "FIRING OFF unit 12621") == 1
          and count_log(W3, "(no drop for 10.25s > window 10.00s, no reload in the table: default)") == 1)
        check(TAG .. "F3b: FIRING OFF on the 10 s default [live log]", lg(TAG, b))
        done(lg(TAG, a) and lg(TAG, b))
        tally(W3)
      end

      -- F4: reload skill applied (8 s base, skill 18 -> 6.56 s)
      local d4 = { name = "wh2_dlc09_tmb_inf_skeleton_archers_ror", uid = 12631, owns = {}, melee = false,
                   ammo_start = 900, ammo_seq = seq_with(900, { 3, 7 }, 40) }
      print("== " .. TAG .. "F4. reload skill: 8 s x (1 - 18/100) = 6.56 s -> cast point at +3.50 s (the first poll past 3.28 s) ==")
      local W4 = run(d4, f.path, TAG, 30)
      if W4 ~= nil then
        local cl = line_of(W4, "CAST POINT unit 12631")
        local ct, ft = nil, nil
        if cl ~= nil then
          ct = tonumber(string.match(cl, "at t=([%d%.]+)s:"))
          ft = tonumber(string.match(cl, "first shot ([%d%.]+)s"))
        end
        local a = (cl ~= nil and raw_find(cl, "+ 0.5 x reload 6.56s", 1, true) ~= nil
          and ct ~= nil and ft ~= nil and math.abs((ct - ft) - 3.5) < 0.001)
        check(TAG .. "F4a: the cast point uses the skill-adjusted 6.56 s (" .. tostring(ct and ft and (ct - ft)) .. " s after the first shot) [live log]", lg(TAG, a))
        done(lg(TAG, a))
        tally(W4)
      end
    end
  end

  if RED125 then
    check("RED CONTROL (harness 125): the pre-126 build flickers on the field shape - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 125: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  end
  print("== HARNESS 125 done: " .. (checks - pre125) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
assert src.count(MOCK_ANCHOR) == 1
src = src.replace(MOCK_ANCHOR, MOCK_ADD + MOCK_ANCHOR)
for a, b in RETIRE:
    n = src.count(a)
    assert n == 1, (a[:70], n)
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "-- checks; run_h124 proves the rule that replaced it. The function stays above.\nrun_h124()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h125()\n")
src = BANNER + src
assert "\u2014" not in BANNER + MOCK_ADD + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
