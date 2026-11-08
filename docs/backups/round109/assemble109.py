import hashlib, os

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261020_airdrops_wlr_harness108/harness108.lua"
TMP = os.path.expandvars(r"%LOCALAPPDATA%/Temp")
OUT = os.path.join(TMP, "harness109.lua")
SEC = r"C:/Users/vlady/Desktop/WH3_mod/docs/backups/round109/h109_section.lua"

def rd(p):
    with open(p, "rb") as f: return f.read().decode("utf-8")
def wr(p, s):
    b = s.encode("utf-8"); assert b.count(b"\r") == 0
    with open(p, "wb") as f: f.write(b)
def rep(s, old, new, n=1, tag=""):
    c = s.count(old)
    if c != n: raise SystemExit("ANCHOR %s: %d != %d\n%r" % (tag, c, n, old[:200]))
    return s.replace(old, new)

s = rd(SRC)

# ---------------------------------------------------------------- 1. the vec mock
OLD_VEC = "  local function vec(g) local v = {}; function v:distance(o) return g end; return v end\n"
NEW_VEC = """  -- HARNESS 109: a REAL coordinate-carrying vector. battle_vector's ground
  -- plane is x/z (get_y is HEIGHT), so a world must be able to place units and
  -- the mock must answer get_x/get_y/get_z and distance_xz exactly as the
  -- engine does. `g` stays the answer of distance() when the other side is not
  -- a vector, so every older world keeps its old number.
  local function vec(g, x, y, z)
    x, y, z = x or 0, y or 0, z or 0
    local v = {}
    function v:get_x() return x end
    function v:get_y() return y end
    function v:get_z() return z end
    function v:distance(o)
      if o ~= nil and o.get_x ~= nil then
        local ox, oy, oz = o:get_x(), o:get_y(), o:get_z()
        return math.sqrt((x - ox) ^ 2 + (y - oy) ^ 2 + (z - oz) ^ 2)
      end
      return g
    end
    function v:distance_xz(o)
      if o ~= nil and o.get_x ~= nil then
        local ox, oz = o:get_x(), o:get_z()
        return math.sqrt((x - ox) ^ 2 + (z - oz) ^ 2)
      end
      return g
    end
    return v
  end
"""
s = rep(s, OLD_VEC, NEW_VEC, 1, "vec mock")

# ---------------------------------------------------------------- 2. position()
OLD_POS = """    function u:position()
      touch()
      if def.position_raises then
        W.position_raise_attempts = W.position_raise_attempts + 1
        error("mock: position refused", 0)
      end
      -- HARNESS 70: cache the vector per unit and tag it, so a ground cast can
      -- be proved to have received THIS unit's own position.
      if def._posvec == nil then
        def._posvec = vec(0)
        def._posvec.marker = "pos:" .. tostring(def.uid)
      end
      return def._posvec
    end
"""
NEW_POS = """    function u:position()
      touch()
      if def.position_raises then
        W.position_raise_attempts = W.position_raise_attempts + 1
        error("mock: position refused", 0)
      end
      -- HARNESS 109: explicit ground coordinates. def.pos = {x, y, z} where y
      -- is HEIGHT (battle_vector's own convention). def.pos_seq = { {x,y,z},
      -- ... } answers the n-th READ a different place (the last entry repeats),
      -- so a world can move a unit BETWEEN the pick and the pre-cast re-check.
      local p = def.pos
      if def.pos_seq ~= nil then
        def.pos_i = (def.pos_i or 0) + 1
        local q = def.pos_seq[def.pos_i]
        if q == nil then q = def.pos_seq[#def.pos_seq] end
        p = q
      end
      if p ~= nil then
        local pv = vec(0, p[1], p[2], p[3])
        pv.marker = "pos:" .. tostring(def.uid)
        def._posvec = pv
        return pv
      end
      -- HARNESS 70: cache the vector per unit and tag it, so a ground cast can
      -- be proved to have received THIS unit's own position.
      if def._posvec == nil then
        def._posvec = vec(0)
        def._posvec.marker = "pos:" .. tostring(def.uid)
      end
      return def._posvec
    end
"""
s = rep(s, OLD_POS, NEW_POS, 1, "position mock")

# ---------------------------------------------------------------- 3. round-107 0y gate
OLD_0Y = """      check("0y " .. nm .. ": ROUND 108 - the air-drop bound is the 1 m user constant, NOT the 70% map (10 -> 7)",
        raw_find(s2, "FOURTH.ENEMY_CAST_R10  = 7", 1, true) ~= nil
        and raw_find(s2, "[10]  = FOURTH.ENEMY_CAST_R10,", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 1", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) == nil
        and raw_find(s2, "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then", 1, true) ~= nil)
"""
NEW_0Y = """      check("0y " .. nm .. ": ROUND 109 - the air-drop bound is the 6 m HORIZONTAL CENTRE constant, NOT the 70% map (10 -> 7)",
        raw_find(s2, "FOURTH.ENEMY_CAST_R10  = 7", 1, true) ~= nil
        and raw_find(s2, "[10]  = FOURTH.ENEMY_CAST_R10,", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_CENTER_M = 6", 1, true) ~= nil
        and raw_find(s2, "AIR_DROP_BOUND_M", 1, true) == nil
        and raw_find(s2, "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then", 1, true) ~= nil)
"""
s = rep(s, OLD_0Y, NEW_0Y, 1, "0y gate")

