"""Round 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY EXCLUSION.

Applies the round-113 edit to BOTH copies:
  * the live source  mod_source/script/battle/mod/zz_test_deadly_onslaught.lua
  * the annotated reading copy  docs/WH3_auto_ability_annotated.lua

Every replacement asserts its exact occurrence count, so a stale snapshot cannot
silently pass. Nothing is loosened: the four dials, AIR_DROP_INHERIT, air_only /
no_melee, the self-centred cast, the fail-closed reads and the pre-cast re-check
are carried over, and the only rule change is the one the user asked for (a
SEGMENT test with a DERIVED half-frontage, plus a ONE-MODEL exclusion).
"""
import io

LIVE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"

# ---------------------------------------------------------------------------
# 1. THE CONSTANTS + THE DERIVATION BLOCK (both files - identical text)
# ---------------------------------------------------------------------------
CONST_OLD = "\nFOURTH.AIR_DROP_INHERIT = false\nFOURTH.ad_note = {}\n"

CONST_NEW = """
FOURTH.AIR_DROP_INHERIT = false
-- ============================================================================
-- ROUND 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY
-- EXCLUSION (the user's sixth air-drop report: a Sky-junk hovering BESIDE a
-- 20-model zombie block never fired while the block walked past - the enemy's
-- CENTRE stayed 10+ m away even though its models swept under the caster; and
-- one fired at a LORD, which must be excluded).
--
-- WHY A POINT COULD NOT DESCRIBE A BLOCK: battle_unit:position() is "the centre
-- position of the main squad of the unit" (battle_unit.lua:118). A 20-model
-- block standing two ranks deep is ten models wide - about 10 m of frontage - so
-- its CENTRE can stay 10 m away while one of its MODELS walks underneath the
-- flyer. The round-110/112 test compared the CASTER'S PROJECTED POINT with the
-- ENEMY'S PROJECTED CENTRE, so that pass was invisible: the centre never came
-- inside 6 m and the rocks were never released.
--
-- THE TEST IS NOW THE ENEMY'S PATH, NOT ITS POINT (the user's ruling, verbatim:
-- "Let's implement the path test with a derived frontage that you suggest."):
--     segment = enemy_current -> enemy_projected   (its own dials, unchanged)
--     perp    = the SHORTEST horizontal distance from that SEGMENT to the
--               CASTER'S projected point (point-to-segment arithmetic on x/z)
--     fire when perp <= AIR_DROP_CENTER_M + ad_frontage(enemy)
-- The caster's two dials, the enemy's two dials, AIR_DROP_INHERIT, air_only /
-- no_melee, the self-centred cast and every fail-closed read are untouched; the
-- pre-cast re-check re-derives the SEGMENT and the DISTANCE at cast time from
-- FRESH reads through the SAME helpers, so it cannot disagree with the picker.
--
-- THE FRONTAGE CREDIT IS DERIVED, NOT GUESSED (FOURTH.ad_frontage):
--   * ordered_width() when it answers a sane positive number - "the width of the
--     position to which the unit has been ordered in metres" (battle_unit.lua)
--     - halved for HALF-width. Source `ordered`. It is the engine's own number
--     for the formation the unit is in, so it wins whenever it is readable.
--   * otherwise the MODEL COUNT and the PER-MODEL COLLISION RADIUS under ONE
--     documented formation assumption: the unit stands TWO RANKS DEEP, so
--         per_rank = ceil(models / 2)
--         frontage = per_rank * 2 * radius      half = per_rank * radius
--     Two ranks is the WIDE end of the game's own infantry formations (the
--     land_units rank_depth column for the 942 infantry rows runs 1..8, median
--     3), and a wider frontage is the SAFE direction for a drop whose whole
--     failure mode is missing a block that sweeps underneath. Source `models`.
--   * the per-model radius is FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6 m. THE BATTLE
--     SCRIPT CANNOT READ IT: battle_unit.lua documents no radius / footprint /
--     bounding box / size read (see the round-109 block above), and battle Lua
--     has NO db access, so land_units.man_entity -> battle_entities.radius
--     cannot be joined at battle time. The constant is the DOCUMENTED value from
--     the extracted tables: over the 942 infantry land_units rows the modal
--     battle_entities.radius is 0.6 m (168 rows), the median 0.7 m, and the
--     Terradon rider 0.6 m. 0.6 ships because it is the modal value and is
--     CONSERVATIVE against the median.
--   * clamped to FOURTH.AIR_DROP_FRONTAGE_MIN_M .. _MAX_M (1 .. 12 m HALF-width).
--     Source `clamped`. The ceiling matters: 12 m half + the 6 m base is an 18 m
--     decision, and a 40-model block in two ranks (20 per rank x 1.2 m = 24 m of
--     frontage) is exactly where it bites. A larger ceiling would let a
--     100-model block trigger a drop 26 m away, which is not "on top of" by any
--     reading of the rule.
--   * a SINGLE-MODEL unit gets NO frontage (0 m, source `single`): a point has no
--     width, and the 6 m base already covers its footprint. This also keeps every
--     single-model world of harnesses 109-112 behaving exactly as it did.
--   * FAIL-CLOSED: unreadable -> 0 m, source `unreadable`; the plain 6 m point
--     distance then decides, exactly as before.
--
-- THE SINGLE-ENTITY EXCLUSION (the user's other report - and THE USER IS RIGHT
-- that one model covers the lord / hero case): a candidate whose
-- battle_unit:initial_number_of_men() - "the number of soldiers the unit started
-- the battle with" (battle_unit.lua:228) - is EXACTLY 1 is skipped, once per
-- episode, as `single entity (1 model)`.
--   * EXACT EQUALITY 1, never "<= 1": a unit with zero models does not exist, so
--     there is no second case to cover (the user's own point).
--   * INITIAL, not current: a 20-model block ground down to one survivor is
--     still a 20-model unit and is NOT a lord (harness world G).
--   * THE COMMANDER KEY SET IS DELIBERATELY NOT USED HERE. The 1,409-key
--     commander set (FOURTH.enemy_is_commander) remains in service for the other
--     evaluators, but it is NOT needed in this one: every INFANTRY-CLASS lord and
--     hero in the game data is a one-model unit (main_units: 0 lord rows and 6
--     hero rows with a land_units class of inf_mel / inf_mis / inf_spr, ALL of
--     them num_men = 1), so the model count already covers that case without a
--     1,409-key membership test on every poll. Multi-model character units DO
--     exist - chariot crews of 2-8 men - but every one of the 146 character rows
--     with num_men >= 2 is land_units class `com`, not infantry, so the infantry
--     filter has already removed them before this guard runs.
--   * an UNREADABLE initial_number_of_men() SKIPS the candidate (fail-closed) and
--     says so: this guard exists to stop a one-model character being targeted,
--     and the engine method is a plain documented read - an unreadable one is a
--     broken engine read, not a target.
FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6
FOURTH.AIR_DROP_RANKS = 2
FOURTH.AIR_DROP_FRONTAGE_MIN_M = 1
FOURTH.AIR_DROP_FRONTAGE_MAX_M = 12
FOURTH.ad_se_logged = {}
FOURTH.ad_note = {}
"""

