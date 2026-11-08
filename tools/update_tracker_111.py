"""Round 111 tracker update - the moving-caster dials.

1. All 19 air-drop rows: the round-110 rule parenthetical is replaced by the
   round-111 text that names the two caster dials and carries the tuning order.
2. The trigger-family glossary row for air_drop_on_infantry is brought to
   round 111 (caster dials, enemy unchanged, tuning order).
3. A new dated Update paragraph is inserted after the harness-110 update.
"""
import io

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
s = io.open(P, encoding="utf-8", newline="").read()
assert "\r" not in s
before = s

OLD_ROW = s[s.find("((**round 110: TWO-BODY"):]
OLD_ROW = OLD_ROW[: OLD_ROW.find("raise it if it never fires)") + len("raise it if it never fires)")]
assert s.count(OLD_ROW) == 19, s.count(OLD_ROW)
assert OLD_ROW.startswith("((**round 110: TWO-BODY")

NEW_ROW = (
    "((**round 111: THE MOVING-CASTER DIALS** - the user's fourth field report, verbatim: "
    "*\"I tested it. It seems to work okay when the caster is stationary, but it definitely drops the "
    "rocks too soon when in movement.\"* A **stationary** caster is right, so the **ENEMY** projection "
    "and the **6 m** bound are right and are NOT touched; the error exists only while the caster "
    "moves and it fires TOO SOON, so the caster's lead term is OVER-STATED. The caster is therefore "
    "projected by **its own two dials** - "
    "`caster(t) = caster + v_caster * FOURTH.AIR_DROP_CASTER_DELAY_S * FOURTH.AIR_DROP_CASTER_LEAD` "
    "(**1.5 s**, **0.5** shipped) - while the enemy keeps "
    "`enemy(t) = enemy + v_enemy * FOURTH.AIR_DROP_DELAY_S` in full, and the drop fires when the "
    "**PROJECTED** horizontal CENTRE-TO-CENTRE separation (X/Z only - `battle_vector:get_y()` is "
    "HEIGHT) is inside **`FOURTH.AIR_DROP_CENTER_M = 6 m`**. `AIR_DROP_CASTER_LEAD` **0.0** treats "
    "the caster as STATIONARY (impact at the cast position - the case the field says is right) and "
    "**1.0** is the round-110 behaviour that over-leads; the pair (1.5, 0.5) is the starting point "
    "and **only ONE dial changes per field test**. **TUNING ORDER:** fires **early while MOVING** -> "
    "lower the lead **0.5 -> 0.3 -> 0.0**, then `AIR_DROP_CASTER_DELAY_S` **1.5 -> 1.0**; still "
    "**early while STATIONARY** -> the fall time itself is too long, lower `FOURTH.AIR_DROP_DELAY_S` "
    "(it shrinks BOTH bodies); **never fires while MOVING** -> raise the lead **0.5 -> 0.8 -> 1.0**. "
    "The velocity is still REBUILT - no vector exists in the API - from `is_moving()`, "
    "`is_moving_fast()`, `slow_speed()` / `fast_speed()` (m/s) and a heading from "
    "`ordered_position()` (= `normalise(ordered - current)`); `bearing()` is the **CASTER-ONLY** "
    "fallback while moving; every unreadable read is **ZERO velocity with a named source** "
    "(`stationary` / `moving-unreadable` / `no-speed` / `no-heading`), so motion is never invented. "
    "**Unchanged:** the ordnance does NOT inherit the caster's velocity (`FOURTH.AIR_DROP_INHERIT = "
    "false` is still the ONE flag - `true` adds the lead term a SECOND time), the 6 m bound standing "
    "in for the formation footprint (the API has no per-unit radius / bbox / size read), "
    "`air_only` / `no_melee` per row, the self-centred cast on the OWNER, fail-closed behaviour, and "
    "the pre-cast re-check - which re-projects through the SAME helper and therefore reads the SAME "
    "two dials. The decision line prints `from delay_caster=1.50s lead=0.50`, plus "
    "`moving caster: lead=0.50 of 1.50s` **only** when the caster's velocity is non-zero)"
)
s = s.replace(OLD_ROW, NEW_ROW)

# ---------------------------------------------------------------- glossary row
G_OLD = ("| `air_drop_on_infantry` | **round 110** - an enemy INFANTRY unit that will be UNDER the "
         "caster WHEN THE ORDNANCE LANDS: BOTH bodies are projected "
         "**`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** forward (a TUNABLE constant - no row carries a fall "
         "time) and the **PROJECTED** horizontal CENTRE-TO-CENTRE separation")
G_NEW = ("| `air_drop_on_infantry` | **rounds 110-111** - an enemy INFANTRY unit that will be UNDER "
         "the caster WHEN THE ORDNANCE LANDS: the **CASTER** is projected by its OWN two dials - "
         "**`FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s` x `FOURTH.AIR_DROP_CASTER_LEAD = 0.5`** - and "
         "the **ENEMY** by **`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** in full (a TUNABLE constant - no row "
         "carries a fall time); the drop fires when the **PROJECTED** horizontal CENTRE-TO-CENTRE "
         "separation")
assert s.count(G_OLD) == 1
s = s.replace(G_OLD, G_NEW)

G_END_OLD = ("The log prints, per decision, the delay, the momentum mode, both bodies' current point "
             "+ velocity + source + projected point, the PROJECTED and instant separations and the "
             "bound, plus a `watch:` band line naming the nearest infantry and both velocities when "
             "nothing qualifies. |")
