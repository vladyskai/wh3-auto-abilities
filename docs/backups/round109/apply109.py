import io, sys, hashlib

LIVE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN  = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"

def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")

def wr(p, s):
    b = s.encode("utf-8")
    assert b.count(b"\r") == 0, "CRLF leaked into " + p
    with open(p, "wb") as f:
        f.write(b)

def rep_region(s, start, end, old, new, n=1, tag=""):
    i = s.find(start)
    if i < 0:
        raise SystemExit("REGION START not found for " + tag)
    j = s.find(end, i)
    if j < 0:
        raise SystemExit("REGION END not found for " + tag)
    body = s[i:j]
    c = body.count(old)
    if c != n:
        raise SystemExit("REGION ANCHOR %s: found %d, want %d" % (tag, c, n))
    return s[:i] + body.replace(old, new) + s[j:]

def rep(s, old, new, n=1, tag=""):
    c = s.count(old)
    if c != n:
        raise SystemExit("ANCHOR %s: found %d, want %d\n%r" % (tag, c, n, old[:200]))
    return s.replace(old, new)

BIG_HEAD = "-- THE RULE (round 108 amendment"
BIG_END  = "FOURTH.AIR_DROP_BOUND_M = 1\n"

BIG_NEW = """-- THE RULE (round 109 - A HORIZONTAL CENTRE DISTANCE, NOT AN EDGE GAP):
-- fire when an enemy INFANTRY unit is genuinely UNDER the caster - the
-- horizontal CENTRE-TO-CENTRE distance between the two units, read from
-- battle_unit:position() ("the centre position of the main squad of the
-- unit", battle_unit.lua:114), is inside FOURTH.AIR_DROP_CENTER_M = 6 m - and
-- the caster satisfies the usage restrictions its own row declares:
--   * air_only  - the row declares the engine's `grounded` invalid-usage flag
--                 (the Dwarf airframes), or every carrier of the key carries
--                 the `flying` unit attribute (the drop families). The mod
--                 reads battle_unit:is_currently_flying() and holds unless the
--                 answer is exactly true. An unreadable read FAILS CLOSED.
--   * no_melee  - the row declares the engine's `engaged_in_melee` invalid-
--                 usage flag, so a cast while fighting would only be refused.
--                 An unreadable read FAILS CLOSED.
--
-- WHY THE EDGE-TO-EDGE TEST WAS REPLACED (the user's second report: "because
-- the distance is calculated edge to edge, it still drops the rocks too
-- soon"). battle_unit:unit_distance() is "the shortest distance in metres
-- between this unit and a supplied unit, taking into account their bounding
-- box rather than just working out the centre-to-centre distance"
-- (battle_unit.lua:160) - it is the gap between the two BOXES. Two boxes can
-- have their EDGES half a metre apart while their CENTRES are 15 m apart: a
-- wide flying formation and a wide infantry block, side by side, are nearly
-- touching while the flyer is nowhere near over the block. A 1 m EDGE bound
-- therefore still fired when the enemy was not underneath at all - the 6.9 m
-- and 6.0 m in the old log were EDGE gaps, and the rocks left the flyer while
-- it was still short of the target.
--
-- WHY A CONSTANT AND NOT A RADIUS: the battle script API exposes NO per-unit
-- radius, footprint, bounding box or size read. battle_unit.lua's 100 methods
-- carry none (the nearest are ordered_width() - the formation width of the
-- ORDERED position, one axis, no depth - and unit_distance(), the edge gap).
-- script_units:radius() (lib_bsu.lua:2600) is a COLLECTION's spread radius
-- around its mean centre, not a unit's footprint, and no vanilla script calls
-- it. The only "radius" in the game data is battle_entities.radius = 0.6 m,
-- the collision radius of ONE MODEL (a Terradon rider), not of the unit. So
-- 6 m is a DOCUMENTED CONSTANT standing in for the formation footprint: the
-- drop families carry 10 models in a rank_depth-2 formation (a frontage of
-- roughly 15-20 m), and 6 m keeps the enemy under the MIDDLE of that
-- formation rather than touching its edge. It is ONE value to tune: if the
-- drop still releases early, LOWER FOURTH.AIR_DROP_CENTER_M; if it never
-- fires, RAISE it.
--
-- X/Z, NEVER X/Y: battle_vector:get_y() is "the height of the vector position
-- from the water plane" and get_z() is north-south (battle_vector.lua), so the
-- HORIZONTAL distance is X/Z - exactly what battle_vector:distance_xz()
-- computes ("disregarding any height difference"). A 3D distance would read
-- 30-60 m from a unit directly underneath a flying caster, so it is never
-- used.
--
-- THE CAST IS SELF-CENTRED: no target flags at all, so the unit form
-- perform_special_ability(key, OWNER) is the engine's own shape for it. The
-- chosen enemy is never a cast target - it is the justification for pressing
-- the button NOW, and it is re-read immediately before the call.
-- ============================================================================
FOURTH.AIR_DROP_CENTER_M = 6
"""