# ---------------------------------------------------------------------------
# 2. THE HELPERS (both files - identical text, no log calls)
# ---------------------------------------------------------------------------
HELP_ANCHOR = """function FOURTH.ad_sep(x1, z1, x2, z2)
\tif type(x1) ~= "number" or type(z1) ~= "number"
\t\tor type(x2) ~= "number" or type(z2) ~= "number" then return nil end
\tlocal dx, dz = x2 - x1, z2 - z1
\treturn math.sqrt(dx * dx + dz * dz)
end
"""

HELP_NEW = HELP_ANCHOR + """
-- THE HALF-FRONTAGE (round 113): how wide is HALF of this formation, in metres?
-- Returns half_m, source, detail. See the round-113 block above the constants
-- for the derivation, the two-rank assumption and why the per-model radius is a
-- constant (battle Lua cannot join land_units -> battle_entities at battle time).
--   "ordered"    ordered_width() / 2      the engine's own formation width
--   "models"     ceil(men / 2) * radius   two ranks; full frontage = per_rank*2r
--   "clamped"    a value pulled into 1 .. 12 m
--   "single"     men < 2 -> 0 m           a single model is a point
--   "unreadable" -> 0 m                   fail-closed: the 6 m bound alone decides
-- `men_now` is the alive count the CALLER already read for its own alive test, so
-- this helper adds NO engine read on the hot path; nil means "read it here".
-- THE DETAIL STRING IS LOG TEXT, never parsed: it carries the arithmetic so a
-- field log can be audited without re-deriving the number.
function FOURTH.ad_frontage(unit, men_now)
\tif unit == nil then return 0, "unreadable", "no unit handle" end
\tlocal ok_w, w = pcall(function() return unit:ordered_width() end)
\tif ok_w and type(w) == "number" and w == w and w > 0 and w < math.huge then
\t\tlocal half = w * 0.5
\t\tif half >= FOURTH.AIR_DROP_FRONTAGE_MIN_M and half <= FOURTH.AIR_DROP_FRONTAGE_MAX_M then
\t\t\treturn half, "ordered", string.format("ordered_width=%.2fm", w)
\t\tend
\t\tlocal clamped = half
\t\tif clamped < FOURTH.AIR_DROP_FRONTAGE_MIN_M then
\t\t\tclamped = FOURTH.AIR_DROP_FRONTAGE_MIN_M
\t\telseif clamped > FOURTH.AIR_DROP_FRONTAGE_MAX_M then
\t\t\tclamped = FOURTH.AIR_DROP_FRONTAGE_MAX_M
\t\tend
\t\treturn clamped, "clamped", string.format(
\t\t\t"ordered_width=%.2fm -> half %.2fm clamped to %.2fm", w, half, clamped)
\tend
\tlocal men = men_now
\tif type(men) ~= "number" then
\t\tlocal ok_m, m = pcall(function() return unit:number_of_men_alive() end)
\t\tif ok_m and type(m) == "number" then men = m end
\tend
\tif type(men) ~= "number" then
\t\treturn 0, "unreadable",
\t\t\t"ordered_width() and number_of_men_alive() both unreadable -> point"
\tend
\tif men < 2 then
\t\treturn 0, "single", string.format("men=%d -> no frontage, a single model is a point", men)
\tend
\tlocal per_rank = math.ceil(men / FOURTH.AIR_DROP_RANKS)
\tlocal half = per_rank * FOURTH.AIR_DROP_MODEL_RADIUS_M
\tif half < FOURTH.AIR_DROP_FRONTAGE_MIN_M then
\t\treturn FOURTH.AIR_DROP_FRONTAGE_MIN_M, "clamped", string.format(
\t\t\t"men=%d -> %.2fm raised to the %.2fm floor", men, half, FOURTH.AIR_DROP_FRONTAGE_MIN_M)
\tend
\tif half > FOURTH.AIR_DROP_FRONTAGE_MAX_M then
\t\treturn FOURTH.AIR_DROP_FRONTAGE_MAX_M, "clamped", string.format(
\t\t\t"men=%d x %d ranks (%d per rank) x %.2fm = %.2fm capped at the %.2fm ceiling",
\t\t\tmen, FOURTH.AIR_DROP_RANKS, per_rank, FOURTH.AIR_DROP_MODEL_RADIUS_M, half,
\t\t\tFOURTH.AIR_DROP_FRONTAGE_MAX_M)
\tend
\treturn half, "models", string.format("men=%d x %d ranks (%d per rank) x %.2fm radius",
\t\tmen, FOURTH.AIR_DROP_RANKS, per_rank, FOURTH.AIR_DROP_MODEL_RADIUS_M)
end

-- The half-frontage as ONE log fragment: "6.00m (models, men=20 x 2 ranks ...)".
-- Never nil - an unknown half prints 0.00m with its source, so the threshold on
-- the same line always adds up.
function FOURTH.ad_frontage_text(half, src, detail)
\tlocal h = (type(half) == "number") and string.format("%.2f", half) or "0.00"
\treturn h .. "m (" .. tostring(src) .. ", " .. tostring(detail) .. ")"
end

-- THE SHORTEST DISTANCE FROM A POINT TO A SEGMENT, on the ground plane (x/z).
-- Standard point-to-segment arithmetic: project the point onto the segment's
-- direction, CLAMP the parameter to 0..1 - a path that ENDS three metres short of
-- the caster's point is judged on its END point, never on the infinite line -
-- and measure to that clamped foot. Returns distance_m, t (the clamped
-- parameter: 0 = the enemy's current point, 1 = its projected point).
-- A ZERO-LENGTH segment (a parked enemy) degenerates to the plain point distance
-- and t = 0, which is exactly the round-110/112 test.
function FOURTH.ad_seg_dist(px, pz, ax, az, bx, bz)
\tif type(px) ~= "number" or type(pz) ~= "number"
\t\tor type(ax) ~= "number" or type(az) ~= "number"
\t\tor type(bx) ~= "number" or type(bz) ~= "number" then return nil, nil end
\tlocal dx, dz = bx - ax, bz - az
\tlocal len2 = dx * dx + dz * dz
\tif len2 <= 1e-9 then
\t\treturn FOURTH.ad_sep(px, pz, ax, az), 0
\tend
\tlocal t = ((px - ax) * dx + (pz - az) * dz) / len2
\tif t < 0 then
\t\tt = 0
\telseif t > 1 then
\t\tt = 1
\tend
\treturn FOURTH.ad_sep(px, pz, ax + t * dx, az + t * dz), t
end
"""

