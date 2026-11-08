"""Reconstruct the round-111 live source (the PRE-112 snapshot) from the edited file.

The round-112 edits are nine self-contained block replacements, recorded as
(new -> old) pairs here, so the pre-edit file can be rebuilt byte-exactly. The
rebuild is PROVEN by size and line count: the round-111 file was 782,275 bytes
and 15,799 lines (wc -l, taken before any round-112 edit). If either differs the
script aborts - a wrong red-control snapshot would make the whole red run
meaningless.
"""
import io

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
DST = r"C:/Users/vlady/Desktop/WH3_mod/docs/backups/round112/pre112_zz_test_deadly_onslaught.lua"
WANT_BYTES = 782275
WANT_LINES = 15799

s = io.open(SRC, encoding="utf-8", newline="").read()
assert "\r" not in s

PAIRS = []

# 1. the formula comment + the enemy dial constant
PAIRS.append(("""-- ROUND 112 ADDS THE FOURTH DIAL, ON THE ENEMY'S TERM (see below). THE FORMULA
-- NOW - FOUR DIALS, TWO PER BODY (FOURTH.ad_lead):
--     caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
--     enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S       * AIR_DROP_ENEMY_LEAD
-- and the drop fires when the PROJECTED horizontal centre separation is inside
-- FOURTH.AIR_DROP_CENTER_M = 6 m.
FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5
FOURTH.AIR_DROP_CASTER_LEAD = 0.5
-- ROUND 112 - THE ENEMY-SIDE DIAL: THE SAME QUALIFICATION, ON THE ENEMY'S TERM.
--
-- THE FIELD EVIDENCE (Sky-junk bomb, four units, the zombies walking THROUGH
-- underneath HOVERING casters): for a caster that does not move, the enemy's
-- FULL 1.5 s carry was carried PAST the hoverer - at the zombie's 2.3 m/s that is
-- v_enemy * AIR_DROP_DELAY_S = 3.45 m of lead - so the projected gap bottomed
-- out around 5 m and then GREW to 10 m, LARGEST exactly when the enemy was
-- underneath. Three of the four units therefore never fired for a whole pass
-- (the fourth fired at a projected 3.5 m on a different approach). The 6 m bound
-- and the caster's dials were not at fault: the ENEMY's lead was.
--
-- 0.0 = the enemy's CURRENT position (the ordnance lands straight down on where
-- the enemy is now); 1.0 = the round-110/111 behaviour, the full 1.5 s carry
-- that produced those misses; 0.3 SHIPS - a small lead is right because the
-- release is not instantaneous and a walking target really does move during the
-- fall, but 30% of 1.5 s is 0.45 s, about 1.0 m at 2.3 m/s, not 3.45 m.
--
-- It scales ONLY the enemy's velocity term. The caster's two dials, the shared
-- delay FOURTH.AIR_DROP_DELAY_S, the 6 m bound, FOURTH.AIR_DROP_INHERIT,
-- air_only / no_melee, the self-centred cast and the pre-cast re-check (which
-- re-projects through the SAME helper, so it reads the SAME four dials) are
-- untouched.
FOURTH.AIR_DROP_ENEMY_LEAD = 0.3""",
"""-- THE FORMULA NOW (FOURTH.ad_lead, caster arm):
--     caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
--     enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
-- and the drop fires when the PROJECTED horizontal centre separation is inside
-- FOURTH.AIR_DROP_CENTER_M = 6 m.
FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5
FOURTH.AIR_DROP_CASTER_LEAD = 0.5"""))

