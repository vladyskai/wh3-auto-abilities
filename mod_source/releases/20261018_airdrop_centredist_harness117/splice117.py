#!/usr/bin/env python3
"""Assemble harness117.lua from harness116.lua.

* renames H116_LIVE/H116_ANN -> H117_LIVE/H117_ANN (the red-control env hooks);
* adds the LIGHT hook (H117_LIGHT=1: the air-drop sections only, the user's
  approved tuning-iteration run);
* rewrites the air-drop tooltip sentence in harness 93's TIP map and the three
  prefix pins that quote it;
* rebases the section-0 pins the round-117 change flips (edge -> centre), in
  harness 114, 115 and 116;
* converts the h115 / h116 mock worlds from the edge table to a GROUND POSITION
  (the measurement the rule now makes), and retouches the log text pins that
  quoted the old edge gap;
* splices the round-117 section before the final summary.
"""
import re

ROOT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases"
SRC = ROOT + r"\20261018_airdrop_velocity_harness116\harness116.lua"
SEC = ROOT + r"\20261018_airdrop_centredist_harness117\h117_section.lua"
OUT = ROOT + r"\20261018_airdrop_centredist_harness117\harness117.lua"


def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    assert b.count(b"\r") == 0, "CR found in " + p
    return b.decode("utf-8")


def wr(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))
    with open(p, "rb") as f:
        assert f.read().count(b"\r") == 0, "CR after write in " + p


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "replace %r matched %d (want %d)" % (old[:80], n, count)
    return s.replace(old, new)


s = rd(SRC)

# ---- 1. the red-control env hooks ------------------------------------------
s = s.replace("H116_LIVE", "H117_LIVE").replace("H116_ANN", "H117_ANN")

# ---- 2. the LIGHT hook -----------------------------------------------------
s = must(s, 'print("== harness 102: file mode ==")',
         '''-- ============================================================================
-- ROUND 117 - THE LIGHT RUN. The user approved, for tuning iterations like the
-- air-drop work, running ONLY the affected harness section (the air-drop
-- sections: h109-h117) instead of the whole suite:
--   H117_LIGHT=1  ->  run_h69 .. run_h108 are skipped
-- The sections themselves are untouched by the flag; without it the file is the
-- full suite, exactly as before.
-- ============================================================================
LIGHT = (os.getenv("H117_LIGHT") ~= nil)

print("== harness 102: file mode ==")''')

# ---- 3. the tooltip sentence (harness 93's TIP map + the three prefix pins) -
s = must(s, "models closes to 0.1 m of this unit's edge",
         "models comes within 6 m of this unit's centre")
s = must(s, 'models closes to 0.1 m"', 'models comes within 6 m"', 3)

# ---- 4. harness 114's section-0 pins ---------------------------------------
# 4a. the four constants
s = must(s, '''    check("0 " .. nm .. ": the FOUR new constants are defined EXACTLY ONCE (0.1 m / 10 men / 30 m / 0.2 s)",
      cp(s2, "\\nFOURTH.AIR_DROP_EDGE_M = 0.1\\n") == 1''',
         '''    check("0 " .. nm .. ": the FOUR constants are defined EXACTLY ONCE (6 m CENTRE / 10 men / 30 m / 0.2 s)",
      cp(s2, "\\nFOURTH.AIR_DROP_CENTER_M = 6.0\\n") == 1''')

# 4b. the retired-constant list (the 6 m CENTRE bound is BACK)
s = must(s, '''    check("0 " .. nm .. ": the FOUR DIALS, the 6 m bound, AIR_DROP_INHERIT and the frontage constants are GONE",
      cp(s2, "FOURTH.AIR_DROP_CENTER_M") == 0''',
         '''    check("0 " .. nm .. ": the FOUR DIALS, AIR_DROP_INHERIT and the frontage constants are GONE (the 6 m CENTRE bound is BACK)",
      cp(s2, "FOURTH.AIR_DROP_CENTER_M") >= 8''')

# 4c. the retired helpers (ad_centre_gap came back as the ONE measurement)
s = must(s, '''    check("0 " .. nm .. ": the projection / frontage / segment / centre helpers are GONE (12 definitions)",''',
         '''    check("0 " .. nm .. ": the projection / frontage / segment helpers are GONE (11), the CENTRE helper is BACK",''')
s = must(s, '''      and cp(s2, "function FOURTH.ad_centre_gap(") == 0
      and cp(s2, "function FOURTH.ad_pos(") == 0''',
         '''      and cp(s2, "function FOURTH.ad_centre_gap(") == 1
      and cp(s2, "function FOURTH.ad_pos(") == 0''')