# ---------------------------------------------------------------------------
# 3. THE SINGLE-ENTITY LOG HELPERS (live only - the annotated copy is log-free)
# ---------------------------------------------------------------------------
SAY_ANCHOR = """function FOURTH.ad_say(unit, marker, note)
\tlocal ok_id, id = pcall(function() return unit:unique_ui_id() end)
\tif not ok_id or id == nil then return end
\tlocal slot = tostring(id)
\tlocal per = FOURTH.ad_note[slot]
\tif per == nil then per = {}; FOURTH.ad_note[slot] = per end
\tif per[marker] == note then return end
\tper[marker] = note
\t\tlog("  " .. FOURTH.ad_tag(unit) .. tostring(marker) .. " " .. note)
end
"""

SAY_NEW = SAY_ANCHOR + """
-- THE SINGLE-ENTITY SKIP, ONCE PER EPISODE (round 113). An "episode" is one
-- continuous run of polls in which the SAME caster skips the SAME one-model
-- enemy: the first skip writes the line, every later poll of that run is silent,
-- and the flag is CLEARED the moment that enemy is judged as a multi-model unit
-- again (or stops being a candidate), so the next pass logs again. Nested by
-- (caster ui id, enemy ui id) - the same allocation-free shape as the arming
-- tables, and no pipe-key is ever built.
function FOURTH.ad_single_say(unit, marker, enemy, men, state)
\tlocal ok_c, cid = pcall(function() return unit:unique_ui_id() end)
\tlocal ok_e, eid = pcall(function() return enemy:unique_ui_id() end)
\tlocal cslot = ok_c and tostring(cid) or "?"
\tlocal eslot = ok_e and tostring(eid) or "?"
\tlocal per = FOURTH.ad_se_logged[cslot]
\tif per == nil then per = {}; FOURTH.ad_se_logged[cslot] = per end
\tif per[eslot] == true then return end
\tper[eslot] = true
\tlocal why, seen
\tif state == "single" then
\t\twhy = "single entity (1 model)"
\t\tseen = "initial_number_of_men() = " .. tostring(men)
\telse
\t\twhy = "single entity check UNREADABLE"
\t\tseen = "initial_number_of_men() answered " .. tostring(men)
\tend
\tlog("  " .. FOURTH.ad_tag(unit) .. tostring(marker) .. " SKIPPED: " .. why
\t\t.. " - '" .. (FOURTH.type_plain(enemy) or "enemy") .. "' has " .. seen
\t\t.. " (a Lord / Hero / character is ONE model: the 1,409-key commander set is"
\t\t.. " deliberately NOT consulted in this evaluator - the model count covers it)"
\t\t.. " - a one-model unit cannot justify a drop"
\t\t.. " [delay=" .. string.format("%.2f", (type(FOURTH.AIR_DROP_DELAY_S) == "number"
\t\t\tand FOURTH.AIR_DROP_DELAY_S or 0)) .. "s bound=" .. tostring(FOURTH.ad_range_m
\t\t\tor FOURTH.AIR_DROP_CENTER_M) .. "m air_only=" .. tostring(FOURTH.ad_air_only == true) .. "]")

end

-- Clear the episode flag for (caster, enemy): called on every poll in which that
-- enemy passes the single-entity guard, so a LATER pass logs a fresh line.
function FOURTH.ad_single_clear(unit, enemy)
\tlocal ok_c, cid = pcall(function() return unit:unique_ui_id() end)
\tlocal ok_e, eid = pcall(function() return enemy:unique_ui_id() end)
\tif not ok_c or not ok_e then return end
\tlocal per = FOURTH.ad_se_logged[tostring(cid)]
\tif per ~= nil then per[tostring(eid)] = nil end
end
"""

# ---------------------------------------------------------------------------
# 4. THE LIVE PICKER
# ---------------------------------------------------------------------------
LIVE_PICK0 = "function FOURTH.ad_pick(unit, routing)"
LIVE_PICK1 = "\nfunction FOURTH.evaluate_air_drop_on_infantry"