# ---------------------------------------------------------------- 4. A5 world
OLD_A5 = """    -- A5: infantry OUTSIDE the 1 m user bound (3 m > 1 m) -> SILENT.
    do
      local uid = 11705
      local W = mk107(uid, { melee = false, dist_by_target = { [11714] = 3.0 } },
        { { name = INF, uid = 11714, melee = true } })
      stub_inf107(W, 11714, true); stub_fly(W, uid, true)
      print("== A5 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A5") then
        polln(W, 3)
        check(TAG .. "A5a: 3 m is outside the 1 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)
        tally(W)
      end
    end
"""
NEW_A5 = """    -- A5: (ROUND 109 ADAPTATION OF THE ROUND-107 WORLD) an infantry unit 8 m
    -- away on the GROUND PLANE is outside the 6 m CENTRE bound -> SILENT. The
    -- old world asserted 3 m was outside a 1 m EDGE bound; that premise is gone
    -- with the edge test, and 3 m is now genuinely UNDER the flyer, so the
    -- world models the new rule's outside instead (same one check, same slot).
    do
      local uid = 11705
      local W = mk107(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11714] = 0.5 } },
        { { name = INF, uid = 11714, melee = true, pos = { 8, 0, 0 } } })
      stub_inf107(W, 11714, true); stub_fly(W, uid, true)
      print("== A5 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A5") then
        polln(W, 3)
        check(TAG .. "A5a: an 8 m centre offset is outside the 6 m centre bound - no fire ("
          .. #W.fires .. ")", #W.fires == 0)
        tally(W)
      end
    end
"""
s = rep(s, OLD_A5, NEW_A5, 1, "A5 world")

# ---------------------------------------------------------------- 5. round-108 0z gates
OLD_0Z = """      check("0z " .. nm .. ": the air-drop bound constant is 1 m",
        raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 1", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) == nil)
      local byp = span108(s2, 'if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then', "\\n\\tend")
      check("0z " .. nm .. ": the family BYPASSES the 70% map and takes the one constant",
        byp ~= nil and raw_find(byp, "ability.range_m = FOURTH.AIR_DROP_BOUND_M", 1, true) ~= nil)
      check("0z " .. nm .. ": the source calls 1 m a USER-CHOSEN TEST value, much tighter than 70%",
        (raw_find(s2, "USER-CHOSEN TEST", 1, true) ~= nil
          or raw_find(s2, "USER'S OWN TEST VALUE", 1, true) ~= nil
          or raw_find(s2, "user's own TEST VALUE", 1, true) ~= nil)
        and raw_find(s2, "MUCH TIGHTER", 1, true) ~= nil)
      check("0z " .. nm .. ": and states that unit_distance is EDGE-TO-EDGE (a unit on top reads 0-5 m)",
        raw_find(s2, "EDGE-TO-EDGE", 1, true) ~= nil
        and raw_find(s2, "0-5 m", 1, true) ~= nil)
      check("0z " .. nm .. ": the source says the 1 m value is one constant to bump",
        raw_find(s2, "ONE constant", 1, true) ~= nil
        and raw_find(s2, "never fires in the field", 1, true) ~= nil)
"""
NEW_0Z = """      check("0z " .. nm .. ": ROUND 109 - the air-drop bound is the 6 m CENTRE constant (the 1 m edge value is gone)",
        raw_find(s2, "FOURTH.AIR_DROP_CENTER_M = 6", 1, true) ~= nil
        and raw_find(s2, "AIR_DROP_BOUND_M", 1, true) == nil)
      local byp = span108(s2, 'if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then', "\\n\\tend")
      check("0z " .. nm .. ": the family BYPASSES the 70% map and takes the one constant",
        byp ~= nil and raw_find(byp, "ability.range_m = FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil)
      check("0z " .. nm .. ": the source calls 6 m the user's own test value, NOT the 70% rule",
        (raw_find(s2, "the user's own test value, NOT the 70% rule", 1, true) ~= nil
          or raw_find(s2, "USER-CHOSEN TEST", 1, true) ~= nil))
      check("0z " .. nm .. ": and explains the EDGE-TO-EDGE failure it replaces (boxes near, centres far)",
        raw_find(s2, "EDGE-TO-EDGE", 1, true) ~= nil
        and raw_find(s2, "bounding", 1, true) ~= nil
        and raw_find(s2, "CENTRES are 15 m apart", 1, true) ~= nil)
      check("0z " .. nm .. ": the source says the 6 m value is ONE value to tune",
        raw_find(s2, "ONE value to tune", 1, true) ~= nil
        and raw_find(s2, "LOWER FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil)
"""
s = rep(s, OLD_0Z, NEW_0Z, 1, "0z gates")