HELPERS = """-- THE HORIZONTAL CENTRE GAP (round 109). battle_unit:position() is "the
-- centre position of the main squad of the unit" (battle_unit.lua:114) and
-- returns a battle_vector. In a battle_vector get_x() is east-west, get_y() is
-- "the height of the vector position from the water plane" and get_z() is
-- north-south (battle_vector.lua) - so the GROUND PLANE IS X/Z, and
-- battle_vector:distance_xz() is the engine's own "disregarding any height
-- difference" distance. The 3D read is never used: a flying caster 40 m up
-- would read 40 m from a unit directly beneath it. nil when either position
-- cannot be read - the caller then treats the enemy as NOT under the caster
-- (fail-closed).
function FOURTH.ad_centre_gap(unit, enemy)
\tlocal ok_a, a = pcall(function() return unit:position() end)
\tlocal ok_b, b = pcall(function() return enemy:position() end)
\tif not ok_a or not ok_b or a == nil or b == nil then return nil end
\tlocal ok_d, d = pcall(function() return a:distance_xz(b) end)
\tif ok_d and type(d) == "number" then return d end
\tlocal ok_x1, x1 = pcall(function() return a:get_x() end)
\tlocal ok_z1, z1 = pcall(function() return a:get_z() end)
\tlocal ok_x2, x2 = pcall(function() return b:get_x() end)
\tlocal ok_z2, z2 = pcall(function() return b:get_z() end)
\tif ok_x1 and ok_z1 and ok_x2 and ok_z2
\t\tand type(x1) == "number" and type(z1) == "number"
\t\tand type(x2) == "number" and type(z2) == "number" then
\t\tlocal dx, dz = x1 - x2, z1 - z2
\t\treturn math.sqrt(dx * dx + dz * dz)
\tend
\treturn nil
end

-- One position as "x, z" metres for the log - never the height, which is the
-- number that would make a flier look far from a unit it is sitting on.
function FOURTH.ad_where(unit)
\tlocal ok_p, p = pcall(function() return unit:position() end)
\tif not ok_p or p == nil then return "(?)" end
\tlocal ok_x, x = pcall(function() return p:get_x() end)
\tlocal ok_z, z = pcall(function() return p:get_z() end)
\tif not ok_x or not ok_z or type(x) ~= "number" or type(z) ~= "number" then return "(?)" end
\treturn string.format("(%.1f, %.1f)", x, z)
end

"""

LOOP_OLD = """\t\t\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
\t\t\t\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)
\t\t\t\tif ok_alive and type(alive) == "number" and alive > 0
\t\t\t\t\tand gap ~= nil and gap <= bound
\t\t\t\t\tand FOURTH.enemy_is_infantry(enemy) then
\t\t\t\t\tif best == nil or gap < best_gap then
\t\t\t\t\t\tbest, best_gap = enemy, gap
\t\t\t\t\tend
\t\t\t\tend
"""