# 2. the tuning guide
PAIRS.append(("""-- THE FOUR DIALS - change ONE per field test. THE DEFAULTS THAT SHIP:
--     AIR_DROP_DELAY_S        = 1.5 s   the enemy's lead time (the fall time)
--     AIR_DROP_ENEMY_LEAD     = 0.3     the enemy's share of it
--     AIR_DROP_CASTER_DELAY_S = 1.5 s   the caster's own lead time
--     AIR_DROP_CASTER_LEAD    = 0.5     the caster's share of it
--     (AIR_DROP_CENTER_M = 6 m is the BOUND, not a lead; AIR_DROP_INHERIT is the
--      momentum flag, not a lead.)
-- WHAT TO CHANGE FOR WHICH SYMPTOM:
--   * the ENEMY WALKS THROUGH underneath while the caster HOVERS -> the enemy's
--     lead is over-stated: lower AIR_DROP_ENEMY_LEAD 0.3 -> 0.0 (0.0 = impact on
--     the enemy's CURRENT position). This is the round-112 Sky-junk report.
--   * the CASTER CHASES a STANDING target and fires EARLY -> the caster's lead
--     is over-stated: AIR_DROP_CASTER_LEAD - LOWER the lead: 0.5 -> 0.3 -> 0.0
--     (the round-111 report, "fires EARLY while MOVING"). If 0.0 is still early,
--     lower AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0.
--   * fires LATE when BOTH move -> the relevant lead has been cut too far: raise
--     the one that matches the body that was moving. "NEVER fires while MOVING"
--     -> AIR_DROP_CASTER_LEAD 0.5 -> 0.8 -> 1.0; a walking target that is never
--     hit -> AIR_DROP_ENEMY_LEAD 0.3 -> 0.6 -> 1.0.
--   * still EARLY while STATIONARY (both bodies parked) -> the shared delay
--     itself is too long: lower AIR_DROP_DELAY_S (it shrinks both bodies and
--     returns the round-109 shape for a parked pair).
-- The four defaults (1.5 / 0.3 / 1.5 / 0.5) are the STARTING POINT.
-- Only ONE dial changes per test, so the field log (which prints all four on every
-- air-drop line: `delay=1.50s enemy_lead=0.30 delay_caster=1.50s
-- caster_lead=0.50`) says which term moved the impact point.""",
"""-- THE TWO DIALS - change ONE per field test, in this order:
--   1. AIR_DROP_CASTER_LEAD - the share of the caster's own lead that is real.
--      1.0 = the round-110 behaviour (the caster projected the full delay
--      ahead, the setting that over-leads); 0.0 = the caster treated as
--      STATIONARY (impact at the cast position, the case the field says is
--      right). 0.5 ships: half the caster's travel, i.e. the release is treated
--      as happening part-way into the delay.
--   2. AIR_DROP_CASTER_DELAY_S - the caster's OWN lead time, independent of the
--      enemy's. 1.5 = the shared fall time; lower it to shorten the caster's
--      lead alone without moving the enemy prediction.
-- WHAT TO CHANGE FOR WHICH SYMPTOM:
--   * fires EARLY while MOVING -> LOWER the lead: 0.5 -> 0.3 -> 0.0; if 0.0 is
--     still early, lower AIR_DROP_CASTER_DELAY_S: 1.5 -> 1.0.
--   * still EARLY while STATIONARY -> the shared delay itself is too long:
--     lower AIR_DROP_DELAY_S (it shrinks both bodies and returns the round-109
--     shape for a parked pair).
--   * NEVER fires while MOVING -> raise the lead back up: 0.5 -> 0.8 -> 1.0.
-- The pair (AIR_DROP_CASTER_DELAY_S = 1.5, AIR_DROP_CASTER_LEAD = 0.5) is the
-- STARTING POINT. Only ONE dial changes per test, so the field log says which
-- term moved the impact point."""))

# 3. the tag helper + ad_say
PAIRS.append(("""-- THE UNIT TAG (round 112) - EVERY air-drop line names the unit that wrote it:
--     [1003] sky_junk_bomb watch: nearest INFANTRY ...
-- The round-112 diagnosis was taken against FOUR identical
-- wh3_main_cth_veh_sky_junk_0 units (ui ids 1002-1005) and the picker's own
-- lines carried no ui id at all, so "which of the four said this?" had to be
-- inferred from line counts in a 231 MB log. The id is the engine's
-- unique_ui_id(); an unreadable id (the unit died between the read and the log)
-- prints [?] rather than dropping the line - a line with an unknown owner is
-- still better than no line.
function FOURTH.ad_tag(unit)
\tlocal ok_id, id = pcall(function() return unit:unique_ui_id() end)
\tif not ok_id or id == nil then return "[?] " end
\treturn "[" .. tostring(id) .. "] "
end

-- One line per (unit, marker), and again only when the note CHANGES - the same
-- dedupe discipline as the engagement set, so a hovering unit does not flood
-- the log while it waits. The note is what is de-duplicated (the tag is not part
-- of the key), and every line - watch, skip, airborne/melee hold - carries the
-- unit's own tag.
function FOURTH.ad_say(unit, marker, note)""",
"""-- One line per (unit, marker), and again only when the note CHANGES - the same
-- dedupe discipline as the engagement set, so a hovering unit does not flood
-- the log while it waits.
function FOURTH.ad_say(unit, marker, note)"""))

PAIRS.append(("""\t\tlog("  " .. FOURTH.ad_tag(unit) .. tostring(marker) .. " " .. note)""",
              """\t\tlog("  " .. tostring(marker) .. " " .. note)"""))