# ---------------------------------------------------------------- 4b. round-108 B worlds
OLD_B1 = """      local W = mk108(uid, { melee = false, dist_by_target = { [11810] = 0.4 } },
        { { name = INF, uid = 11810, melee = true } })
      stub_inf108(W, 11810, true); stub_fly108(W, uid, true)
      print("== B1 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B1") then
        polln(W, 2)
        check(TAG .. "B1a: a unit 0.4 m under the caster fires at the 1 m bound (fires " .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B1b: the cast is on the OWNER",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "B1c: the log line prints the real 0.4 m gap and the 1 m bound [live log]",
          lg108((TAG ~= "[live] ")
            or (count_log(W, "distance=0.4m bound=1m") >= 1
              and count_log(W, "pre-cast re-check: still over an INFANTRY enemy") == 1)))
        tally(W)
      end
"""
NEW_B1 = """      local W = mk108(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11810] = 0.4 } },
        { { name = INF, uid = 11810, melee = true, pos = { 0, 0, 0 } } })
      stub_inf108(W, 11810, true); stub_fly108(W, uid, true)
      print("== B1 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B1") then
        polln(W, 2)
        check(TAG .. "B1a: a unit ON the caster's ground point fires (round 109: the 6 m CENTRE bound) (fires "
          .. #W.fires .. ")", #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B1b: the cast is on the OWNER",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "B1c: the log line prints the CENTRE distance and the 6 m bound [live log]",
          lg108((TAG ~= "[live] ")
            or (count_log(W, "centre=0.0m") >= 1
              and count_log(W, "bound=6m") >= 1
              and count_log(W, "pre-cast re-check: still over an INFANTRY enemy") == 1)))
        tally(W)
      end
"""
s = rep(s, OLD_B1, NEW_B1, 1, "round-108 B1")

OLD_B2 = """      local W = mk108(uid, { melee = false, dist_by_target = { [11811] = 3.0 } },
        { { name = INF, uid = 11811, melee = true } })
      stub_inf108(W, 11811, true); stub_fly108(W, uid, true)
      print("== B2 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B2") then
        polln(W, 3)
        check(TAG .. "B2a: 3 m is OUTSIDE the 1 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)
"""
NEW_B2 = """      local W = mk108(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11811] = 0.5 } },
        { { name = INF, uid = 11811, melee = true, pos = { 10, 0, 0 } } })
      stub_inf108(W, 11811, true); stub_fly108(W, uid, true)
      print("== B2 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B2") then
        polln(W, 3)
        check(TAG .. "B2a: a 10 m CENTRE offset is OUTSIDE the 6 m bound - no fire (" .. #W.fires .. ")",
          #W.fires == 0)
"""
s = rep(s, OLD_B2, NEW_B2, 1, "round-108 B2")

OLD_B3 = """      local W = mk108(uid, { melee = false, dist_by_target = { [11812] = 1.0 } },
        { { name = INF, uid = 11812, melee = true } })
      stub_inf108(W, 11812, true); stub_fly108(W, uid, true)
      print("== B3 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B3") then
        polln(W, 2)
        check(TAG .. "B3a: exactly 1.0 m is INSIDE the bound - it fires (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B3b: the boundary line reads distance=1.0m bound=1m [live log]",
          lg108((TAG ~= "[live] ") or count_log(W, "distance=1.0m bound=1m") >= 1))
"""
NEW_B3 = """      local W = mk108(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11812] = 0.5 } },
        { { name = INF, uid = 11812, melee = true, pos = { 6, 0, 0 } } })
      stub_inf108(W, 11812, true); stub_fly108(W, uid, true)
      print("== B3 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B3") then
        polln(W, 2)
        check(TAG .. "B3a: exactly 6.0 m is INSIDE the centre bound - it fires (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B3b: the boundary line reads centre=6.0m bound=6m [live log]",
          lg108((TAG ~= "[live] ") or (count_log(W, "centre=6.0m") >= 1
            and count_log(W, "bound=6m") >= 1)))
"""
s = rep(s, OLD_B3, NEW_B3, 1, "round-108 B3")

# ---------------------------------------------------------------- 6. splice the new section
tail_anchor = 'check("ZERO search calls by the mod across everything, harness 71 to 100 AND 101-102\'s worlds included (counted " .. find_calls .. ")",\n  find_calls == 0)\n'
s = rep(s, tail_anchor, tail_anchor + "\n" + rd(SEC) + "\n", 1, "section splice")

wr(OUT, s)
print("harness109 written", len(s), hashlib.md5(s.encode()).hexdigest())
