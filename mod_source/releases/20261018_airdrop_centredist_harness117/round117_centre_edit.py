#!/usr/bin/env python3
"""Round 117 edit: the air-drop detection moves from the EDGE gap to the CENTRE gap.

ONE change, nothing else: the pair test that decided UNDER used
`unit:unit_distance(enemy)` (bounding-box EDGE to EDGE, battle_unit.lua:160)
against AIR_DROP_EDGE_M = 0.1. It now uses the GROUND-PLANE CENTRE-to-CENTRE
distance between the caster's position() and the enemy's position() (x/z only,
never y) against FOURTH.AIR_DROP_CENTER_M = 6.0.

The candidate filter, the velocity-aware dynamic delay (measured once per
contact), the short-crossing fallback, the 0.2 s fast pass, the 250 ms poll and
every gate are untouched.

Applied to BOTH copies (live + annotated) with exact occurrence assertions.
Binary read/write so the shipped file stays LF.
"""

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = ROOT + r"\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = ROOT + r"\docs\WH3_auto_ability_annotated.lua"


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


def tabs(x):
    """Leading whitespace only: two spaces of indent -> one tab (string literals
    like log("  " ..) must NOT be touched)."""
    out = []
    for line in x.split("\n"):
        i = 0
        while line[i:i + 2] == "  ":
            i += 2
        out.append(("\t" * (i // 2)) + line[i:])
    return "\n".join(out)


def both(s, old, new, count=1):
    """Replace, accepting the live copy's SPACES or the annotated copy's TABS."""
    n = s.count(old)
    if n == count:
        return s.replace(old, new)
    alt_o, alt_n = tabs(old), tabs(new)
    n2 = s.count(alt_o)
    assert n2 == count, "anchor %r matched %d (spaces) / %d (tabs), want %d" % (
        old[:90], n, n2, count)
    return s.replace(alt_o, alt_n)


# ============================================================================
# 1. THE HEADER: the round-117 ruling and the new rule, in full
# ============================================================================
OLD_RULE = """-- THE RULE, IN FULL - nothing else decides:
--   candidate = ALIVE (number_of_men_alive() > 0) and
--               number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's edge-to-edge unit_distance() is READABLE
--   chosen    = the NEAREST valid candidate by that distance
--   UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
--   FIRE      = UNDER, and the delay measured for that pair at the first
--               contact of the episode has elapsed (round 116 - see below)
"""

NEW_RULE = """-- ROUND 117 - THE MEASUREMENT MOVES, THE RULE DOES NOT
-- THE USER'S RULING, verbatim: "Let's keep our current calculation but just
-- replace the detection on edge with detection on the distance to center.
-- Let's say 6 meters for now. I'll test."
-- The candidate filter, the velocity-aware delay MEASURED ONCE PER CONTACT,
-- the short-crossing fallback, the 250 ms poll and the 0.2 s fast pass, the
-- gates and the read-verification lines are UNCHANGED. ONE number moved: the
-- gap that decides UNDER. It used to be the engine's bounding-box EDGE gap
-- (`unit:unit_distance(enemy)`, battle_unit.lua:160); it is now the
-- GROUND-PLANE CENTRE-to-CENTRE distance between the two units' own
-- position() reads - x/z only, the height is never read - computed by
-- FOURTH.ad_centre_gap(). The old 0.10 m edge constant is RETIRED (nothing
-- else in the file used it) and FOURTH.AIR_DROP_CENTER_M = 6.0 replaces it.
--
-- THE RULE, IN FULL - nothing else decides:
--   candidate = ALIVE (number_of_men_alive() > 0) and
--               number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's CENTRE gap (ad_centre_gap) is READABLE
--   chosen    = the NEAREST valid candidate by that CENTRE gap
--   UNDER     = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m)
--   FIRE      = UNDER, and the delay measured for that pair at the first
--               contact of the episode has elapsed (round 116 - see below)
"""

OLD_WHY = """-- battle_unit:unit_distance() is "the shortest distance in metres between this
-- unit and a supplied unit, taking into account their bounding box rather than
-- just working out the centre-to-centre distance" (battle_unit.lua:160). It is
-- the number the user asked for, so it is the number that decides - not a
-- centre distance, not a projected point, not a frontage credit.
"""

NEW_WHY = """-- WHY THE CENTRE, AND WHY x/z ONLY. battle_unit:unit_distance() is "the
-- shortest distance in metres between this unit and a supplied unit, taking
-- into account their bounding box rather than just working out the
-- centre-to-centre distance" (battle_unit.lua:160) - two wide formations can
-- have boxes 0.1 m apart while their CENTRES are 15 m apart, which reads as
-- "on top of each other" and drops too early. The user's ruling is to detect
-- on the distance to the CENTRE instead. battle_unit:position() is "the centre
-- position of the main squad of the unit"; battle_vector's ground plane is x/z
-- (get_y is HEIGHT), so the gap is read with position():distance_xz() and
-- never with the 3D distance - a flyer 60 m up over an enemy is 0 m away here,
-- which is exactly what an air drop on that enemy means.
"""

# ============================================================================
# 2. THE CONSTANTS
# ============================================================================
OLD_CONSTS = """-- THE FOUR CONSTANTS - one test value each, no per-entry edit needed:
--   AIR_DROP_EDGE_M  = 0.10 m  FIRE below this edge-to-edge gap
--   AIR_DROP_MIN_MEN = 10      a candidate needs MORE alive models than this
--   AIR_DROP_NEAR_M  = 30 m    the fast pass runs while a valid enemy is closer
--   AIR_DROP_FAST_S  = 0.2 s   the fast pass interval
FOURTH.AIR_DROP_EDGE_M = 0.1
"""

NEW_CONSTS = """-- THE FOUR CONSTANTS - one test value each, no per-entry edit needed:
--   AIR_DROP_CENTER_M = 6.0 m  FIRE below this CENTRE-to-CENTRE ground gap
--   AIR_DROP_MIN_MEN  = 10     a candidate needs MORE alive models than this
--   AIR_DROP_NEAR_M   = 30 m   the fast pass runs while a valid enemy is closer
--   AIR_DROP_FAST_S   = 0.2 s  the fast pass interval
FOURTH.AIR_DROP_CENTER_M = 6.0
"""

# ============================================================================
# 3. THE HELPER - inserted immediately above the candidate scan
# ============================================================================
HELPER = """-- THE CENTRE GAP (round 117) - the ONE measurement this evaluator makes:
-- the GROUND-PLANE distance between the caster's own centre and the enemy's
-- own centre, in metres, from the two documented position() reads.
--   * x/z ONLY. get_y is HEIGHT on battle_vector's ground plane; a caster 60 m
--     above the enemy is 0 m away, never 60 m.
--   * battle_vector:distance_xz(vector) is the engine's own "distance ...
--     disregarding any height difference" read; it is TRIED FIRST and the
--     plain sqrt(dx^2 + dz^2) is the fallback, so a state where the method is
--     unavailable still measures the same number.
--   * FAIL CLOSED: any read that raises, or that does not answer a NUMBER,
--     answers nil - the candidate is then not valid and nothing is cast.
-- Returns d, x1, z1, x2, z2 (the positions are returned so a caller may log
-- them; only d decides anything).
function FOURTH.ad_centre_gap(caster, enemy)
  local ok_a, a = pcall(function() return caster:position() end)
  local ok_b, b = pcall(function() return enemy:position() end)
  if not ok_a or not ok_b or a == nil or b == nil then return nil end
  local ok_x1, x1 = pcall(function() return a:get_x() end)
  local ok_z1, z1 = pcall(function() return a:get_z() end)
  local ok_x2, x2 = pcall(function() return b:get_x() end)
  local ok_z2, z2 = pcall(function() return b:get_z() end)
  if not (ok_x1 and ok_z1 and ok_x2 and ok_z2) then return nil end
  if type(x1) ~= "number" or type(z1) ~= "number"
    or type(x2) ~= "number" or type(z2) ~= "number" then return nil end
  local ok_d, d = pcall(function() return a:distance_xz(b) end)
  if not ok_d or type(d) ~= "number" then
    local dx, dz = x1 - x2, z1 - z2
    d = math.sqrt((dx * dx) + (dz * dz))
  end
  return d, x1, z1, x2, z2
end

"""

OLD_NEAR_DOC = """-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass can never disagree about who is valid.
-- Returns: nearest valid enemy, its edge-to-edge gap in metres, its CURRENT
-- model count, its type key. nil when no valid candidate exists, or when the
-- enemy army cannot be read at all (fail-closed: no candidate, no cast).
-- A candidate is valid when number_of_men_alive() answers a NUMBER greater
-- than AIR_DROP_MIN_MEN AND unit_distance() answers a number. Nothing else.
"""

NEW_NEAR_DOC = """-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass can never disagree about who is valid.
-- Returns: nearest valid enemy, its CENTRE-to-CENTRE ground gap in metres, its
-- CURRENT model count, its type key. nil when no valid candidate exists, or
-- when the enemy army cannot be read at all (fail-closed: no candidate, no
-- cast).
-- A candidate is valid when number_of_men_alive() answers a NUMBER greater
-- than AIR_DROP_MIN_MEN AND ad_centre_gap() answers a number. Nothing else.
"""

# ============================================================================
# 4. THE EVALUATOR HEADER + ITS ONE COMPARISON
# ============================================================================
OLD_PICK_DOC = """-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- edge gap against AIR_DROP_EDGE_M - after the caster-side usage checks the
-- ability's own row declares. The exact distance, the entity count, the enemy
-- type and this caster's ui id are written on EVERY decision:
--     [1003] sky_junk_bomb nearest valid:'wh_main_inf_zombie_0' entities=20
--            edge=0.04m (need < 0.10m) -> NOT YET
"""

NEW_PICK_DOC = """-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- CENTRE gap against AIR_DROP_CENTER_M - after the caster-side usage checks
-- the ability's own row declares. The exact distance, the entity count, the
-- enemy type and this caster's ui id are written on EVERY decision:
--     [1003] sky_junk_bomb nearest valid:'wh_main_inf_zombie_0' entities=20
--            centre=5.90m (need < 6.00m) -> NOT YET
"""

OLD_UNDER_DOC = """-- SECONDS the pair has been CONTINUOUSLY under the edge line, on THE POLL'S OWN
-- CLOCK: tick_count advances once per poll (POLL_MS = 250 ms) and always runs,
"""

NEW_UNDER_DOC = """-- SECONDS the pair has been CONTINUOUSLY under the centre line, on THE POLL'S
-- OWN CLOCK: tick_count advances once per poll (POLL_MS = 250 ms) and always runs,
"""

# ---- the picker body pieces (identical in both copies, indentation differs) --
OLD_PICK_LOCAL = """  local edge_text = string.format("%.2f", dist)
  local need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
"""
NEW_PICK_LOCAL = """  local centre_text = string.format("%.2f", dist)
  local need = string.format("%.2f", FOURTH.AIR_DROP_CENTER_M)
"""

OLD_PICK_HOLD_LOG = """    FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
      .. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m)"
      .. " -> HOLDING (the pair's ui ids are unreadable, so no dwell can be timed)")
"""
NEW_PICK_HOLD_LOG = """    FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
      .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m)"
      .. " -> HOLDING (the pair's ui ids are unreadable, so no dwell can be timed)")
"""

OLD_PICK_SEP = """  if dist >= FOURTH.AIR_DROP_EDGE_M then
"""
NEW_PICK_SEP = """  if dist >= FOURTH.AIR_DROP_CENTER_M then
"""

# the two NOT YET lines are identical - replace both
OLD_NOT_YET = """      FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
        .. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
"""
NEW_NOT_YET = """      FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
        .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> NOT YET")
"""

OLD_REASON_SHORT = """    return "nearest valid '" .. etype .. "' has " .. tostring(men)
      .. " models; SHORT CROSSING - it held " .. string.format("%.2f", under)
      .. "s under the " .. need .. "m edge line and has separated to " .. edge_text
"""
NEW_REASON_SHORT = """    return "nearest valid '" .. etype .. "' has " .. tostring(men)
      .. " models; SHORT CROSSING - it held " .. string.format("%.2f", under)
      .. "s under the " .. need .. "m centre line and has separated to " .. centre_text
"""

OLD_REASON_DWELL = """  return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models, its EDGE gap is "
    .. edge_text .. "m - under the " .. need .. "m line for " .. string.format("%.2f", under)
"""
NEW_REASON_DWELL = """  return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models, its CENTRE gap is "
    .. centre_text .. "m - under the " .. need .. "m line for " .. string.format("%.2f", under)
"""

# LIVE ONLY: the FIRING decision line is a log-only ad_say (a comment in ANN).
OLD_FIRE_SAY = """  FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
    .. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> FIRING"
    .. " (the nearest of the valid enemies; unit_distance is edge-to-edge)")
"""
NEW_FIRE_SAY = """  FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
    .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> FIRING"
    .. " (the nearest of the valid enemies; the gap is centre-to-centre, x/z)")
"""

# ============================================================================
# 5. THE PRE-CAST RE-CHECK (the code is common; the comments differ per copy)
# ============================================================================
OLD_RECHECK_DOC_COMMON = """  -- THE AIR-DROP RE-CHECK (round 114). Immediately before the call the CASTER
  -- must still be ALIVE, still AIRBORNE where its row is air-only and still OUT
  -- of melee where the engine forbids it; the CHOSEN ENEMY must still be alive
  -- with MORE THAN AIR_DROP_MIN_MEN models, and the EDGE gap must still be under
  -- AIR_DROP_EDGE_M. The enemy reads and the distance are RE-TAKEN here from
  -- FRESH handles - the same number_of_men_alive() read and the SAME
  -- unit_distance primitive the picker used, so the two readings cannot
  -- disagree - and a lapsed condition SKIPS the cast rather than spending it.
"""

NEW_RECHECK_DOC_COMMON = """  -- THE AIR-DROP RE-CHECK (round 114, re-measured on the CENTRE in round 117).
  -- Immediately before the call the CASTER must still be ALIVE, still AIRBORNE
  -- where its row is air-only and still OUT of melee where the engine forbids
  -- it; the CHOSEN ENEMY must still be alive with MORE THAN AIR_DROP_MIN_MEN
  -- models, and its CENTRE gap must still be under AIR_DROP_CENTER_M. The
  -- enemy reads and the distance are RE-TAKEN here from FRESH handles - the
  -- same number_of_men_alive() read and the SAME ad_centre_gap measurement the
  -- picker used, so the two readings cannot disagree - and a lapsed condition
  -- SKIPS the cast rather than spending it.
"""

OLD_RECHECK_DOC_LIVE_TAIL = """  -- Every number that decided it is written, with `-> SKIPPED at re-check`.
"""
NEW_RECHECK_DOC_LIVE_TAIL = """  -- Every number that decided it is written, with `-> SKIPPED at re-check`, and
  -- the gap it prints is the CENTRE gap re-measured on this line.
"""

OLD_RECHECK_VARS = """    local edge_now = FOURTH.eg_enemy_gap(unit, enemy)
    local edge_ok = (edge_now ~= nil and edge_now < FOURTH.AIR_DROP_EDGE_M)
    local edge_text = ((edge_now ~= nil) and (string.format("%.2f", edge_now) .. "m") or "?")
"""
NEW_RECHECK_VARS = """    local centre_now = FOURTH.ad_centre_gap(unit, enemy)
    local centre_ok = (centre_now ~= nil and centre_now < FOURTH.AIR_DROP_CENTER_M)
    local centre_text = ((centre_now ~= nil) and (string.format("%.2f", centre_now) .. "m") or "?")
"""

OLD_GAP_OK = """    local gap_ok = (edge_ok or (fallback_now and dwell_ok))
"""
NEW_GAP_OK = """    local gap_ok = (centre_ok or (fallback_now and dwell_ok))
"""

# LIVE: the two log lines. ANN: the two stand-in comments.
OLD_SKIP_LOG = """      log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
        .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
        .. " edge=" .. edge_text .. " (need < "
        .. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> SKIPPED at re-check"
        .. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)
        .. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)
        .. " over_min_men=" .. tostring(men_ok) .. " edge_ok=" .. tostring(edge_ok)
"""
NEW_SKIP_LOG = """      log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
        .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
        .. " centre=" .. centre_text .. " (need < "
        .. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> SKIPPED at re-check"
        .. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)
        .. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)
        .. " over_min_men=" .. tostring(men_ok) .. " centre_ok=" .. tostring(centre_ok)
"""

OLD_FIRE_LOG = """    log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
      .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
      .. " edge=" .. edge_text .. " (need < "
      .. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> FIRING (re-checked)"
"""
NEW_FIRE_LOG = """    log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
      .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
      .. " centre=" .. centre_text .. " (need < "
      .. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> FIRING (re-checked)"
"""

ANN_SKIP_NOTE = """      -- (annotated copy: the SKIPPED-at-re-check line is a log-only line - it
      -- prints the enemy type, entities=<n>, edge=<m>, the 0.10 m line and
      -- which of caster_alive / flying / melee / enemy_alive / over_min_men /
      -- edge_ok lapsed)
"""
ANN_SKIP_NOTE_NEW = """      -- (annotated copy: the SKIPPED-at-re-check line is a log-only line - it
      -- prints the enemy type, entities=<n>, centre=<m>, the 6.0 m line and
      -- which of caster_alive / flying / melee / enemy_alive / over_min_men /
      -- centre_ok lapsed)
"""

ANN_FIRE_NOTE = """    -- (annotated copy: the FIRING (re-checked) line is a log-only line with the
    -- same four fields, re-measured on fresh handles)
"""
ANN_FIRE_NOTE_NEW = """    -- (annotated copy: the FIRING (re-checked) line is a log-only line with the
    -- same four fields, the CENTRE gap re-measured on fresh handles)
"""

ANN_FIRE_SAY_NOTE = """  -- (annotated copy: the FIRING decision line is a log-only line that repeats
  -- the nearest enemy, its entity count, the exact edge and the delay it waited
  -- for on every cast)
"""
ANN_FIRE_SAY_NOTE_NEW = """  -- (annotated copy: the FIRING decision line is a log-only line that repeats
  -- the nearest enemy, its entity count, the exact CENTRE gap and the delay it
  -- waited for on every cast)
"""

# ============================================================================
# 6. THE TOOLTIP + THE FAMILY BOUND
# ============================================================================
OLD_TIP = """  air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models closes to 0.1 m of this unit's edge, after a wait measured from that enemy's velocity at the moment of contact: 0 s if it is running at this unit, 1 s if it is stationary or crossing, 2 s if it is running away, airborne where the ability requires it",
"""
NEW_TIP = """  air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m of this unit's centre, after a wait measured from that enemy's velocity at the moment of contact: 0 s if it is running at this unit, 1 s if it is stationary or crossing, 2 s if it is running away, airborne where the ability requires it",
"""

OLD_BOUND = """  -- ROUND 114: the air-drop family is bounded by its OWN rule, not by the 70%
  -- table. The rule is ONE comparison - the nearest valid enemy's edge-to-edge
  -- unit_distance against FOURTH.AIR_DROP_EDGE_M - so the entry's range_m is
  -- carried for the inventory/diagnostics only and set to that same line; the
  -- evaluator never reads it. The 70% map would otherwise stamp the row's 10 m
  -- range onto it as 7 m, which is not the test any more.
  if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then
    ability.range_m = FOURTH.AIR_DROP_EDGE_M
"""
NEW_BOUND = """  -- ROUND 114: the air-drop family is bounded by its OWN rule, not by the 70%
  -- table. The rule is ONE comparison - the nearest valid enemy's CENTRE gap
  -- against FOURTH.AIR_DROP_CENTER_M (round 117; it was the edge gap) - so the
  -- entry's range_m is carried for the inventory/diagnostics only and set to
  -- that same line; the evaluator never reads it. The 70% map would otherwise
  -- stamp the row's 10 m range onto it as 7 m, which is not the test any more.
  if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then
    ability.range_m = FOURTH.AIR_DROP_CENTER_M
"""

# ============================================================================
# 7. THE FAST-PASS COMMENT
# ============================================================================
OLD_FAST_DOC = """-- VALID enemy (alive, more than AIR_DROP_MIN_MEN models, readable unit_distance)
-- is inside AIR_DROP_NEAR_M = 30 m. Outside 30 m it does nothing but note the
"""
NEW_FAST_DOC = """-- VALID enemy (alive, more than AIR_DROP_MIN_MEN models, readable centre gap)
-- is inside AIR_DROP_NEAR_M = 30 m. Outside 30 m it does nothing but note the
"""

# ============================================================================
# 8. THE ENTRY-BLOCK COMMENT (the family's own doc, near the ABILITIES rows)
# ============================================================================
OLD_ENTRY_RULE = """\t-- THE RULE (round 114, the user's ruling): fire the moment the NEAREST
\t-- VALID enemy's EDGE-TO-EDGE distance - battle_unit:unit_distance - is
\t-- below FOURTH.AIR_DROP_EDGE_M = 0.1 m, where a valid enemy is one that is
"""
NEW_ENTRY_RULE = """\t-- THE RULE (round 114, the user's ruling; the MEASUREMENT moved to the
\t-- CENTRE in round 117): fire the moment the NEAREST VALID enemy's GROUND
\t-- CENTRE distance - position():distance_xz - is below
\t-- FOURTH.AIR_DROP_CENTER_M = 6.0 m, where a valid enemy is one that is
"""

# ============================================================================
# 9. THE HISTORY LISTS that still named the retired constant
# ============================================================================
OLD_HIST_CENTRE = """--   * AIR_DROP_CENTER_M (the 6 m centre bound), the derived frontage credit
"""
NEW_HIST_CENTRE = """--   * the 6 m centre bound (round 117 brought it BACK, as AIR_DROP_CENTER_M)
--     and the derived frontage credit
"""

OLD_HIST_LIVE = """--     ad_centre_gap, ad_pos, ad_sep and ad_vec_text.
"""
NEW_HIST_LIVE = """--     ad_centre_gap, ad_pos, ad_sep and ad_vec_text. (ad_centre_gap came back
--   in round 117 - it is now the ONE measurement the rule makes.)
"""

OLD_HIST_ANN = """--     ad_centre_gap, ad_pos, ad_sep, ad_vec_text. Nothing else in the file used
--     any of them.
"""
NEW_HIST_ANN = """--     ad_centre_gap, ad_pos, ad_sep, ad_vec_text. Nothing else in the file used
--     any of them. (ad_centre_gap came back in round 117 - it is now the ONE
--     measurement the rule makes.)
"""

OLD_115_HIST = """--   * when the NEAREST valid enemy's edge gap first drops under
--     AIR_DROP_EDGE_M the PAIR (caster ui id, enemy ui id) is stamped with the
"""
NEW_115_HIST = """--   * when the NEAREST valid enemy's gap first drops under the line (the
--     CENTRE gap since round 117) the PAIR (caster ui id, enemy ui id) is stamped with the
"""

ANN_116_HEAD = """-- The rule: the nearest valid enemy with more than AIR_DROP_MIN_MEN models must
-- stay under AIR_DROP_EDGE_M for a delay MEASURED at the first contact of the
"""
ANN_116_HEAD_NEW = """-- The rule: the nearest valid enemy with more than AIR_DROP_MIN_MEN models must
-- stay under AIR_DROP_CENTER_M (6 m, centre to centre, x/z) for a delay MEASURED at the first contact of the
"""


OLD_WHY_ANN = """-- battle_unit:unit_distance() is "the shortest distance in metres between this
-- unit and a supplied unit, taking into account their bounding box rather than
-- just working out the centre-to-centre distance" (battle_unit.lua:160). It is
-- the number the user asked for, so it is the number that decides.
"""

OLD_HIST_CENTRE_ANN = """--   * AIR_DROP_CENTER_M and the derived frontage credit
"""


OLD_CONSTS_ANN = """-- THE FOUR CONSTANTS:
--   AIR_DROP_EDGE_M  = 0.10 m  FIRE below this edge-to-edge gap
--   AIR_DROP_MIN_MEN = 10      a candidate needs MORE alive models than this
--   AIR_DROP_NEAR_M  = 30 m    the fast pass runs while a valid enemy is closer
--   AIR_DROP_FAST_S  = 0.2 s   the fast pass interval
FOURTH.AIR_DROP_EDGE_M = 0.1
"""

OLD_NEAR_DOC_ANN = """-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass cannot disagree about who is valid. Returns the
-- nearest valid enemy, its edge gap in metres, its CURRENT model count and its
-- type key; nil when no valid candidate exists or the enemy army is unreadable.
"""

NEW_NEAR_DOC_ANN = """-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass cannot disagree about who is valid. Returns the
-- nearest valid enemy, its CENTRE-to-CENTRE ground gap in metres, its CURRENT
-- model count and its type key; nil when no valid candidate exists or the enemy
-- army is unreadable.
"""

OLD_PICK_DOC_ANN = """-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- edge gap against AIR_DROP_EDGE_M - after the caster-side usage checks the
-- ability's own row declares. (The live build writes, on EVERY decision, the
-- distance, the entity count, the enemy type and the caster's ui id:
--     [1003] sky_junk_bomb nearest valid:'<key>' entities=N edge=0.04m
--            (need < 0.10m) -> NOT YET / FIRING)
"""

NEW_PICK_DOC_ANN = """-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- CENTRE gap against AIR_DROP_CENTER_M - after the caster-side usage checks the
-- ability's own row declares. (The live build writes, on EVERY decision, the
-- distance, the entity count, the enemy type and the caster's ui id:
--     [1003] sky_junk_bomb nearest valid:'<key>' entities=N centre=5.90m
--            (need < 6.00m) -> NOT YET / FIRING)
"""


def apply(path, ann):
    s = rd(path)
    tag = "ANN" if ann else "LIVE"
    if s.count("function FOURTH.ad_centre_gap(caster, enemy)") == 1:
        print(tag + ": already applied - skipped")
        return

    # ---- header / constants / helper
    s = both(s, OLD_RULE, NEW_RULE)
    s = both(s, OLD_WHY_ANN, NEW_WHY) if ann else both(s, OLD_WHY, NEW_WHY)
    s = both(s, OLD_CONSTS_ANN, NEW_CONSTS) if ann else both(s, OLD_CONSTS, NEW_CONSTS)
    if ann:
        s = both(s, OLD_NEAR_DOC_ANN, HELPER + OLD_NEAR_DOC_ANN)
        s = both(s, OLD_NEAR_DOC_ANN, NEW_NEAR_DOC_ANN)
    else:
        s = both(s, OLD_NEAR_DOC, HELPER + OLD_NEAR_DOC)
        s = both(s, OLD_NEAR_DOC, NEW_NEAR_DOC)
    s = both(s, "    local d = FOURTH.eg_enemy_gap(unit, enemy)",
             "    local d = FOURTH.ad_centre_gap(unit, enemy)")
    s = both(s, OLD_PICK_DOC_ANN, NEW_PICK_DOC_ANN) if ann else both(s, OLD_PICK_DOC, NEW_PICK_DOC)
    s = both(s, OLD_UNDER_DOC, NEW_UNDER_DOC)
    s = both(s, OLD_ENTRY_RULE, NEW_ENTRY_RULE)

    # ---- the picker
    s = both(s, OLD_PICK_LOCAL, NEW_PICK_LOCAL)
    s = both(s, OLD_PICK_HOLD_LOG, NEW_PICK_HOLD_LOG)
    s = both(s, OLD_PICK_SEP, NEW_PICK_SEP)
    s = both(s, OLD_NOT_YET, NEW_NOT_YET, 2)
    s = both(s, OLD_REASON_SHORT, NEW_REASON_SHORT)
    s = both(s, OLD_REASON_DWELL, NEW_REASON_DWELL)
    if ann:
        s = both(s, ANN_FIRE_SAY_NOTE, ANN_FIRE_SAY_NOTE_NEW)
    else:
        s = both(s, OLD_FIRE_SAY, NEW_FIRE_SAY)

    # ---- the pre-cast re-check
    s = both(s, OLD_RECHECK_DOC_COMMON, NEW_RECHECK_DOC_COMMON)
    if not ann:
        s = both(s, OLD_RECHECK_DOC_LIVE_TAIL, NEW_RECHECK_DOC_LIVE_TAIL)
    s = both(s, OLD_RECHECK_VARS, NEW_RECHECK_VARS)
    s = both(s, OLD_GAP_OK, NEW_GAP_OK)
    if ann:
        s = both(s, ANN_SKIP_NOTE, ANN_SKIP_NOTE_NEW)
        s = both(s, ANN_FIRE_NOTE, ANN_FIRE_NOTE_NEW)
    else:
        s = both(s, OLD_SKIP_LOG, NEW_SKIP_LOG)
        s = both(s, OLD_FIRE_LOG, NEW_FIRE_LOG)

    # ---- tooltip, family bound, fast-pass doc, history lists
    s = both(s, OLD_TIP, NEW_TIP)
    s = both(s, OLD_BOUND, NEW_BOUND)
    s = both(s, OLD_FAST_DOC, NEW_FAST_DOC)
    if ann:
        s = both(s, OLD_HIST_CENTRE_ANN, NEW_HIST_CENTRE)
        s = both(s, OLD_HIST_ANN, NEW_HIST_ANN)
        s = both(s, ANN_116_HEAD, ANN_116_HEAD_NEW)
    else:
        s = both(s, OLD_HIST_LIVE, NEW_HIST_LIVE)
        s = both(s, OLD_HIST_CENTRE, NEW_HIST_CENTRE)
        s = both(s, OLD_115_HIST, NEW_115_HIST)

    # ---- the invariants
    left = s.count("AIR_DROP_EDGE_M")
    if left != 0:
        i = s.index("AIR_DROP_EDGE_M")
        print("REMAINING in " + tag + ": ..." + s[i - 200:i + 120].replace("\n", "\\n") + "...")
    assert left == 0, "%s: AIR_DROP_EDGE_M still appears %d time(s)" % (tag, left)
    assert s.count("\nFOURTH.AIR_DROP_CENTER_M = 6.0\n") == 1, tag + ": the constant is defined once"
    n_c = s.count("AIR_DROP_CENTER_M")
    assert n_c >= 8, "%s: only %d mentions of AIR_DROP_CENTER_M" % (tag, n_c)
    assert s.count("function FOURTH.ad_centre_gap(caster, enemy)") == 1, tag + ": helper"
    assert s.count("FOURTH.ad_centre_gap(") == 4, (tag + ": helper call sites = %d"
                                                  % s.count("FOURTH.ad_centre_gap("))
    pick = s[s.index("function FOURTH.ad_pick(unit, routing)"):]
    pick = pick[:pick.index("function FOURTH.evaluate_air_drop_on_infantry")]
    assert "eg_enemy_gap" not in pick, tag + ": the picker still calls eg_enemy_gap"
    if ann:
        assert "log(" not in s, "ANN: the reading copy must stay log-free"
    wr(path, s)
    print(tag + ": " + str(len(s)) + " bytes, 0 CR, centre mentions " + str(n_c))


apply(LIVE, False)
apply(ANN, True)
print("OK - round 117 centre-gap edit applied to both copies")