# 4. ad_lead
PAIRS.append(("""-- ROUND 111 - THE CASTER'S LEAD IS ITS OWN TERM. The CASTER is projected
--     caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
-- ROUND 112 - SO IS THE ENEMY'S. An enemy is projected by the shared
--     enemy  + v_enemy  * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD
-- and the two dials are read HERE, on every call, so the pre-cast re-check""",
"""-- ROUND 111 - THE CASTER'S LEAD IS ITS OWN TERM. The CASTER is projected
--     caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
-- while an enemy is still projected by the shared t (FOURTH.AIR_DROP_DELAY_S) in
-- full. The two dials are read HERE, on every call, so the pre-cast re-check"""))

PAIRS.append(("""\t-- the caster's own lead time and the share of it; the enemy's delay stays t
\tlocal t_caster, lead_caster = t, 1
\tif allow_bearing == true then
\t\tlocal d_caster = FOURTH.AIR_DROP_CASTER_DELAY_S
\t\tif type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end
\t\tlocal l_caster = FOURTH.AIR_DROP_CASTER_LEAD
\t\tif type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end
\tend
\t-- ROUND 112: the ENEMY's share of its own delay. Read only on the enemy arm
\t-- (allow_bearing false), so the caster's two dials above are never mixed
\t-- with it; an unreadable value falls back to 1.0, the round-110/111 carry.
\tlocal lead_enemy = 1
\tif allow_bearing ~= true then
\t\tlocal l_enemy = FOURTH.AIR_DROP_ENEMY_LEAD
\t\tif type(l_enemy) == "number" and l_enemy >= 0 then lead_enemy = l_enemy end
\tend
\tlocal vx, vz, speed, src = FOURTH.ad_velocity(unit, allow_bearing)
\t-- the full-delay line: the enemy's term at lead 1.0, and the fallback shape
\tlocal px, pz = x + vx * t, z + vz * t
\tif allow_bearing ~= true and lead_enemy ~= 1 then
\t\t-- 0.0 = the enemy's CURRENT position; 0.3 = the shipped share
\t\tpx = x + vx * t * lead_enemy
\t\tpz = z + vz * t * lead_enemy
\tend
\tif allow_bearing == true then""",
"""\t-- the caster's own lead time and the share of it; the enemy's stays t
\tlocal t_caster, lead_caster = t, 1
\tif allow_bearing == true then
\t\tlocal d_caster = FOURTH.AIR_DROP_CASTER_DELAY_S
\t\tif type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end
\t\tlocal l_caster = FOURTH.AIR_DROP_CASTER_LEAD
\t\tif type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end
\tend
\tlocal vx, vz, speed, src = FOURTH.ad_velocity(unit, allow_bearing)
\tlocal px, pz = x + vx * t, z + vz * t
\tif allow_bearing == true then"""))

# 5. ad_dial_text
PAIRS.append(("""-- THE FOUR DIALS AS LOG TEXT (round 112 - round 111 printed only the caster's
-- two, which is why a STATIONARY-caster miss could not be attributed to the
-- enemy's term from the log at all). Printed on every air-drop line so the user
-- can see WHICH term produced each projected point:
--     delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50
-- plus a `moving caster: lead=0.50 of 1.50s` fragment ONLY when the caster's
-- velocity is non-zero (a parked caster's lead term is inert, and a fragment
-- there would invite tuning the wrong dial). Values are read from the live
-- constants, never recomputed; an unreadable constant falls back to the value
-- FOURTH.ad_lead itself would use.
function FOURTH.ad_dial_text(moving)
\tlocal d = FOURTH.AIR_DROP_DELAY_S
\tif type(d) ~= "number" then d = 0 end
\tlocal le = FOURTH.AIR_DROP_ENEMY_LEAD
\tif type(le) ~= "number" then le = 1 end
\tlocal d_c = FOURTH.AIR_DROP_CASTER_DELAY_S
\tif type(d_c) ~= "number" then d_c = d end
\tlocal l_c = FOURTH.AIR_DROP_CASTER_LEAD
\tif type(l_c) ~= "number" then l_c = 1 end
\tlocal s = "delay=" .. string.format("%.2f", d) .. "s "
\t\t.. "enemy_lead=" .. string.format("%.2f", le) .. " "
\t\t.. "delay_caster=" .. string.format("%.2f", d_c) .. "s "
\t\t.. "caster_lead=" .. string.format("%.2f", l_c)
\tif moving == true then
\t\ts = s .. " moving caster: lead=" .. string.format("%.2f", l_c)
\t\t\t.. " of " .. string.format("%.2f", d_c) .. "s"
\tend""",
"""-- THE TWO DIALS AS LOG TEXT (round 111). Printed on every air-drop decision so
-- the user can see WHICH term produced the projected point: `delay_caster=1.50s
-- lead=0.50`, plus a `moving caster: lead=0.50 of 1.50s` fragment ONLY when the
-- caster's velocity is non-zero (a parked caster's lead term is inert, and a
-- fragment there would invite tuning the wrong dial). Values are read from the
-- live constants, never recomputed.
function FOURTH.ad_dial_text(moving)
\tlocal d = FOURTH.AIR_DROP_CASTER_DELAY_S
\tif type(d) ~= "number" then d = FOURTH.AIR_DROP_DELAY_S end
\tif type(d) ~= "number" then d = 0 end
\tlocal l = FOURTH.AIR_DROP_CASTER_LEAD
\tif type(l) ~= "number" then l = 1 end
\tlocal s = "delay_caster=" .. string.format("%.2f", d) .. "s lead=" .. string.format("%.2f", l)
\tif moving == true then
\t\ts = s .. " moving caster: lead=" .. string.format("%.2f", l)
\t\t\t.. " of " .. string.format("%.2f", d) .. "s"
\tend"""))