G_END_NEW = ("The log prints, per decision, the two caster dials (`from delay_caster=1.50s lead=0.50`, "
             "plus `moving caster: lead=0.50 of 1.50s` only when the caster is moving), the momentum "
             "mode, both bodies' current point + velocity + source + projected point, the PROJECTED and "
             "instant separations and the bound, plus a `watch:` band line naming the nearest infantry "
             "and both velocities when nothing qualifies. **`AIR_DROP_CASTER_LEAD` 0.0 = the caster "
             "treated as stationary, 1.0 = the round-110 over-lead; TUNING ORDER: early while moving "
             "-> lower the lead 0.5 -> 0.3 -> 0.0 (then the caster delay 1.5 -> 1.0); early while "
             "stationary -> lower the shared `AIR_DROP_DELAY_S`; never fires while moving -> raise the "
             "lead 0.5 -> 0.8 -> 1.0. ONE dial per test.** |")
assert s.count(G_END_OLD) == 1
s = s.replace(G_END_OLD, G_END_NEW)

# ------------------------------------------------------- the dated Update entry
ANCHOR = ("installed pack md5 `588e6c3c6781d02321ce7b31af04884f`; `zz_probe_dist.pack` left installed "
          "(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n")
assert s.count(ANCHOR) == 1

UPDATE = (
    "**Update 2026-10-18 (harness 111 - THE MOVING-CASTER DIALS: ONLY THE CASTER'S LEAD MOVES).** "
    "One field report is **implemented and shipping**: the user's fourth air-drop test - *\"I tested "
    "it. It seems to work okay when the caster is stationary, but it definitely drops the rocks too "
    "soon when in movement. How do we tune it?\"* **THE READING, AS ARITHMETIC:** a stationary caster "
    "is RIGHT, so the **enemy** projection and the **6 m** bound are RIGHT and must not be touched; "
    "the error appears only while the caster moves and fires **too soon**, so the caster's projected "
    "point runs AHEAD of the real impact point - the caster's lead term is **over-stated** (round 110 "
    "gave it the full 1.5 s: 12 m of lead at 8 m/s, when in practice the release happens part-way "
    "through the wind-up or the flier has already turned into the pass). **THE FIX - TWO DIALS ON THE "
    "CASTER ONLY:** `caster_projected = caster + v_caster * FOURTH.AIR_DROP_CASTER_DELAY_S * "
    "FOURTH.AIR_DROP_CASTER_LEAD` (**1.5 s**, **0.5** shipped) while `enemy_projected = enemy + "
    "v_enemy * FOURTH.AIR_DROP_DELAY_S` keeps its full term; the drop still fires when the PROJECTED "
    "horizontal centre separation is inside the same **6 m**. At the shipped pair the caster leads by "
    "**half** its travel (8 m/s -> 6 m, not 12 m), and a **parked** caster is identical at every dial "
    "value because the term multiplies zero velocity - exactly the case the field says is right. "
    "`AIR_DROP_CASTER_LEAD` **0.0** = the caster treated as stationary, **1.0** = the round-110 "
    "behaviour. **KEPT EXACTLY:** the enemy term and its delay, the 6 m bound, `AIR_DROP_INHERIT`, "
    "`air_only` / `no_melee` per row, the self-centred cast on the OWNER, every fail-closed read, the "
    "70% map exemption, and the pre-cast re-check - which re-projects through the SAME helper and so "
    "reads the SAME two dials (a world where the pick is taken at lead 0.5 and the re-check disagrees "
    "is impossible by construction). **THE LOG:** the decision line, the `watch:` line and both "
    "pre-cast lines now print `delay_caster=1.50s lead=0.50`, plus a `moving caster: lead=0.50 of "
    "1.50s` fragment **only** when the caster's velocity is non-zero (a parked caster's lead term did "
    "nothing, and a fragment there would invite tuning the wrong dial). **TUNING ORDER - ONE DIAL PER "
    "TEST:** fires **early while MOVING** -> lower `AIR_DROP_CASTER_LEAD` **0.5 -> 0.3 -> 0.0**, and "
    "only if 0.0 is still early lower `AIR_DROP_CASTER_DELAY_S` **1.5 -> 1.0** (the caster's own "
    "time, the enemy prediction untouched); still **early while STATIONARY** -> the fall time itself "
    "is too long, lower `AIR_DROP_DELAY_S` (it shrinks both bodies and returns the round-109 shape "
    "for a parked pair); **never fires while MOVING** -> raise the lead back **0.5 -> 0.8 -> 1.0**. "
    "**NO COUNTS MOVED:** 689 entries / 742 keys, `air_drop_on_infantry` **12 entries / 19 keys**, 46 "
    "evaluators - behaviour only. Spreadsheet `docs/WH3_abilities_master_v12_2026-10-18.xlsx` (+ "
    "`.ods`; v12 supersedes v11; **v1-v11 byte-unchanged**); round doc "
    "`docs/WH3_round111_airdrop_movingcaster.md`; harness 111: **4387 checks / 0 failures** (run "
    "twice, byte-identical), red control (the round-110 build) **41 failures, ALL in the new section "
    "and all accounted for**; installed pack md5 `651f12e61284cae472bb06bf3a66b87d`; "
    "`zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n"
)
s = s.replace(ANCHOR, ANCHOR + UPDATE)

assert s != before
assert s.count("round 111: THE MOVING-CASTER DIALS") == 19, s.count("round 111: THE MOVING-CASTER DIALS")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker updated:", len(before), "->", len(s))
print("air-drop rows carrying the round-111 rule:", s.count("((**round 111: THE MOVING-CASTER DIALS**"))
print("update paragraph present:", s.count("harness 111 - THE MOVING-CASTER DIALS"))