LOOP_NEW = """\t\t\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
\t\t\t\tif ok_alive and type(alive) == "number" and alive > 0
\t\t\t\t\tand FOURTH.enemy_is_infantry(enemy) then
\t\t\t\t\t-- ROUND 109: the HORIZONTAL CENTRE distance is the test. The
\t\t\t\t\t-- edge-to-edge gap is only a diagnostic, printed with the pick.
\t\t\t\t\tlocal gap = FOURTH.ad_centre_gap(unit, enemy)
\t\t\t\t\tif gap ~= nil then
\t\t\t\t\t\tif near == nil or gap < near_gap then
\t\t\t\t\t\t\tnear, near_gap = enemy, gap
\t\t\t\t\t\tend
\t\t\t\t\t\tif gap <= bound and (best == nil or gap < best_gap) then
\t\t\t\t\t\t\tbest, best_gap = enemy, gap
\t\t\t\t\t\tend
\t\t\t\t\tend
\t\t\t\tend
"""

NIL_OLD = "\tif best == nil then return nil end\n"
NIL_NEW = """\tif best == nil then
\t\t-- WHY IT DID NOT FIRE (round 109): the nearest INFANTRY enemy and the
\t\t-- NUMBER that failed, one line per CHANGE so a waiting flyer is quiet.
\t\tif near ~= nil then
\t\t\tFOURTH.ad_say(unit, marker, "watch: nearest INFANTRY '"
\t\t\t\t.. (FOURTH.type_plain(near) or "enemy") .. "' is centre="
\t\t\t\t.. string.format("%.1f", near_gap) .. "m vs bound=" .. tostring(bound)
\t\t\t\t.. "m -> NOT under the caster")
\t\tend
\t\treturn nil
\tend
"""

RET_OLD = """\treturn "closest INFANTRY enemy under the caster (targeting " .. etype
\t\t.. ", distance=" .. string.format("%.1f", best_gap)
\t\t.. "m, bound=" .. tostring(bound) .. "m)\""""
RET_NEW = """\treturn "closest INFANTRY enemy under the caster (targeting " .. etype
\t\t.. ", centre=" .. string.format("%.1f", best_gap)
\t\t.. "m, bound=" .. tostring(bound) .. "m)\""""

PICKER_HEAD_OLD = """-- THE AIR-DROP PICKER: the CLOSEST ALIVE enemy that IS INFANTRY and whose
-- edge-to-edge gap to the caster is inside the ability's 70% bound.
"""
PICKER_HEAD_NEW = """-- THE AIR-DROP PICKER (round 109): the CLOSEST ALIVE enemy that IS INFANTRY
-- and whose HORIZONTAL CENTRE distance to the caster is inside the ability's
-- own bound - a centre-based overlap test, never the edge-to-edge
-- unit_distance proxy (which fires while the two BOXES are near each other but
-- the CENTRES are far apart).
"""

LIVE_TARGET_OLD = """\t\tlog("  " .. marker .. " target: '" .. etype .. "' is the closest INFANTRY unit under the caster"
\t\t.. " (distance=" .. string.format("%.1f", best_gap) .. "m bound=" .. tostring(bound)
\t\t.. "m air_only=" .. tostring(FOURTH.ad_air_only == true) .. ")")
"""
LIVE_TARGET_NEW = """\tlocal edge = FOURTH.eg_enemy_gap(unit, best)
\tlog("  " .. marker .. " target: '" .. etype .. "' is UNDER the caster"
\t\t.. " (caster=" .. FOURTH.ad_where(unit) .. " enemy=" .. FOURTH.ad_where(best)
\t\t.. " centre=" .. string.format("%.1f", best_gap) .. "m"
\t\t.. " edge=" .. ((edge ~= nil) and string.format("%.1f", edge) or "?") .. "m"
\t\t.. " bound=" .. tostring(bound) .. "m radius=none (constant stands in)"
\t\t.. " air_only=" .. tostring(FOURTH.ad_air_only == true) .. ")")
"""