LIVE_PICK_NEW = '''function FOURTH.ad_pick(unit, routing)
\tif routing then return nil end
\tlocal marker = FOURTH.ad_marker or "air_drop"
\tlocal bound = FOURTH.ad_range_m
\tif type(bound) ~= "number" then bound = FOURTH.AIR_DROP_CENTER_M end
\tif FOURTH.ad_air_only then
\t\tlocal ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
\t\tif not ok_fly or flying ~= true then
\t\t\tFOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
\t\t\t\t.. (ok_fly and tostring(flying) or "UNREADABLE")
\t\t\t\t.. " -> HOLDING (this ability's row is air-only)")
\t\t\treturn nil
\t\tend
\tend
\tif FOURTH.ad_no_melee then
\t\tlocal ok_m, m = pcall(function() return unit:is_in_melee() end)
\t\tif not ok_m then
\t\t\tFOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
\t\t\treturn nil
\t\tend
\t\tif m == true then
\t\t\tFOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
\t\t\t\t.. " (the row declares engaged_in_melee)")
\t\t\treturn nil
\t\tend
\tend
\tlocal ok_coll, coll = pcall(function()
\t\treturn bm:get_scriptunits_for_main_enemy_army_to_local_player()
\tend)
\tif not ok_coll or coll == nil then return nil end
\tlocal ok_n, n = pcall(function() return coll:count() end)
\tif not ok_n or type(n) ~= "number" then return nil end
\t-- THE CASTER, ONCE (round 110): its current point, its velocity and the
\t-- PROJECTED impact point. An unreadable caster position is fail-closed: with
\t-- nothing to project there is no honest decision, so it holds.
\tlocal ad_t = FOURTH.AIR_DROP_DELAY_S
\tif type(ad_t) ~= "number" or ad_t < 0 then ad_t = 0 end
\t-- NAMING: best_ux/best_uz are the CASTER's own current point and
\t-- best_uvx/best_uspd/best_usrc its velocity and the read it came from;
\t-- best_ipx/best_ipz are the IMPACT point (its projected position, or
\t-- caster + 2*v*d when FOURTH.AIR_DROP_INHERIT is on). They carry the best_
\t-- prefix because they belong to the CHOSEN pair, not to a candidate.
\tlocal best_ux, best_uz, best_uvx, best_uvz, best_uspd, best_usrc, best_ipx, best_ipz
\t\t= FOURTH.ad_lead(unit, ad_t, true)
\tif best_ipx == nil then
\t\tFOURTH.ad_say(unit, marker, "caster position UNREADABLE -> HOLDING"
\t\t\t.. " (fail-closed: the drop point cannot be projected)")
\t\treturn nil
\tend
\t-- ROUND 113: THE DECIDING NUMBER IS best_perp - the shortest distance from the
\t-- ENEMY'S PATH SEGMENT to the caster's projected point - and best_eff is the
\t-- threshold it was compared with (bound + this candidate's half-frontage).
\t-- best_gap keeps the old name and now CARRIES THE PERP (it is what the picker
\t-- ranks and reports); best_pgap is the OLD point-to-point projected centre
\t-- separation, kept only as the printed diagnostic it has become.
\tlocal best, best_gap, best_pgap = nil, nil, nil
\tlocal best_perp, best_half, best_fsrc, best_fdetail, best_eff
\tlocal near, near_gap, near_now, near_perp, near_eff = nil, nil, nil, nil, nil
\tlocal near_half, near_fsrc, near_fdetail, near_pgap
\tlocal near_vx, near_vz, near_spd, near_src
\tlocal near_ex, near_ez, near_epx, near_epz
\tlocal best_ex, best_ez, best_now, best_epx, best_epz
\tlocal best_evx, best_evz, best_espd, best_esrc
\tfor i = 1, n do
\t\tlocal ok_su, su = pcall(function() return coll:item(i) end)
\t\tif ok_su and su ~= nil then
\t\t\tlocal enemy = nil
\t\t\tpcall(function() enemy = su.unit end)
\t\t\tif enemy ~= nil then
\t\t\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
\t\t\t\tif ok_alive and type(alive) == "number" and alive > 0
\t\t\t\t\tand FOURTH.enemy_is_infantry(enemy) then
\t\t\t\t\t-- ROUND 113 - THE SINGLE-ENTITY EXCLUSION. initial_number_of_men()
\t\t\t\t\t-- is the size the unit STARTED the battle with, so a 20-model block
\t\t\t\t\t-- ground down to one survivor is still a 20-model unit and is NOT
\t\t\t\t\t-- skipped (harness world G); a lord / hero IS one model and is.
\t\t\t\t\t-- EXACT EQUALITY: zero models cannot exist. See the round-113 block
\t\t\t\t\t-- above the constants for why the commander key set is NOT read here.
\t\t\t\t\tlocal ok_im, im = pcall(function() return enemy:initial_number_of_men() end)
\t\t\t\t\tlocal se_state = nil
\t\t\t\t\tif not ok_im or type(im) ~= "number" then
\t\t\t\t\t\tse_state = "unreadable"
\t\t\t\t\telseif im == 1 then
\t\t\t\t\t\tse_state = "single"
\t\t\t\t\tend
\t\t\t\t\tif se_state == nil then
\t\t\t\t\t\tFOURTH.ad_single_clear(unit, enemy)
\t\t\t\t\t\tlocal ex, ez, evx, evz, espd, esrc, epx, epz
\t\t\t\t\t\t\t= FOURTH.ad_lead(enemy, ad_t, false)
\t\t\t\t\t\tif epx ~= nil then
\t\t\t\t\t\t\t-- ROUND 113: THE PATH TEST. The segment is the enemy's own
\t\t\t\t\t\t\t-- CURRENT -> PROJECTED line; perp is the shortest distance
\t\t\t\t\t\t\t-- from it to the caster's projected point; the candidate fires
\t\t\t\t\t\t\t-- when that is inside the bound PLUS its own half-frontage.
\t\t\t\t\t\t\tlocal half, fsrc, fdetail = FOURTH.ad_frontage(enemy, alive)
\t\t\t\t\t\t\tlocal eff = bound + half
\t\t\t\t\t\t\tlocal perp = FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)
\t\t\t\t\t\t\tlocal pgap = FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)
\t\t\t\t\t\t\tlocal ngap = FOURTH.ad_sep(best_ux, best_uz, ex, ez)
\t\t\t\t\t\t\tif perp ~= nil and pgap ~= nil and ngap ~= nil then
\t\t\t\t\t\t\t\tif near == nil or perp < near_perp then
\t\t\t\t\t\t\t\t\tnear, near_gap, near_now, near_perp = enemy, pgap, ngap, perp
\t\t\t\t\t\t\t\t\tnear_eff, near_half, near_fsrc, near_fdetail = eff, half, fsrc, fdetail
\t\t\t\t\t\t\t\t\tnear_pgap = pgap
\t\t\t\t\t\t\t\t\tnear_vx, near_vz = evx, evz
\t\t\t\t\t\t\t\t\tnear_spd, near_src = espd, esrc
\t\t\t\t\t\t\t\t\tnear_ex, near_ez, near_epx, near_epz = ex, ez, epx, epz
\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\t\tif perp <= eff and (best == nil or perp < best_perp) then
\t\t\t\t\t\t\t\t\tbest, best_gap, best_perp = enemy, perp, perp
\t\t\t\t\t\t\t\t\tbest_half, best_fsrc, best_fdetail = half, fsrc, fdetail
\t\t\t\t\t\t\t\t\tbest_eff, best_pgap = eff, pgap
\t\t\t\t\t\t\t\t\tbest_ex, best_ez, best_now = ex, ez, ngap
\t\t\t\t\t\t\t\t\tbest_epx, best_epz = epx, epz
\t\t\t\t\t\t\t\t\tbest_evx, best_evz = evx, evz
\t\t\t\t\t\t\t\t\tbest_espd, best_esrc = espd, esrc
\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\tend
\t\t\t\t\t\tend
\t\t\t\t\telse
\t\t\t\t\t\tFOURTH.ad_single_say(unit, marker, enemy, im, se_state)
\t\t\t\t\tend
\t\t\t\tend
\t\t\tend
\t\tend
\tend
\tif best == nil then
\t\t-- WHY IT DID NOT FIRE (round 113): the nearest INFANTRY enemy BY PERP -
\t\t-- the shortest distance from its path segment to the caster's projected
\t\t-- point - that number, the threshold it had to beat, the frontage credit it
\t\t-- was given, the old point-to-point separation and both velocities. The same
\t\t-- two brakes as round 109 keep it out of the log's way: written only when
\t\t-- that enemy's projected POINT separation is inside 30 m, and THE DECIDING
\t\t-- NUMBER IS NEVER BANDED (round 112, diagnosis D1: the 6 m bound sat inside
\t\t-- a 5 m band, so "~5m" covered 5.00-9.99 m and the one number needed to
\t\t-- choose a new bound was destroyed exactly where it mattered). Below 15 m
\t\t-- the numbers print EXACTLY (%.2f); at 15 m and above the 5 m band stays so
\t\t-- the log does not grow per 0.1 m.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\tlocal gap_text, now_text, perp_text
\t\t\tif near_gap < 15 then
\t\t\t\tgap_text = string.format("%.2f", near_gap) .. "m"
\t\t\telse
\t\t\t\tgap_text = "~" .. string.format("%.0f", math.floor(near_gap / 5) * 5) .. "m"
\t\t\tend
\t\t\tif near_now < 15 then
\t\t\t\tnow_text = string.format("%.2f", near_now) .. "m"
\t\t\telse
\t\t\t\tnow_text = "~" .. string.format("%.0f", math.floor(near_now / 5) * 5) .. "m"
\t\t\tend
\t\t\tif type(near_perp) == "number" and near_perp < 15 then
\t\t\t\tperp_text = string.format("%.2f", near_perp) .. "m"
\t\t\telseif type(near_perp) == "number" then
\t\t\t\tperp_text = "~" .. string.format("%.0f", math.floor(near_perp / 5) * 5) .. "m"
\t\t\telse
\t\t\t\tperp_text = "?"
\t\t\tend
\t\t\tFOURTH.ad_say(unit, marker, "watch: nearest INFANTRY '"
\t\t\t\t.. (FOURTH.type_plain(near) or "enemy") .. "' is centre="
\t\t\t\t.. now_text .. " vs bound=" .. tostring(bound)
\t\t\t\t.. "m -> NOT under the caster"
\t\t\t\t.. " [perp=" .. perp_text .. " vs threshold="
\t\t\t\t.. string.format("%.2f", (type(near_eff) == "number") and near_eff or bound) .. "m"
\t\t\t\t.. " (bound=" .. tostring(bound) .. "m + frontage="
\t\t\t\t.. FOURTH.ad_frontage_text(near_half, near_fsrc, near_fdetail) .. ")"
\t\t\t\t.. " segment=" .. FOURTH.ad_pos(near_ex, near_ez) .. "->"
\t\t\t\t.. FOURTH.ad_pos(near_epx, near_epz)
\t\t\t\t.. " projected sep=" .. gap_text
\t\t\t\t.. " after delay=" .. string.format("%.2f", ad_t) .. "s; caster v="
\t\t\t\t.. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)
\t\t\t\t.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="
\t\t\t\t.. FOURTH.ad_vec_text(near_vx, near_vz, near_spd, near_src) .. "]")
\t\tend
\t\treturn nil
\tend
\tlocal etype = FOURTH.type_plain(best) or "enemy"
\t-- the instant centre gap, from the round-109 helper, is a CROSS-CHECK on the
\t-- instant number the motion reads produced (same engine primitive), and the
\t-- edge gap stays a DIAGNOSTIC only - neither is part of the test.
\tlocal enemy = best
\tlocal now_dxz = FOURTH.ad_centre_gap(unit, enemy)
\tlocal edge = FOURTH.eg_enemy_gap(unit, enemy)
\tFOURTH.ad_enemy = best
\tFOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
\tlog("  " .. FOURTH.ad_tag(unit) .. marker .. " target: '" .. etype .. "' is UNDER the caster"
\t\t.. " (PROJECTED " .. string.format("%.2f", ad_t) .. "s AHEAD"
\t\t.. " momentum=" .. ((FOURTH.AIR_DROP_INHERIT == true) and "inherited" or "none")
\t\t.. " caster=" .. FOURTH.ad_pos(best_ux, best_uz)
\t\t.. " v=" .. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)
\t\t.. " proj=" .. FOURTH.ad_pos(best_ipx, best_ipz)
\t\t-- ROUND 111: the two caster dials, then a moving-only fragment - the
\t\t-- projected point above was produced by THIS lead, and a parked caster
\t\t-- gets no fragment because its lead term did nothing.
\t\t.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)
\t\t.. " enemy=" .. FOURTH.ad_pos(best_ex, best_ez)
\t\t.. " v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)
\t\t.. " proj=" .. FOURTH.ad_pos(best_epx, best_epz)
\t\t-- ROUND 113: THE PATH. The segment is the enemy's current -> projected
\t\t-- line, perp is the shortest distance from it to the caster's projected
\t\t-- point (the number that decided), and threshold is what it had to beat -
\t\t-- the 6 m base PLUS this candidate's half-frontage, printed with the
\t\t-- frontage's SOURCE so a wrong-looking credit can be traced to `ordered`,
\t\t-- `models` or `clamped` at once.
\t\t.. " segment=" .. FOURTH.ad_pos(best_ex, best_ez) .. "->" .. FOURTH.ad_pos(best_epx, best_epz)
\t\t.. " perp=" .. string.format("%.2f", best_perp) .. "m"
\t\t.. " frontage=" .. FOURTH.ad_frontage_text(best_half, best_fsrc, best_fdetail)
\t\t.. " threshold=" .. string.format("%.2f", best_eff) .. "m (bound=" .. tostring(bound) .. "m"
\t\t.. " + frontage=" .. string.format("%.2f", best_half) .. "m)"
\t\t.. " centre=" .. string.format("%.1f", best_pgap)
\t\t.. "m (the PROJECTED POINT separation - no longer the test) now="
\t\t.. string.format("%.1f", best_now) .. "m"
\t\t.. " now_dxz=" .. ((now_dxz ~= nil) and string.format("%.1f", now_dxz) or "?") .. "m"
\t\t.. " bound=" .. tostring(bound) .. "m"
\t\t.. " edge=" .. ((edge ~= nil) and string.format("%.1f", edge) or "?") .. "m"
\t\t.. " per_model_radius=" .. string.format("%.2f", FOURTH.AIR_DROP_MODEL_RADIUS_M)
\t\t.. "m (a CONSTANT - no battle_unit read exposes a radius)"
\t\t.. " air_only=" .. tostring(FOURTH.ad_air_only == true) .. ")")
\treturn "closest INFANTRY enemy whose PATH passes the projected caster point (targeting " .. etype
\t\t.. ", perp=" .. string.format("%.2f", best_perp) .. "m vs threshold="
\t\t.. string.format("%.2f", best_eff) .. "m after " .. string.format("%.2f", ad_t) .. "s"
\t\t.. ", bound=" .. tostring(bound) .. "m + frontage=" .. string.format("%.2f", best_half) .. "m)"
end
'''

