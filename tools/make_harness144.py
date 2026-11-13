#!/usr/bin/env python3
"""Build harness144.lua from harness143.lua for round 145 (the read-only battlefield map probe). Older harnesses are
never edited.

Pin rebases (documented in docs/WH3_round145_map_probe.md):
  I1b and I3b (harness 77 identity worlds): the unit's type() reads grow by exactly ONE per battle - the map probe's
  single type() read of an own unit the identity watch has not read yet (it is then kept in FOURTH.map_type). The
  per-4 s identity cadence those worlds prove is unchanged; only the constant +1 is added.
  The tooltip mirror is unchanged (no new trigger). No count pin moves (no entry added).
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch3_harness143\harness143.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_map_probe_harness144\harness144.lua"

BANNER = """-- ============================================================================
-- HARNESS 144 - ROUND 145: THE BATTLEFIELD MAP PROBE (READ-ONLY).
--   Every 2 s of the conflict phase the live build logs one MAP row per unit of
--   both sides and a MAP_END line. Nothing is cast, no trigger changes.
--   Edited vs harness143: this banner, the I1b / I3b +1 type() read rebase,
--   run_h144 and its call.
--   RED control: H144_LIVE / H144_ANN on docs/backups/round145/pre145_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 144 (round 145): THE BATTLEFIELD MAP PROBE.
--   M1 two of our units and two enemies, 24 polls of battle: MAP snapshots 2 s
--   apart; each snapshot has 2 side=P rows and 2 side=E rows and a MAP_END with
--   own=2 enemy=2; the rows carry the mock's coordinates, width and men; our
--   rows print routing=- (not read), the enemy rows a routing flag; the mock has
--   no strategic_value / alliance -> sv=? vis=?; NOTHING is cast.
--   M2 an enemy whose width and position reads raise -> width=? x=? and the poll
--   reports no error.
--   M3 our units' type() is read at most ONCE per unit over the whole run.
--   The annotated copy (log-free) must load and run the same worlds without a
--   poll error.
--   RED (pre-145 = round 144): M1 logs no MAP row.
-- ============================================================================
function run_h144()
  local L144 = os.getenv("H144_LIVE") or LIVE
  local A144 = os.getenv("H144_ANN") or ANN
  local RED144 = (os.getenv("H144_LIVE") ~= nil) or (os.getenv("H144_ANN") ~= nil)
  local pre144 = checks
  local PRE145 = "C:/Users/vlady/Desktop/WH3_mod/docs/backups/round145/pre145_zz_test_deadly_onslaught.lua"
  local SW ="wh_main_emp_inf_swordsmen"
  local ORC = "wh_main_grn_inf_orc_boyz"
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 144 - section 0zq: the round-145 tokens ==")
  if not RED144 then
    for _, f in ipairs({ { name = "live", path = L144 }, { name = "ann", path = A144 } }) do
      local s = read_file(f.path)
      check("0zq " .. f.name .. ": the map probe is present, read-only and called once per poll through pcall",
        raw_find(s, "FOURTH.MAP_EVERY_S = 2", 1, true) ~= nil
        and raw_find(s, "function FOURTH.map_rows(tick)", 1, true) ~= nil
        and raw_find(s, "function FOURTH.map_own_type(u, id)", 1, true) ~= nil
        and cp(s, "pcall(FOURTH.map_tick, tick_count)") == 1
        and cp(s, "\t{ marker = ") == 722)
    end
    local live = read_file(L144)
    local a = raw_find(live, "function FOURTH.map_num(f, fmt)", 1, true)
    local b = raw_find(live, "FOURTH.evaluators = {", 1, true)
    local span = (a ~= nil and b ~= nil) and live:sub(a, b) or ""
    check("0zq live: the map code casts nothing and writes no trigger state",
      #span > 0 and raw_find(span, "perform_special_ability", 1, true) == nil
      and raw_find(span, "cast_target", 1, true) == nil and raw_find(span, "eg_enemy", 1, true) == nil
      and raw_find(span, "ah_", 1, true) == nil and raw_find(span, "string.find", 1, true) == nil)
    check("0zq ann: the reading copy stays log-free", raw_find(read_file(A144), "log(", 1, true) == nil)
  end

  local FILES = { { path = A144, tag = "[annotated] " }, { path = L144, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, PATH, TAG, polls)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards, bar = {} })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.conflict = true
    polln(W, polls)
    return W
  end
  local function lines_with(W, tok)
    local r = {}
    for _, l in ipairs(W.log_lines or {}) do if raw_find(l, tok, 1, true) ~= nil then r[#r + 1] = l end end
    return r
  end
  local function no_poll_error(W)
    return #lines_with(W, "POLL ERROR") == 0
  end
  local function base_world(b, enemy2)
    local units = {
      { name = SW, uid = b, owns = {}, melee = false, pos = { 10, 0, 20 }, width = 29.4, initial_men = 120 },
      { name = SW, uid = b + 1, owns = {}, melee = true, pos = { 40, 0, 20 }, width = 29.4, initial_men = 120 },
    }
    local enemies = {
      { name = ORC, uid = b + 5, melee = true, pos = { 40, 0, 32 }, width = 30.2, initial_men = 120 },
      enemy2 or { name = ORC, uid = b + 6, melee = false, pos = { 80, 0, 60 }, width = 30.2, initial_men = 120 },
    }
    return units, enemies
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    local live = (TAG == "[live] ")
    -- M1
    local units, enemies = base_world(15800)
    local W = world("M1. two of ours, two enemies, 24 polls of battle", units, enemies, f.path, TAG, 24)
    if W ~= nil then
      local maps = lines_with(W, "MAP t=")
      local ends = lines_with(W, "MAP_END t=")
      local a
      if RED144 then
        a = (#maps == 0 and #ends == 0)
        check(TAG .. "M1-RED: the pre-145 build logs no MAP row (" .. #maps .. ")", a)
      elseif live then
        local p, e = #lines_with(W, " side=P "), #lines_with(W, " side=E ")
        a = (#ends >= 2 and #maps == 4 * #ends and p == 2 * #ends and e == 2 * #ends
          and #lines_with(W, "MAP_END t=") == #lines_with(W, " own=2 enemy=2 "))
        check(TAG .. "M1a: " .. #ends .. " snapshots, each 2 of ours + 2 enemies (" .. #maps .. " rows)", a)
        done(a)
        local t1, t2 = nil, nil
        if #ends >= 2 then
          t1 = tonumber(ends[1]:match("MAP_END t=([%d%.]+)"))
          t2 = tonumber(ends[2]:match("MAP_END t=([%d%.]+)"))
        end
        a = (t1 ~= nil and t2 ~= nil and math.abs((t2 - t1) - 2.0) < 1e-6)
        check(TAG .. "M1b: the snapshots are 2 s apart (" .. tostring(t1) .. " -> " .. tostring(t2) .. ")", a)
        done(a)
        local r = lines_with(W, " id=15805 ")[1] or ""
        a = (raw_find(r, " side=E ", 1, true) ~= nil and raw_find(r, " type=" .. ORC .. " ", 1, true) ~= nil
          and raw_find(r, " x=40.0 z=32.0 ", 1, true) ~= nil and raw_find(r, " width=30.2 ", 1, true) ~= nil
          and raw_find(r, " melee=1 ", 1, true) ~= nil and raw_find(r, " sv=? ", 1, true) ~= nil
          and raw_find(r, " vis=? ", 1, true) ~= nil and raw_find(r, " routing=0", 1, true) ~= nil)
        check(TAG .. "M1c: the enemy row carries its coordinates, width, melee flag, routing read (" .. r .. ")", a)
        done(a)
        local o = lines_with(W, " id=15800 ")[1] or ""
        a = (raw_find(o, " side=P ", 1, true) ~= nil and raw_find(o, " type=" .. SW .. " ", 1, true) ~= nil
          and raw_find(o, " x=10.0 z=20.0 ", 1, true) ~= nil and raw_find(o, " width=29.4 ", 1, true) ~= nil
          and raw_find(o, " routing=-", 1, true) ~= nil)
        check(TAG .. "M1d: our row carries its coordinates and width; routing is not read (" .. o .. ")", a)
        done(a)
        a = (#W.fires == 0 and #(W.ground_fires or {}) == 0 and no_poll_error(W))
        check(TAG .. "M1e: nothing was cast and no poll error (fires " .. #W.fires .. ")", a)
        done(a)
        -- M3: the same world on the pre-145 snapshot is the baseline; the map adds at most ONE type() read
        local tc = (W.type_calls and W.type_calls[15800]) or 0
        local u0, e0 = base_world(15800)
        local W0 = world("M3 baseline: the same world on the pre-145 snapshot", u0, e0, PRE145, TAG, 24)
        local tc0 = (W0 ~= nil and W0.type_calls and W0.type_calls[15800]) or -99
        if W0 ~= nil then tally(W0) end
        a = (tc0 >= 0 and tc - tc0 >= 0 and tc - tc0 <= 1)
        check(TAG .. "M3: the map adds at most ONE type() read of our unit (" .. tc .. " vs " .. tc0
          .. " without the probe)", a)
        done(a)
      else
        a = no_poll_error(W) and #W.fires == 0
        check(TAG .. "M1: the reading copy runs the probe without a poll error and casts nothing", a)
        done(a)
      end
      tally(W)
    end
    -- M2
    if not RED144 then
      local u2, e2 = base_world(15840, { name = ORC, uid = 15846, melee = false, pos = { 80, 0, 60 },
        width_raises = true, position_raises = true, initial_men = 120 })
      local W2 = world("M2. an enemy whose width and position reads raise", u2, e2, f.path, TAG, 16)
      if W2 ~= nil then
        local a
        if live then
          local r = lines_with(W2, " id=15846 ")[1] or ""
          a = (raw_find(r, " width=? ", 1, true) ~= nil and raw_find(r, " x=? z=? ", 1, true) ~= nil
            and no_poll_error(W2))
          check(TAG .. "M2: unreadable reads print ? and the poll goes on (" .. r .. ")", a)
        else
          a = no_poll_error(W2)
          check(TAG .. "M2: the reading copy survives the unreadable reads", a)
        end
        done(a)
        tally(W2)
      end
    end
  end
  if RED144 then
    check("RED CONTROL (harness 144): the pre-145 build has no map probe - 2/2 files checked", true)
  else
    check("HARNESS 144: every map world behaved - " .. n_ok .. "/" .. n_all, n_all == 9 and n_ok == 9)
  end
  print("== HARNESS 144 done: " .. (checks - pre144) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()
R = [
    ("    b = (ident == math.floor(T / 16))\n",
     "    b = (ident == math.floor(T / 16) + 1)   -- ROUND 145: + the map probe's ONE type() read per unit per battle\n"),
    ('      .. " attempts over 240 polls (want " .. math.floor(240 / 16) .. ")", ident == math.floor(240 / 16))',
     '      .. " attempts over 240 polls (want " .. math.floor(240 / 16) .. " + 1 map read)", ident == math.floor(240 / 16) + 1)'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:60], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h142()\nrun_h143()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h144()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