# ---------------- live ----------------
s = rd(LIVE)
i = s.find(BIG_HEAD); assert i > 0, "live: big head not found"
j = s.find(BIG_END, i); assert j > 0, "live: big end not found"
j += len(BIG_END)
s = s[:i] + BIG_NEW + s[j:]

s = rep(s, "\t-- enemy INFANTRY unit is within FOURTH.AIR_DROP_BOUND_M = **1 m** of the\n"
           "\t-- caster (round 108: the user's own test value, NOT the 70% rule) - the\n"
           "\t-- edge-to-edge overlap proxy - and the caster satisfies the\n",
           "\t-- enemy INFANTRY unit is UNDER the caster - the horizontal CENTRE-TO-\n"
           "\t-- CENTRE distance is inside FOURTH.AIR_DROP_CENTER_M = **6 m**\n"
           "\t-- (round 109: the user's own test value, NOT the 70% rule) - and the\n"
           "\t-- caster satisfies the\n", 1, "live top comment")

s = rep(s, "-- THE AIR-DROP PICKER: the CLOSEST ALIVE enemy that IS INFANTRY and whose\n"
           "-- edge-to-edge gap to the caster is inside the ability's 70% bound.\n",
           PICKER_HEAD_NEW, 1, "live picker head")
s = rep(s, "function FOURTH.ad_pick(unit, routing)\n", HELPERS + "function FOURTH.ad_pick(unit, routing)\n", 1, "live helpers")
s = rep(s, "\tif type(bound) ~= \"number\" then bound = FOURTH.AIR_DROP_BOUND_M end\n",
           "\tif type(bound) ~= \"number\" then bound = FOURTH.AIR_DROP_CENTER_M end\n", 1, "live picker bound")
s = rep(s, "\tlocal best, best_gap = nil, nil\n",
           "\tlocal best, best_gap = nil, nil\n\tlocal near, near_gap = nil, nil\n", 1, "live near locals")
s = rep(s, LOOP_OLD, LOOP_NEW, 1, "live loop")
s = rep(s, NIL_OLD, NIL_NEW, 1, "live nil")
s = rep(s, RET_OLD, RET_NEW, 1, "live return")
s = rep(s, LIVE_TARGET_OLD, LIVE_TARGET_NEW, 1, "live target line")

# pre-cast re-check
s = rep(s, "\t\tif type(ad_bound_now) ~= \"number\" then ad_bound_now = FOURTH.AIR_DROP_BOUND_M end\n",
           "\t\tif type(ad_bound_now) ~= \"number\" then ad_bound_now = FOURTH.AIR_DROP_CENTER_M end\n", 1, "live recheck bound")
s = rep(s, "\t\tlocal gap_now = FOURTH.eg_enemy_gap(unit, enemy)\n\t\tlocal in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)\n",
           "\t\t-- ROUND 109: the same HORIZONTAL CENTRE test as the picker.\n"
           "\t\tlocal gap_now = FOURTH.ad_centre_gap(unit, enemy)\n"
           "\t\tlocal in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)\n", 1, "live recheck gap")
s = rep_region(s, "\tif FOURTH.ad_enemy ~= nil then\n", "\t-- SELF-SUMMON RE-CHECK",
           "\t\t\t\t.. ((gap_now ~= nil) and (\" distance=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" distance=?\")\n",
           "\t\t\t\t.. ((gap_now ~= nil) and (\" centre=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" centre=?\")\n", 1, "live recheck skip text")
s = rep_region(s, "\tif FOURTH.ad_enemy ~= nil then\n", "\t-- SELF-SUMMON RE-CHECK",
           "\t\t\t.. \", distance=\" .. ((gap_now ~= nil) and string.format(\"%.1f\", gap_now) or \"?\")\n",
           "\t\t\t.. \", centre=\" .. ((gap_now ~= nil) and string.format(\"%.1f\", gap_now) or \"?\")\n", 1, "live recheck ok text")