# ---------------------------------------------------------------------------
# 5. THE ANNOTATED PICKER (same logic, log lines replaced by notes)
# ---------------------------------------------------------------------------
ANN_PICK_NEW = '''function FOURTH.ad_pick(unit, routing)
\tif routing then return nil end
\tlocal marker = FOURTH.ad_marker or "air_drop"
\tlocal bound = FOURTH.ad_range_m
\tif type(bound) ~= "number" then bound = FOURTH.AIR_DROP_CENTER_M end
\tif FOURTH.ad_air_only then
\t\tlocal ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
\t\tif not ok_fly or flying ~= true then
\t\t\tFOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
\t\t\t\t.. (ok_fly and tostring(flying) or "UNREADABLE")
\t\t\t\t.. " -> HOLDING (this ability's row is air-only)")
\t\t\treturn nil
\t\tend
\tend
\tif FOURTH.ad_no_melee then
\t\tlocal ok_m, m = pcall(function() return unit:is_in_melee() end)
\t\tif not ok_m then
\t\t\tFOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
\t\t\treturn nil
\t\tend
\t\tif m == true then
\t\t\tFOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
\t\t\t\t.. " (the row declares engaged_in_melee)")
\t\t\treturn nil
\t\tend
\tend
\tlocal ok_coll, coll = pcall(function()
\t\treturn bm:get_scriptunits_for_main_enemy_army_to_local_player()
\tend)
\tif not ok_coll or coll == nil then return nil end
\tlocal ok_n, n = pcall(function() return coll:count() end)
\tif not ok_n or type(n) ~= "number" then return nil end
\t-- THE CASTER, ONCE (round 110): its current point, its velocity and the
\t-- PROJECTED impact point. An unreadable caster position is fail-closed: with
\t-- nothing to project there is no honest decision, so it holds.
\tlocal ad_t = FOURTH.AIR_DROP_DELAY_S
\tif type(ad_t) ~= "number" or ad_t < 0 then ad_t = 0 end
\t-- NAMING: best_ux/best_uz are the CASTER's own current point and
\t-- best_uvx/best_uspd/best_usrc its velocity and the read it came from;
\t-- best_ipx/best_ipz are the IMPACT point (its projected position, or
\t-- caster + 2*v*d when FOURTH.AIR_DROP_INHERIT is on). They carry the best_
\t-- prefix because they belong to the CHOSEN pair, not to a candidate.
\tlocal best_ux, best_uz, best_uvx, best_uvz, best_uspd, best_usrc, best_ipx, best_ipz
\t\t= FOURTH.ad_lead(unit, ad_t, true)
\tif best_ipx == nil then
\t\tFOURTH.ad_say(unit, marker, "caster position UNREADABLE -> HOLDING"
\t\t\t.. " (fail-closed: the drop point cannot be projected)")
\t\treturn nil
\tend
\t-- ROUND 113: THE DECIDING NUMBER IS best_perp - the shortest distance from the
\t-- ENEMY'S PATH SEGMENT to the caster's projected point - and best_eff is the
\t-- threshold it was compared with (bound + this candidate's half-frontage).
\tlocal best, best_gap, best_pgap = nil, nil, nil
\tlocal best_perp, best_half, best_fsrc, best_fdetail, best_eff
\tlocal near, near_gap, near_now, near_perp, near_eff = nil, nil, nil, nil, nil
\tlocal near_half, near_fsrc, near_fdetail, near_pgap
\tlocal near_vx, near_vz, near_spd, near_src
\tlocal near_ex, near_ez, near_epx, near_epz
\tlocal best_ex, best_ez, best_now, best_epx, best_epz
\tlocal best_evx, best_evz, best_espd, best_esrc
\tfor i = 1, n do
\t\tlocal ok_su, su = pcall(function() return coll:item(i) end)
\t\tif ok_su and su ~= nil then
\t\t\tlocal enemy = nil
\t\t\tpcall(function() enemy = su.unit end)
\t\t\tif enemy ~= nil then
\t\t\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
\t\t\t\tif ok_alive and type(alive) == "number" and alive > 0
\t\t\t\t\tand FOURTH.enemy_is_infantry(enemy) then
\t\t\t\t\t-- ROUND 113 - THE SINGLE-ENTITY EXCLUSION. initial_number_of_men()
\t\t\t\t\t-- is the size the unit STARTED the battle with, so a depleted
\t\t\t\t\t-- 20-model block is NOT a single entity; a lord / hero is. EXACT
\t\t\t\t\t-- EQUALITY 1: zero models cannot exist.
\t\t\t\t\tlocal ok_im, im = pcall(function() return enemy:initial_number_of_men() end)
\t\t\t\t\tlocal se_state = nil
\t\t\t\t\tif not ok_im or type(im) ~= "number" then
\t\t\t\t\t\tse_state = "unreadable"
\t\t\t\t\telseif im == 1 then
\t\t\t\t\t\tse_state = "single"
\t\t\t\t\tend
\t\t\t\t\tif se_state == nil then
\t\t\t\t\t\tFOURTH.ad_single_clear(unit, enemy)
\t\t\t\t\t\tlocal ex, ez, evx, evz, espd, esrc, epx, epz
\t\t\t\t\t\t\t= FOURTH.ad_lead(enemy, ad_t, false)
\t\t\t\t\t\tif epx ~= nil then
\t\t\t\t\t\t\t-- ROUND 113: THE PATH TEST ...
\t\t\t\t\t\t\tlocal half, fsrc, fdetail = FOURTH.ad_frontage(enemy, alive)
\t\t\t\t\t\t\tlocal eff = bound + half
\t\t\t\t\t\t\tlocal perp = FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)
\t\t\t\t\t\t\tlocal pgap = FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)
\t\t\t\t\t\t\tlocal ngap = FOURTH.ad_sep(best_ux, best_uz, ex, ez)
\t\t\t\t\t\t\tif perp ~= nil and pgap ~= nil and ngap ~= nil then
\t\t\t\t\t\t\t\tif near == nil or perp < near_perp then
\t\t\t\t\t\t\t\t\tnear, near_gap, near_now, near_perp = enemy, pgap, ngap, perp
\t\t\t\t\t\t\t\t\tnear_eff, near_half, near_fsrc, near_fdetail = eff, half, fsrc, fdetail
\t\t\t\t\t\t\t\t\tnear_pgap = pgap
\t\t\t\t\t\t\t\t\tnear_vx, near_vz = evx, evz
\t\t\t\t\t\t\t\t\tnear_spd, near_src = espd, esrc
\t\t\t\t\t\t\t\t\tnear_ex, near_ez, near_epx, near_epz = ex, ez, epx, epz
\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\t\tif perp <= eff and (best == nil or perp < best_perp) then
\t\t\t\t\t\t\t\t\tbest, best_gap, best_perp = enemy, perp, perp
\t\t\t\t\t\t\t\t\tbest_half, best_fsrc, best_fdetail = half, fsrc, fdetail
\t\t\t\t\t\t\t\t\tbest_eff, best_pgap = eff, pgap
\t\t\t\t\t\t\t\t\tbest_ex, best_ez, best_now = ex, ez, ngap
\t\t\t\t\t\t\t\t\tbest_epx, best_epz = epx, epz
\t\t\t\t\t\t\t\t\tbest_evx, best_evz = evx, evz
\t\t\t\t\t\t\t\t\tbest_espd, best_esrc = espd, esrc
\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\tend
\t\t\t\t\t\tend
\t\t\t\t\telse
\t\t\t\t\t\t-- (annotated copy: the single-entity skip line is a log-only line -
\t\t\t\t\t\t-- it names the enemy, "single entity (1 model)", the initial size and
\t\t\t\t\t\t-- why the commander key set is not consulted here)
\t\t\t\t\tend
\t\t\t\tend
\t\t\tend
\t\tend
\tend
\tif best == nil then
\t\t-- WHY IT DID NOT FIRE (round 113): the nearest INFANTRY enemy BY PERP, that
\t\t-- number, the threshold it had to beat, the frontage credit it was given,
\t\t-- the old point-to-point separation and both velocities. Written only when
\t\t-- that enemy's projected POINT separation is inside 30 m.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\t-- (annotated copy: the why-not watch line is a log-only line)
\t\t\tlocal gap_text, now_text, perp_text
\t\t\tif near_gap < 15 then
\t\t\t\tgap_text = string.format("%.2f", near_gap) .. "m"
\t\t\telse
\t\t\t\tgap_text = "~" .. string.format("%.0f", math.floor(near_gap / 5) * 5) .. "m"
\t\t\tend
\t\t\tif near_now < 15 then
\t\t\t\tnow_text = string.format("%.2f", near_now) .. "m"
\t\t\telse
\t\t\t\tnow_text = "~" .. string.format("%.0f", math.floor(near_now / 5) * 5) .. "m"
\t\t\tend
\t\t\tif type(near_perp) == "number" and near_perp < 15 then
\t\t\t\tperp_text = string.format("%.2f", near_perp) .. "m"
\t\t\telseif type(near_perp) == "number" then
\t\t\t\tperp_text = "~" .. string.format("%.0f", math.floor(near_perp / 5) * 5) .. "m"
\t\t\telse
\t\t\t\tperp_text = "?"
\t\t\tend
\t\tend
\t\treturn nil
\tend
\tlocal etype = FOURTH.type_plain(best) or "enemy"
\t-- (annotated copy: the target line is a log-only line. It prints the delay, the
\t-- momentum mode, both bodies' current point + velocity + source + projected
\t-- point, the path SEGMENT, the PERPENDICULAR distance that decided, the
\t-- frontage credit with its SOURCE, the threshold, the old point separation, the
\t-- instant separation, the bound, the edge gap and air_only.)
\tlocal enemy = best
\tlocal now_dxz = FOURTH.ad_centre_gap(unit, enemy)
\tFOURTH.ad_enemy = best
\tFOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
\treturn "closest INFANTRY enemy whose PATH passes the projected caster point (targeting " .. etype
\t\t.. ", perp=" .. string.format("%.2f", best_perp) .. "m vs threshold="
\t\t.. string.format("%.2f", best_eff) .. "m after " .. string.format("%.2f", ad_t) .. "s"
\t\t.. ", bound=" .. tostring(bound) .. "m + frontage=" .. string.format("%.2f", best_half) .. "m)"
end
'''