# 4d. and ad_centre_gap IS called now
s = must(s, '''      and cp(s2, "FOURTH.ad_frontage(") == 0 and cp(s2, "FOURTH.ad_centre_gap(") == 0''',
         '''      and cp(s2, "FOURTH.ad_frontage(") == 0 and cp(s2, "FOURTH.ad_centre_gap(") == 4''')

# 4e. the scan measures the centre
s = must(s, '''      and raw_find(near, "FOURTH.eg_enemy_gap(unit, enemy)", 1, true) ~= nil''',
         '''      and raw_find(near, "FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil''')

# 4f. the one comparison
s = must(s, '''    check("0 " .. nm .. ": the DECISION is one comparison (dist >= AIR_DROP_EDGE_M -> NOT YET)",
      pick ~= nil
      and raw_find(pick, "if dist >= FOURTH.AIR_DROP_EDGE_M then", 1, true) ~= nil''',
         '''    check("0 " .. nm .. ": the DECISION is one comparison (dist >= AIR_DROP_CENTER_M -> NOT YET)",
      pick ~= nil
      and raw_find(pick, "if dist >= FOURTH.AIR_DROP_CENTER_M then", 1, true) ~= nil''')

# 4g. the decision line names the CENTRE
s = must(s, '''    check("0 " .. nm .. ": the decision carries the ui id, the type, the entity count and the exact edge",''',
         '''    check("0 " .. nm .. ": the decision carries the ui id, the type, the entity count and the exact CENTRE",''')
s = must(s, """      and raw_find(pick, '" edge="', 1, true) ~= nil""",
         """      and raw_find(pick, '" centre="', 1, true) ~= nil""")

# ---- 5. harness 115's section-0 pins ---------------------------------------
s = must(s, '''    check("0 " .. nm .. ": the four round-114 constants are untouched (0.1 m / 10 men / 30 m / 0.2 s)",
      cp(s2, "\\nFOURTH.AIR_DROP_EDGE_M = 0.1\\n") == 1''',
         '''    check("0 " .. nm .. ": the four round-114 constants are untouched (6 m CENTRE / 10 men / 30 m / 0.2 s)",
      cp(s2, "\\nFOURTH.AIR_DROP_CENTER_M = 6.0\\n") == 1''')
s = must(s, '''      and raw_find(s2, "local gap_ok = (edge_ok or (fallback_now and dwell_ok))", 1, true) ~= nil''',
         '''      and raw_find(s2, "local gap_ok = (centre_ok or (fallback_now and dwell_ok))", 1, true) ~= nil''')

# ---- 6. harness 116's section-0 pin ---------------------------------------
s = must(s, '''      and cp(s2, "\\nFOURTH.AIR_DROP_EDGE_M = 0.1\\n") == 1
      and raw_find(s2, "is_currently_flying()", 1, true) ~= nil''',
         '''      and cp(s2, "\\nFOURTH.AIR_DROP_CENTER_M = 6.0\\n") == 1
      and raw_find(s2, "is_currently_flying()", 1, true) ~= nil''')

# ---- 6b. h114's retired-constant check: its trailing clause still named EDGE
s = must(s,
         '      and cp(s2, "\\nFOURTH.AIR_DROP_EDGE_M = 0.1\\n") == 1)',
         '      and cp(s2, "\\nFOURTH.AIR_DROP_CENTER_M = 6.0\\n") == 1)')

# ---- 6c. h115 G: TWO enemies, so both need a PLACE (the dm table moved them) --
s = must(s, """    local dm = { [euid1] = 0.05, [euid2] = 9.0 }
    local W = make_world({ can_perform = true,
      units = { { name = "sky_junk", uid = uid, owns = { DFA }, melee = false, dist_by_target = dm } },
      enemies = { { name = INF, uid = euid1, men_alive = 20 },
                  { name = INF, uid = euid2, men_alive = 20 } },""",
         """    local dm = { [euid1] = 0.05, [euid2] = 9.0 }
    -- ROUND 117: the two enemies are PLACED (5.9 m = UNDER the 6 m line, 9.0 m =
    -- over it) and the world MOVES them by mutating these tables - the mock
    -- reads def.pos on every call.
    local p1, p2 = { 5.9, 0, 0 }, { 9.0, 0, 0 }
    local W = make_world({ can_perform = true,
      units = { { name = "sky_junk", uid = uid, owns = { DFA }, melee = false, dist_by_target = dm } },
      enemies = { { name = INF, uid = euid1, men_alive = 20, pos = p1, ordered = p1 },
                  { name = INF, uid = euid2, men_alive = 20, pos = p2, ordered = p2 } },""")