s = rep(s, "\t\tability.range_m = FOURTH.AIR_DROP_BOUND_M\n", "\t\tability.range_m = FOURTH.AIR_DROP_CENTER_M\n", 1, "live load loop")

assert "AIR_DROP_BOUND_M" not in s, "live: stale AIR_DROP_BOUND_M remains"
wr(LIVE, s)
print("live written", len(s))

# ---------------- annotated ----------------
s = rd(ANN)
i = s.find(BIG_HEAD); assert i > 0, "ann: big head not found"
j = s.find(BIG_END, i); assert j > 0, "ann: big end not found"
j += len(BIG_END)
s = s[:i] + BIG_NEW + s[j:]

s = rep(s, "\t-- enemy INFANTRY unit is within FOURTH.AIR_DROP_BOUND_M = **1 m** of the\n"
           "\t-- caster (round 108: the user's own test value, NOT the 70% rule) - the\n"
           "\t-- edge-to-edge overlap proxy - and the caster satisfies the\n",
           "\t-- enemy INFANTRY unit is UNDER the caster - the horizontal CENTRE-TO-\n"
           "\t-- CENTRE distance is inside FOURTH.AIR_DROP_CENTER_M = **6 m**\n"
           "\t-- (round 109: the user's own test value, NOT the 70% rule) - and the\n"
           "\t-- caster satisfies the\n", 1, "ann top comment")

s = rep(s, "-- THE AIR-DROP PICKER: the CLOSEST ALIVE enemy that IS INFANTRY and whose\n"
           "-- edge-to-edge gap to the caster is inside the ability's 70% bound.\n",
           PICKER_HEAD_NEW, 1, "ann picker head")
s = rep(s, "function FOURTH.ad_pick(unit, routing)\n", HELPERS + "function FOURTH.ad_pick(unit, routing)\n", 1, "ann helpers")
s = rep(s, "\tif type(bound) ~= \"number\" then bound = FOURTH.AIR_DROP_BOUND_M end\n",
           "\tif type(bound) ~= \"number\" then bound = FOURTH.AIR_DROP_CENTER_M end\n", 1, "ann picker bound")
s = rep(s, "\tlocal best, best_gap = nil, nil\n",
           "\tlocal best, best_gap = nil, nil\n\tlocal near, near_gap = nil, nil\n", 1, "ann near locals")
s = rep(s, LOOP_OLD, LOOP_NEW, 1, "ann loop")
s = rep(s, NIL_OLD, NIL_NEW, 1, "ann nil")
s = rep(s, RET_OLD, RET_NEW, 1, "ann return")

s = rep(s, "\t\tif type(ad_bound_now) ~= \"number\" then ad_bound_now = FOURTH.AIR_DROP_BOUND_M end\n",
           "\t\tif type(ad_bound_now) ~= \"number\" then ad_bound_now = FOURTH.AIR_DROP_CENTER_M end\n", 1, "ann recheck bound")
s = rep(s, "\t\tlocal gap_now = FOURTH.eg_enemy_gap(unit, enemy)\n\t\tlocal in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)\n",
           "\t\t-- ROUND 109: the same HORIZONTAL CENTRE test as the picker.\n"
           "\t\tlocal gap_now = FOURTH.ad_centre_gap(unit, enemy)\n"
           "\t\tlocal in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)\n", 1, "ann recheck gap")
s = rep(s, "\t\tability.range_m = FOURTH.AIR_DROP_BOUND_M\n", "\t\tability.range_m = FOURTH.AIR_DROP_CENTER_M\n", 1, "ann load loop")

assert "AIR_DROP_BOUND_M" not in s, "ann: stale AIR_DROP_BOUND_M remains"
wr(ANN, s)
print("ann written", len(s))
print("md5 live", hashlib.md5(open(LIVE,'rb').read()).hexdigest())
print("md5 ann ", hashlib.md5(open(ANN,'rb').read()).hexdigest())
