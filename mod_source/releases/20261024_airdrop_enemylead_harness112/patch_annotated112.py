"""Mirror the round-112 edits into the annotated (reading) copy.

The annotated copy is the same logic with the log calls replaced by placeholder
comments; it must carry every constant, the projection maths and the exact-metre
watch text, and must stay LOG-FREE (no `log(`) and find-free.
"""
import io

ANN = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"

s = io.open(ANN, encoding="utf-8", newline="").read()
assert "\r" not in s

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# ---------------------------------------------------------------- 1. constants
rep("""-- THE FORMULA NOW (FOURTH.ad_lead, caster arm):
--     caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
--     enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
-- and the drop fires when the PROJECTED horizontal centre separation is inside
-- FOURTH.AIR_DROP_CENTER_M = 6 m.
FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5
FOURTH.AIR_DROP_CASTER_LEAD = 0.5""",
"""-- ROUND 112 ADDS THE FOURTH DIAL, ON THE ENEMY'S TERM (see below). THE FORMULA
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
FOURTH.AIR_DROP_ENEMY_LEAD = 0.3""")

# ---------------------------------------------------------------- 2. tuning guide
rep("""-- THE TWO DIALS - change ONE per field test, in this order:
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
-- term moved the impact point.""",
"""-- THE FOUR DIALS - change ONE per field test. THE DEFAULTS THAT SHIP:
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
-- caster_lead=0.50`) says which term moved the impact point.""")

# ---------------------------------------------------------------- 3. ad_lead
rep("""-- ROUND 111 - THE CASTER'S LEAD IS ITS OWN TERM. The CASTER is projected
--     caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
-- while an enemy is still projected by the shared t (FOURTH.AIR_DROP_DELAY_S) in
-- full. The two dials are read HERE, on every call, so the pre-cast re-check""",
"""-- ROUND 111 - THE CASTER'S LEAD IS ITS OWN TERM. The CASTER is projected
--     caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
-- ROUND 112 - SO IS THE ENEMY'S. An enemy is projected by the shared
--     enemy  + v_enemy  * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD
-- and the two dials are read HERE, on every call, so the pre-cast re-check""")

rep("""\t-- the caster's own lead time and the share of it; the enemy's stays t
\tlocal t_caster, lead_caster = t, 1
\tif allow_bearing == true then
\t\tlocal d_caster = FOURTH.AIR_DROP_CASTER_DELAY_S
\t\tif type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end
\t\tlocal l_caster = FOURTH.AIR_DROP_CASTER_LEAD
\t\tif type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end
\tend
\tlocal vx, vz, speed, src = FOURTH.ad_velocity(unit, allow_bearing)
\tlocal px, pz = x + vx * t, z + vz * t
\tif allow_bearing == true then""",
"""\t-- the caster's own lead time and the share of it; the enemy's delay stays t
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
\tif allow_bearing == true then""")

# ---------------------------------------------------------------- 4. ad_dial_text
rep("""-- THE TWO DIALS AS LOG TEXT (round 111) - the log build lives in the shipped
-- file; the reading copy keeps the helper so both trees stay call-compatible.
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
\tend""",
"""-- THE FOUR DIALS AS LOG TEXT (round 112) - the log build lives in the shipped
-- file; the reading copy keeps the helper so both trees stay call-compatible.
-- The text is `delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`.
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
\tend""")

# ---------------------------------------------------------------- 5. the watch block
rep("""\t\t-- separation is inside 30 m, and banded at 5 m so one line appears per
\t\t-- band rather than per 0.1 m. The exact numbers are on the target line and
\t\t-- on the pre-cast re-check.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\t-- (annotated copy: the why-not band line is a log-only line)
\t\t\tlocal band = math.floor(near_gap / 5) * 5
\t\t\tlocal nband = math.floor(near_now / 5) * 5
\t\t\tFOURTH.ad_say(unit, marker, "watch: nearest INFANTRY '"
\t\t\t\t.. (FOURTH.type_plain(near) or "enemy") .. "' is centre=~"
\t\t\t\t.. string.format("%.0f", nband) .. "m vs bound=" .. tostring(bound)
\t\t\t\t.. "m -> NOT under the caster"
\t\t\t\t.. " [projected sep=~" .. string.format("%.0f", band)
\t\t\t\t.. "m after delay=" .. string.format("%.2f", ad_t) .. "s; caster v=\"""",
"""\t\t-- separation is inside 30 m, and THE DECIDING NUMBER IS NEVER BANDED
\t\t-- (round 112, diagnosis D1: the 6 m bound sat inside a 5 m band, so
\t\t-- "~5m" covered 5.00-9.99 m and the one number needed to choose a new
\t\t-- bound was destroyed exactly where it mattered). Below 15 m BOTH numbers
\t\t-- print EXACTLY (%.2f); at 15 m and above the 5 m band stays.
\t\tif near ~= nil and near_gap <= 30 then
\t\t\t-- (annotated copy: the why-not watch line is a log-only line)
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
\t\t\t\t.. " after delay=" .. string.format("%.2f", ad_t) .. "s; caster v=\"""")

# the annotated copy must stay LOG-FREE
assert "log(" not in s.replace("blog(", "") or True
assert "\r" not in s
io.open(ANN, "w", encoding="utf-8", newline="").write(s)
print("annotated copy updated:", len(s.encode("utf-8")), "bytes")
import re
bad = [l for l in s.split("\n") if re.search(r"(?<![A-Za-z_])log\(", l)]
print("log( lines:", len(bad))
assert not bad, bad[:3]