# ---------------------------------------------------------------------------
# 6. THE PRE-CAST RE-CHECK (the same test, on fresh reads)
# ---------------------------------------------------------------------------
RC_LIVE_END = """\t\t\t.. " bound=" .. tostring(ad_bound_now) .. "m) - carrying on")
"""

# The live re-check: the projection + gate + both log lines.
RC_OLD_HEAD = """\t\t-- ROUND 110: the FRESH two-body projection is the test; the instant centre
\t\t-- distance from the round-109 helper is still read as the cross-check the
\t\t-- log prints beside it (one engine primitive, both numbers).
\t\tlocal now_dxz = FOURTH.ad_centre_gap(unit, enemy)
\t\tlocal uc_x2, uc_z2, uc_vx2, uc_vz2, uc_spd2, uc_src2, upx, upz
\t\t\t= FOURTH.ad_lead(unit, ad_t_now, true)
\t\tlocal epx, epz = FOURTH.ad_project(enemy, ad_t_now)
\t\tlocal pgap_now = nil
\t\tif upx ~= nil and epx ~= nil then
\t\t\tpgap_now = FOURTH.ad_sep(upx, upz, epx, epz)
\t\tend
\t\t-- THE PROJECTED separation keeps the round-109 name `gap_now`: the bound
\t\t-- test below is the same line of code it always was, and only the quantity
\t\t-- it measures has changed (the instant distance is now_dxz, the
\t\t-- cross-check).
\t\tlocal gap_now = pgap_now
\t\tlocal in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)
"""