# 6. the watch line
PAIRS.append(("""\t\t-- separation is inside 30 m, and THE DECIDING NUMBER IS NEVER BANDED
\t\t-- (round 112, diagnosis D1: the 6 m bound sat inside a 5 m band, so
\t\t-- "~5m" covered 5.00-9.99 m and the one number needed to choose a new
\t\t-- bound was destroyed exactly where it mattered). Below 15 m BOTH numbers
\t\t-- print EXACTLY (%.2f); at 15 m and above, where the number is context
\t\t-- only, the 5 m band stays so the log does not grow per 0.1 m.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\tlocal gap_text, now_text
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
\t\t\tFOURTH.ad_say(unit, marker, "watch: nearest INFANTRY '"
\t\t\t\t.. (FOURTH.type_plain(near) or "enemy") .. "' is centre="
\t\t\t\t.. now_text .. " vs bound=" .. tostring(bound)
\t\t\t\t.. "m -> NOT under the caster"
\t\t\t\t.. " [projected sep=" .. gap_text
\t\t\t\t.. " after delay=" .. string.format("%.2f", ad_t) .. "s; caster v=\"""",
"""\t\t-- separation is inside 30 m, and banded at 5 m so one line appears per
\t\t-- band rather than per 0.1 m. The exact numbers are on the target line and
\t\t-- on the pre-cast re-check.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\tlocal band = math.floor(near_gap / 5) * 5
\t\t\tlocal nband = math.floor(near_now / 5) * 5
\t\t\tFOURTH.ad_say(unit, marker, "watch: nearest INFANTRY '"
\t\t\t\t.. (FOURTH.type_plain(near) or "enemy") .. "' is centre=~"
\t\t\t\t.. string.format("%.0f", nband) .. "m vs bound=" .. tostring(bound)
\t\t\t\t.. "m -> NOT under the caster"
\t\t\t\t.. " [projected sep=~" .. string.format("%.0f", band)
\t\t\t\t.. "m after delay=" .. string.format("%.2f", ad_t) .. "s; caster v=\""""))

# 7-9. the three tagged log lines
PAIRS.append(("""\tlog("  " .. FOURTH.ad_tag(unit) .. marker .. " target: '" .. etype .. "' is UNDER the caster\"""",
              """\tlog("  " .. marker .. " target: '" .. etype .. "' is UNDER the caster\""""))
PAIRS.append(("""\t\t\t\t\t\tlog("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " SKIPPED: the drop lapsed before the cast\"""",
              """\t\t\t\t\t\tlog("  " .. ad_marker_now .. " SKIPPED: the drop lapsed before the cast\""""))
PAIRS.append(("""\t\t\t\tlog("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " pre-cast re-check: still over an INFANTRY enemy\"""",
              """\t\t\t\tlog("  " .. ad_marker_now .. " pre-cast re-check: still over an INFANTRY enemy\""""))
PAIRS.append(("""\t\t\t\tthe caster's velocity is non-zero""", """\t\t\t\tthe caster's velocity is non-zero""")) if False else None

out = s
for new, old in PAIRS:
    assert out.count(new) == 1, (out.count(new), new[:70])
    out = out.replace(new, old)

nbytes = len(out.encode("utf-8"))
nlines = out.count("\n")
assert nbytes == WANT_BYTES, (nbytes, WANT_BYTES)
assert nlines == WANT_LINES, (nlines, WANT_LINES)
assert "AIR_DROP_ENEMY_LEAD" not in out
assert "function FOURTH.ad_tag" not in out
io.open(DST, "w", encoding="utf-8", newline="").write(out)
print("wrote", DST, nbytes, "bytes,", nlines, "lines - matches the round-111 file")