s = must(s, """      dm[euid1] = 9.0
      dm[euid2] = 0.05
      polln(W, 1)""",
         """      p1[1], p2[1] = 9.0, 5.9
      polln(W, 1)""")

# ---- 6d. the LIGHT run cannot evaluate the cumulative whole-suite totals -----
s = must(s, """local failures, checks = 0, 0
local function check(label, cond)
  checks = checks + 1""",
         """local failures, checks = 0, 0
LIGHT_SKIPPED = 0
-- the UNWRAPPED finder: check() must never touch the counted string.find
find_plain = string.find
local function check(label, cond)
  -- ROUND 117, LIGHT RUN (H117_LIGHT=1): the cumulative "the WHOLE harness-NN
  -- suite re-ran" sums compare the running total against the FULL suite, which
  -- a light run deliberately does not produce (the earlier sections are
  -- skipped). They are not evaluated and not counted; a full run re-proves
  -- them. Everything else - every world, every pin - still runs and counts.
  if LIGHT == true and (find_plain(label, "the WHOLE harness-", 1, true) ~= nil
      or find_plain(label, "the WHOLE earlier suite", 1, true) ~= nil
      or find_plain(label, "HEADLINE (this round): ability_for is O(1)", 1, true) ~= nil) then
    LIGHT_SKIPPED = LIGHT_SKIPPED + 1
    return
  end
  checks = checks + 1""")

s = must(s, """print("checks: " .. checks .. ", failures: " .. failures)""",
         """if LIGHT then
  print("LIGHT RUN: the cumulative whole-suite totals were not evaluated ("
    .. LIGHT_SKIPPED .. " check(s) skipped) - a FULL run re-proves them.")
end
print("checks: " .. checks .. ", failures: " .. failures)""")

# ---- 7. the mock worlds: the edge table becomes a GROUND POSITION ----------
OLD_MK = '''  local function mk(uid, edef, dm, dseq)
    local def = { name = "sky_junk", uid = uid, owns = { DFA }, melee = false }
    if dm ~= nil then def.dist_by_target = dm end
    if dseq ~= nil then def.dist_seq = dseq end
    local W = make_world({ can_perform = true, units = { def }, enemies = { edef },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = DFA } } })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return true end end
    return W
  end
'''

NEW_MK = '''  local function mk(uid, edef, dm, dseq)
    local def = { name = "sky_junk", uid = uid, owns = { DFA }, melee = false }
    if dm ~= nil then def.dist_by_target = dm end
    if dseq ~= nil then def.dist_seq = dseq end
    local W = make_world({ can_perform = true, units = { def }, enemies = { edef },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = DFA } } })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return true end end
    -- ROUND 117: THE GROUND POSITION IS NOW THE MEASUREMENT. The world's old
    -- edge table (dm[euid] = an edge gap in metres) becomes a PLACE on the
    -- ground, seen from the caster at the origin: under 0.1 m -> a 5.9 m CENTRE
    -- gap (UNDER the 6 m line), anything else -> 6.5 m (over it). dm is read on
    -- EVERY call, so a world that mutates it to model a separation separates
    -- for real. The BEARING from the caster and the HEADING (ordered -
    -- position) are preserved exactly, so every cosine the older worlds
    -- measured is unchanged - only the number the rule compares is new.
    -- THE ENEMY IS NOT IN THE FRIENDLY LIST: it lives in W.enemy_entries, so a
    -- direct lookup is needed to reach the object the mod reads.
    local eo = nil
    for i = 1, #(W.enemy_entries or {}) do
      local eu2 = W.enemy_entries[i].unit
      local ok_e2, id_e2 = pcall(function() return eu2:unique_ui_id() end)
      if ok_e2 and tostring(id_e2) == tostring(edef.uid) then eo = eu2 end
    end
    if eo ~= nil and dm ~= nil then
      local base = edef.pos or { 0, 0, 0 }
      local blen = math.sqrt((base[1] * base[1]) + (base[3] * base[3]))
      local ux, uz = 1, 0
      if blen > 0.001 then ux, uz = base[1] / blen, base[3] / blen end
      local function cv(x, z)
        local v = {}
        function v:get_x() return x end
        function v:get_y() return 0 end
        function v:get_z() return z end
        function v:distance_xz(o)
          local ox, oz = o:get_x(), o:get_z()
          return math.sqrt(((x - ox) * (x - ox)) + ((z - oz) * (z - oz)))
        end
        return v
      end
      local function radius()
        local d = dm[edef.uid]
        if type(d) == "number" and d < 0.1 then return 5.9 end
        return 6.5
      end
      if not edef.position_raises then
        eo.position = function()
          local r = radius()
          return cv(ux * r, uz * r)
        end
      end
      if not edef.ordered_raises then
        eo.ordered_position = function()
          local r = radius()
          local p = edef.ordered or base
          local q = edef.pos or base
          return cv((ux * r) + (p[1] - q[1]), (uz * r) + (p[3] - q[3]))
        end
      end
    end
    return W
  end
'''
s = must(s, OLD_MK, NEW_MK, 2)