RC_NEW_HEAD = """\t\t-- ROUND 113: THE FRESH SEGMENT TEST. The enemy's CURRENT and PROJECTED
\t\t-- points are re-read here (ONE ad_lead call - the same read the picker
\t\t-- takes, so a drift world still sees the same sequence), the segment is
\t\t-- rebuilt from THEM, and the distance is measured to the CASTER'S FRESH
\t\t-- projected point through the SAME helper the picker used. The half-frontage
\t\t-- is re-derived from the FRESH alive count `ea` (no extra engine read). The
\t\t-- projected POINT separation survives as a printed diagnostic only: it is no
\t\t-- longer the test, so `gap_now` now carries the PERPENDICULAR distance.
\t\tlocal now_dxz = FOURTH.ad_centre_gap(unit, enemy)
\t\tlocal uc_x2, uc_z2, uc_vx2, uc_vz2, uc_spd2, uc_src2, upx, upz
\t\t\t= FOURTH.ad_lead(unit, ad_t_now, true)
\t\tlocal ex2, ez2, evx2, evz2, espd2, esrc2, epx, epz
\t\t\t= FOURTH.ad_lead(enemy, ad_t_now, false)
\t\tlocal pgap_now, perp_now, ptseg_now = nil, nil, nil
\t\tlocal half_now, fsrc_now, fdetail_now = 0, "unreadable", "?"
\t\tlocal eff_now = ad_bound_now
\t\tif upx ~= nil and epx ~= nil then
\t\t\tpgap_now = FOURTH.ad_sep(upx, upz, epx, epz)
\t\t\tperp_now, ptseg_now = FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)
\t\t\thalf_now, fsrc_now, fdetail_now = FOURTH.ad_frontage(enemy, (ok_ea and ea) or nil)
\t\t\teff_now = ad_bound_now + half_now
\t\tend
\t\tlocal gap_now = perp_now
\t\tlocal in_bound_now = (perp_now ~= nil and perp_now <= eff_now)
"""

RC_OLD_SKIP = """\t\t\t\t.. \" delay=\" .. string.format(\"%.2f\", ad_t_now) .. \"s\"
\t\t\t\t.. ((pgap_now ~= nil) and (\" projected centre=\" .. string.format(\"%.1f\", pgap_now) .. \"m\") or \" projected centre=?\")
\t\t\t\t.. ((now_dxz ~= nil) and (\" now=\" .. string.format(\"%.1f\", now_dxz) .. \"m\") or \" now=?\")
"""

RC_NEW_SKIP = """\t\t\t\t.. \" delay=\" .. string.format(\"%.2f\", ad_t_now) .. \"s\"
\t\t\t\t.. ((pgap_now ~= nil) and (\" projected centre=\" .. string.format(\"%.1f\", pgap_now) .. \"m\") or \" projected centre=?\")
\t\t\t\t.. ((now_dxz ~= nil) and (\" now=\" .. string.format(\"%.1f\", now_dxz) .. \"m\") or \" now=?\")
\t\t\t\t.. ((perp_now ~= nil) and (\" perp=\" .. string.format(\"%.2f\", perp_now) .. \"m\") or \" perp=?\")
\t\t\t\t.. \" vs threshold=\" .. string.format(\"%.2f\", eff_now) .. \"m (bound=\"
\t\t\t\t.. tostring(ad_bound_now) .. \"m + frontage=\"
\t\t\t\t.. FOURTH.ad_frontage_text(half_now, fsrc_now, fdetail_now) .. \")\"
\t\t\t\t.. ((ex2 ~= nil and epx ~= nil) and (\" segment=\" .. FOURTH.ad_pos(ex2, ez2) .. \"->\"
\t\t\t\t\t.. FOURTH.ad_pos(epx, epz)) or \"\")
"""