# ---- 8. the log text pins that quoted the old edge gap ---------------------
# h115 A2
s = must(s, 'death_from_above dwell started: under at gap 0.05m, waiting 1.00s',
         'death_from_above dwell started: under at gap 5.90m, waiting 1.00s')
# h115 C2 (cancel) and h116 J2 (fallback): both print the separation gap
s = must(s, '"dwell cancelled: separated after 0.25s (gap 0.40m"',
         '"dwell cancelled: separated after 0.25s (gap 6.50m"')
s = must(s, '"short crossing: under for 0.75s (>= 0.30s) -> FIRING on separation (gap 0.40m, the delay measured was 1.00s)"',
         '"short crossing: under for 0.75s (>= 0.30s) -> FIRING on separation (gap 6.50m, the delay measured was 1.00s)"')
# h116 A3 (the closing world's start line)
s = must(s, 'death_from_above dwell started: under at gap 0.05m, waiting 0.00s',
         'death_from_above dwell started: under at gap 5.90m, waiting 0.00s')
# h116 F1: the attacking world, now at a 5.9 m centre
s = must(s, 'ordered=(5.0,0.0) |h|=0.0 proj=+0.00 src=no-heading delay=1.00s',
         'ordered=(5.9,0.0) |h|=0.0 proj=+0.00 src=no-heading delay=1.00s')
# h116 G2: the turn world, now measured from a 5.9 m centre
s = must(s, 'pos=(5.0,0.0) ordered=(5.0,3.0) |h|=3.0',
         'pos=(5.9,0.0) ordered=(5.9,3.0) |h|=3.0')

# h115 F: the drift world, from the edge sequence to a POSITION sequence
s = must(s, """    -- reads 1-4 are the four non-firing polls, read 5 is the firing poll's
    -- picker, read 6 is the re-check - which sees the pair has drifted out.
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, nil,
      { 0.05, 0.05, 0.05, 0.05, 0.05, 0.30 })""",
         """    -- ROUND 117: the re-check re-measures the CENTRE, and every poll makes TWO
    -- position() reads (the picker's centre gap + the hold tick's velocity
    -- read), so the drift is a POSITION SEQUENCE: reads 1-8 are the four
    -- non-firing polls, read 9 the firing poll's picker and read 10 the
    -- re-check - which sees the pair at 6.5 m and skips the cast.
    local seq = {}
    for i = 1, 9 do seq[i] = { 5.9, 0, 0 } end
    seq[10] = { 6.5, 0, 0 }
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20,
      pos = { 5.9, 0, 0 }, ordered = { 5.9, 0, 0 }, pos_seq = seq })""")
s = must(s, '"F1: the dwell completed but the re-check found 0.30 m - no cast ("',
         '"F1: the dwell completed but the re-check found 6.50 m - no cast ("')
s = must(s, '"F2: the skip line prints the FRESH edge [live log]"',
         '"F2: the skip line prints the FRESH centre gap [live log]"')
s = must(s, '"edge=0.30m (need < 0.10m) -> SKIPPED at re-check"',
         '"centre=6.50m (need < 6.00m) -> SKIPPED at re-check"', 2)
s = must(s, 'and cl(W, "edge_ok=false") == 1', 'and cl(W, "centre_ok=false") == 1')

# ---- 9. h116 I2: a raising position() is now a FAIL-CLOSED world -----------
s = must(s, """      check(TAG .. "I2a: pos=UNREADABLE is printed verbatim [live log]",
        lg((TAG ~= "[live] ") or (cl(W2, "pos=UNREADABLE ordered=") == 1)))
      check(TAG .. "I2b: ... |h| cannot be computed, so it says UNREADABLE too [live log]",
        lg((TAG ~= "[live] ") or (cl(W2, "|h|=UNREADABLE proj=+0.00 src=pos-unreadable delay=1.00s") == 1)))""",
         """      check(TAG .. "I2a: a raising position() is FAIL-CLOSED - no candidate, no cast ("
        .. #W2.fires .. ")", #W2.fires == 0)
      check(TAG .. "I2b: ... and the sweep never crashed and never wrote a dwell line [live log]",
        lg((TAG ~= "[live] ") or (cl(W2, "dwell started") == 0)))""")