RC_OLD_FIRE = """\t\t\t.. \", projected centre=\" .. ((pgap_now ~= nil) and string.format(\"%.1f\", pgap_now) or \"?\")
\t\t\t.. \"m now=\" .. ((now_dxz ~= nil) and string.format(\"%.1f\", now_dxz) or \"?\")
\t\t\t.. \"m delay=\" .. string.format(\"%.2f\", ad_t_now)
"""

RC_NEW_FIRE = """\t\t\t.. \", projected centre=\" .. ((pgap_now ~= nil) and string.format(\"%.1f\", pgap_now) or \"?\")
\t\t\t.. \"m now=\" .. ((now_dxz ~= nil) and string.format(\"%.1f\", now_dxz) or \"?\")
\t\t\t.. \"m perp=\" .. ((perp_now ~= nil) and string.format(\"%.2f\", perp_now) or \"?\")
\t\t\t.. \"m vs threshold=\" .. string.format(\"%.2f\", eff_now) .. \"m (bound=\"
\t\t\t.. tostring(ad_bound_now) .. \"m + frontage=\"
\t\t\t.. FOURTH.ad_frontage_text(half_now, fsrc_now, fdetail_now) .. \")\"
\t\t\t.. ((ex2 ~= nil and epx ~= nil) and (\" segment=\" .. FOURTH.ad_pos(ex2, ez2) .. \"->\"
\t\t\t\t.. FOURTH.ad_pos(epx, epz)) or \"\")
\t\t\t.. \" delay=\" .. string.format(\"%.2f\", ad_t_now)
"""

# the annotated copy's re-check head is the SAME logic text (its log lines are
# already comments), so the same replacement applies; the live-only log
# fragments are asserted absent below.

# ---------------------------------------------------------------------------
# 7. THE TUNING GUIDE - one more dial, stated in the source
# ---------------------------------------------------------------------------
TUNE_OLD = """--     (AIR_DROP_CENTER_M = 6 m is the BOUND, not a lead; AIR_DROP_INHERIT is the
--      momentum flag, not a lead.)"""
TUNE_NEW = """--     (AIR_DROP_CENTER_M = 6 m is the BOUND, not a lead; AIR_DROP_INHERIT is the
--      momentum flag, not a lead.)
-- ROUND 113 ADDS A SIXTH FIELD DIAL, AND IT IS NOT A LEAD EITHER - it is the
-- FRONTAGE CREDIT, per MODEL, not per test:
--     AIR_DROP_MODEL_RADIUS_M = 0.6 m   the per-model collision radius used when
--                                       ordered_width() cannot be read
--     AIR_DROP_FRONTAGE_MAX_M = 12 m    the CEILING on the half-width credit
-- A block that still walks past WITHOUT a drop -> the credit is under-stated:
-- RAISE AIR_DROP_FRONTAGE_MAX_M (12 -> 15 -> 20). A drop that leaves while the
-- enemy is visibly NOT underneath -> the credit is over-stated: LOWER it
-- (12 -> 8 -> 6) or set it to 0, which restores the pure 6 m point test."""


def apply(path, edits):
    s = io.open(path, encoding="utf-8", newline="").read()
    assert "\r" not in s, path
    for old, new, count in edits:
        got = s.count(old)
        assert got == count, (path, got, count, old[:120])
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("wrote", path, len(s))


def span(s, head, tail):
    i = s.find(head)
    assert i >= 0, head
    j = s.find(tail, i)
    assert j > i, tail
    return s[i:j]


# ------------------------------------------------------------------ live edits
live = io.open(LIVE, encoding="utf-8", newline="").read()
pick_old = span(live, LIVE_PICK0, LIVE_PICK1)
rc_old = span(live, "\tif FOURTH.ad_enemy ~= nil then", "\t-- SELF-SUMMON RE-CHECK")

rc_new = rc_old
for old, new in ((RC_OLD_HEAD, RC_NEW_HEAD), (RC_OLD_SKIP, RC_NEW_SKIP),
                 (RC_OLD_FIRE, RC_NEW_FIRE)):
    assert rc_new.count(old) == 1, old[:100]
    rc_new = rc_new.replace(old, new)

apply(LIVE, [
    (CONST_OLD, CONST_NEW, 1),
    (HELP_ANCHOR, HELP_NEW, 1),
    (SAY_ANCHOR, SAY_NEW, 1),
    (pick_old, LIVE_PICK_NEW, 1),
    (rc_old, rc_new, 1),
    (TUNE_OLD, TUNE_NEW, 1),
])

# ------------------------------------------------------------- annotated edits
ann = io.open(ANN, encoding="utf-8", newline="").read()
apick_old = span(ann, LIVE_PICK0, LIVE_PICK1)
arc_old = span(ann, "\tif FOURTH.ad_enemy ~= nil then", "\t-- SELF-SUMMON RE-CHECK")

arc_new = arc_old
assert arc_new.count(RC_OLD_HEAD) == 1, "the annotated re-check head moved"
arc_new = arc_new.replace(RC_OLD_HEAD, RC_NEW_HEAD)
# the annotated copy's lapse / re-check lines are comments: it must stay log-free
assert "projected centre=" not in arc_new, "the annotated re-check carries log text"
assert "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)" in arc_new, \
    "the annotated re-check does not run the fresh segment test"

# the annotated copy needs the two single-entity helpers too (it is log-free, so
# ad_single_say is a comment-only placeholder there)
ANN_SINGLE = """
-- (annotated copy) THE SINGLE-ENTITY EPISODE FLAG - the two helpers the picker
-- calls. ad_single_say writes the once-per-episode skip line in the LIVE copy
-- ("SKIPPED: single entity (1 model)"); here it is a comment-only placeholder so
-- this reading copy stays log-free. ad_single_clear is the real bookkeeping.
function FOURTH.ad_single_say(unit, marker, enemy, men, state)
\t-- (live copy only: one line per episode, then silence until the enemy is
\t-- judged multi-model again or stops being a candidate)
end

function FOURTH.ad_single_clear(unit, enemy)
\tlocal ok_c, cid = pcall(function() return unit:unique_ui_id() end)
\tlocal ok_e, eid = pcall(function() return enemy:unique_ui_id() end)
\tif not ok_c or not ok_e then return end
\tlocal per = FOURTH.ad_se_logged[tostring(cid)]
\tif per ~= nil then per[tostring(eid)] = nil end
end
"""

ANN_SEG_TAIL = """\treturn FOURTH.ad_sep(px, pz, ax + t * dx, az + t * dz), t
end
"""

apply(ANN, [
    (CONST_OLD, CONST_NEW, 1),
    (HELP_ANCHOR, HELP_NEW, 1),
    (ANN_SEG_TAIL, ANN_SEG_TAIL + ANN_SINGLE, 1),
    (apick_old, ANN_PICK_NEW, 1),
    (arc_old, arc_new, 1),
    (TUNE_OLD, TUNE_NEW, 1),
])
print("round 113 edit applied to both copies")