# ---- 10. h116 K: the drift is a POSITION sequence (the re-check re-measures) --
s = must(s, '''    -- reads 1-4 are the four non-firing polls, read 5 the firing poll's picker,
    -- read 6 the re-check - which sees that the pair has drifted out.
    local W = mk(uid, mover(euid, 5, 0, 90), nil, { 0.05, 0.05, 0.05, 0.05, 0.05, 0.30 })''',
         '''    -- ROUND 117: the re-check re-measures the CENTRE, and every poll makes TWO
    -- position() reads (the picker's centre gap + the hold tick's velocity
    -- read), so the drift is a POSITION SEQUENCE: reads 1-8 are the four
    -- non-firing polls, read 9 the firing poll's picker and read 10 the
    -- re-check - which sees the pair at 6.5 m and skips the cast.
    local edef = mover(euid, 5.9, 0, 90)
    local seq = {}
    for i = 1, 9 do seq[i] = { 5.9, 0, 0 } end
    seq[10] = { 6.5, 0, 0 }
    edef.pos_seq = seq
    local W = mk(uid, edef)''')
s = must(s, '''      check(TAG .. "K1: the delay completed but the re-check found 0.30 m - no cast (" .. #W.fires .. ")",''',
         '''      check(TAG .. "K1: the delay completed but the re-check found 6.50 m - no cast (" .. #W.fires .. ")",''')

# ---- 11. the three suite-boundary pins become LIGHT-aware ------------------
s = must(s, '''  if red114 then
    check("HARNESS 113 suite boundary (harness 114): N/A in the red run - the pre-114 snapshot "
      .. "still carries every harness-112 world", true)
  else''',
         '''  if red114 then
    check("HARNESS 113 suite boundary (harness 114): N/A in the red run - the pre-114 snapshot "
      .. "still carries every harness-112 world", true)
  elseif LIGHT then
    check("HARNESS 112 suite boundary (harness 114): LIGHT RUN - the air-drop sections only ("
      .. pre114 .. " checks so far)", pre114 >= 400)
  else''')
# h115's boundary
def patch_boundary(s, tag):
    old = '''  if red%s then
    check("HARNESS 114 suite boundary (harness 115): N/A in the red run - the pre-115 snapshot "
      .. "still carries every harness-112 world", true)
  else''' % tag
    new = '''  if red%s then
    check("HARNESS 114 suite boundary (harness 115): N/A in the red run - the pre-115 snapshot "
      .. "still carries every harness-112 world", true)
  elseif LIGHT then
    check("HARNESS 114 suite boundary (harness 115): LIGHT RUN - the air-drop sections only ("
      .. pre115 .. " checks so far)", pre115 >= 400)
  else''' % tag
    return must(s, old, new)

s = patch_boundary(s, "115")

old116 = '''  if red116 then
    check("HARNESS 115 suite boundary (harness 116): N/A in the red run - the pre-116 snapshot "
      .. "still carries every harness-115 world", true)
  else'''
new116 = '''  if red116 then
    check("HARNESS 115 suite boundary (harness 116): N/A in the red run - the pre-116 snapshot "
      .. "still carries every harness-115 world", true)
  elseif LIGHT then
    check("HARNESS 115 suite boundary (harness 116): LIGHT RUN - the air-drop sections only ("
      .. pre116 .. " checks so far)", pre116 >= 400)
  else'''
s = must(s, old116, new116)

# ---- 12. splice the round-117 section + the LIGHT-aware runner ------------
section = rd(SEC)
s = must(s, "\nrun_h112()\nrun_h114()\nrun_h115()\nrun_h116()\n",
         "\n" + section + '''
-- THE RUNNER. The air-drop sections always run; the rest of the suite is
-- skipped in a LIGHT run (H117_LIGHT=1).
if LIGHT then
  print("== HARNESS 117 - LIGHT RUN: the AIR-DROP sections only (h109-h117) ==")
end
run_h112()
run_h114()
run_h115()
run_h116()
run_h117()
''')

# ---- 13. guard the pre-air-drop sections ----------------------------------
def guard(m):
    return "if not LIGHT then %s end" % m.group(0)

s, n = re.subn(r"(?m)^run_h(\d+)\(\)$", lambda m: guard(m) if int(m.group(1)) < 109 else m.group(0), s)
print("guarded call lines:", n)

assert "AIR_DROP_EDGE_M" in s  # only the history/pin text may mention it
wr(OUT, s)
print("wrote", OUT, len(s), "bytes")
