#!/usr/bin/env python3
"""Build WH3_abilities_master_v18_2026-10-18.xlsx from v17.

SIGN-OFF PASS. Rounds 117 and 118 shipped in LIGHT mode (air-drop harness
sections only, no workbook), so v17 still describes round 116's measured
delay - machinery that no longer exists in the shipped script.

Edits, on all 19 air-drop rows (columns 19 and 22): the SHIPPED round-118 rule
- the nearest ALIVE enemy with more than 10 models whose HORIZONTAL
CENTRE-to-CENTRE distance is under FOURTH.AIR_DROP_CENTER_M = 6.0 m, cast on
the evaluation that measures it, with no wait, no projection, no fallback and
no edge measurement.

Definitions: the trigger-family glossary line for air_drop_on_infantry is
rewritten; sections 12/13/14 are RETITLED as RETIRED with a one-line reason
each (sections 8-11 already carried round 114's retirement - their titles gain
their reason too); a new section 15 states the rule in force, the single
decision constant and the full retired list with one reason per block.

Numbers: the family-table header, the reconciliation block and the date line
are rewritten with the arithmetic stated (1,799 = 1,141 + 658; 742 implemented
keys over 689 entries; 46 evaluators).

Changelog: a v18 row recording that 117 and 118 shipped in light mode and are
reconciled here, with both installed md5s.

v1-v17 are never opened for writing: a NEW filename is written.
"""
import openpyxl

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v17_2026-10-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v18_2026-10-18.xlsx"

wb = openpyxl.load_workbook(SRC)
ws = wb["Abilities"]

# --------------------------------------------------------------------------- rows
OLD_SUMMARY_MARK = "trigger rule: round 116 - THE EDGE-GAP RULE PLUS a delay MEASURED"
NEW_SUMMARY = (
    "trigger rule: round 118 (RECONCILED AT SIGN-OFF in v18) - ONE COMPARISON, MADE AND ACTED ON IN "
    "THE SAME EVALUATION: the nearest ALIVE enemy with MORE THAN 10 models whose HORIZONTAL "
    "CENTRE-to-CENTRE distance from this unit (position() x/z, battle_vector:distance_xz with a sqrt "
    "fallback) is UNDER 6.0 m. The candidate rule is unchanged: alive, more than 10 models, NO "
    "infantry filter and no single-entity test. A second 0.2 s fast pass re-runs the SAME evaluator "
    "while a valid enemy is inside 30 m and adds evaluations, never time; the global poll stays at "
    "250 ms and every guard / charge / in-flight / serialisation gate is unchanged. air_only / "
    "no_melee as the row declares them; the cast is SELF-CENTRED on the OWNER; every read fails "
    "closed; the pre-cast re-check re-measures the centre gap on fresh handles and SKIPS the cast "
    "rather than spending it. The earlier measurement and timing designs (rounds 108-116) are "
    "RETIRED - listed block by block, with one reason each, in Definitions section 15.")

NEW_TRIGGER = (
    "air_drop_on_infantry (round 118 - ONE COMPARISON, ACTED ON IN THE SAME EVALUATION; reconciled "
    "into this workbook at the sign-off pass): the row has NO target flags at all (target_friends / "
    "target_enemies / target_ground / target_self all false), effect_range 0 and "
    "target_intercept_range 10, so the engine drops where the CASTER is and the only decision is "
    "WHEN. THE USER'S RULES, verbatim: '1. I want the trigger to be checked much more frequently "
    "when armed and less than 30 meters from a valid enemy unit. 2. Valid units are those who have "
    "more than 10 entities.' then, on the measurement, 'I tried it. Let's keep the distance to "
    "center' - and the round-118 ruling on top of it is recorded verbatim in Definitions section 15. "
    "THE CHECKS, IN ORDER (every one is a fail-closed pcall in the source): (1) routing -> return "
    "nil. (2) air_only rows: is_currently_flying() must be exactly true; an unreadable read HOLDS "
    "and logs 'airborne check: is_currently_flying() = <v|UNREADABLE> -> HOLDING (this ability's "
    "row is air-only)'. (3) no_melee rows: is_in_melee() must not be true - an UNREADABLE read "
    "HOLDS ('-> HOLDING (fail-closed)'), a true read HOLDS ('-> HOLDING (the row declares "
    "engaged_in_melee)'). (4) THE CANDIDATE SCAN FOURTH.ad_nearest walks "
    "bm:get_scriptunits_for_main_enemy_army_to_local_player(); per enemy, number_of_men_alive() "
    "must answer a NUMBER > FOURTH.AIR_DROP_MIN_MEN = 10. There is NO infantry test in this "
    "evaluator (removed by the user) and NO single-entity test (a one-model Lord / Hero fails the "
    "> 10 test by itself). (5) the candidate's distance must be READABLE, measured by "
    "FOURTH.ad_centre_gap: both position() reads and their get_x() / get_z() must answer NUMBERS, "
    "then battle_vector:distance_xz(b) - the engine's own 'disregarding any height difference' "
    "read - with sqrt(dx*dx + dz*dz) as the fallback; any raise or non-number answers nil and that "
    "enemy is not a candidate. get_y is HEIGHT on the ground plane and is never used, so a caster "
    "60 m above the target is 0 m away. (6) the NEAREST candidate by that centre distance is "
    "chosen. (7) FIRE when the chosen enemy's centre distance is < FOURTH.AIR_DROP_CENTER_M = 6.00 "
    "m - on THAT evaluation: nothing is stamped and nothing is re-measured inside a contact, and a "
    "contact that leaves the line simply stops firing. THE CAST IS SELF-CENTRED: "
    "perform_special_ability(key, OWNER) through the shared FOURTH.try_pair readiness + gate + cast "
    "path, so the 2 s guard, the per-key charge gate, the in-flight wind-up hold and the per-unit "
    "serialisation window all still apply. THE PRE-CAST RE-CHECK runs immediately before the call "
    "on FRESH handles: the CASTER must still be alive, still airborne where its row is air-only and "
    "still out of melee where the engine forbids it; the CHOSEN ENEMY must still be alive, still "
    "have MORE than AIR_DROP_MIN_MEN models, and its centre gap must STILL be under "
    "AIR_DROP_CENTER_M - re-measured with the SAME ad_centre_gap primitive, so the two readings "
    "cannot disagree. A lapsed condition prints 'nearest valid:'<key>' entities=<n> centre=<d.dd>m "
    "(need < 6.00m) -> SKIPPED at re-check (caster_alive=.. flying=.. melee=.. enemy_alive=.. "
    "over_min_men=.. centre_ok=.. min_men=10) - cast not spent', and a good one prints '-> FIRING "
    "(re-checked)'. THE FAST PASS: a SECOND model timer (AIR_DROP_FAST_S = 0.2 s, its own "
    "bm:repeat_callback, pcall-wrapped) runs the SAME evaluator through the SAME try_pair path, but "
    "only for units that are ALIVE, ARMED for an air-drop marker, and only while a VALID enemy is "
    "inside AIR_DROP_NEAR_M = 30 m; it never iterates the full ability table, the global poll "
    "(POLL_MS = 250) and every other ability's cadence are UNCHANGED, and the gates (stamped in "
    "poll ticks) make a second fast tick inside the same poll window unable to cast again. THE LOG, "
    "ON EVERY DECISION: '[<ui id>] <marker> nearest valid:'<enemy land_units key>' entities=<n> "
    "centre=<d.dd>m (need < 6.00m) -> NOT YET' at or over the line, '-> FIRING (the nearest of the "
    "valid enemies; the gap is centre-to-centre, x/z)' under it, plus ONE 'fast poll: ON (nearest "
    "valid <d>m)' / 'fast poll: OFF' line per change and the two re-check lines above. FOUR "
    "CONSTANTS, ONE OF WHICH DECIDES: AIR_DROP_CENTER_M = 6.0 m (FIRE below this centre gap - the "
    "single knob), AIR_DROP_MIN_MEN = 10, AIR_DROP_NEAR_M = 30 m (the fast pass runs while a valid "
    "enemy is this close), AIR_DROP_FAST_S = 0.2 s (the fast pass interval). The earlier "
    "measurement and timing designs (rounds 108-116) are RETIRED, each with a one-line reason, in "
    "Definitions section 15.")

rows = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(row=r, column=21).value != "air_drop_on_infantry":
        continue
    rows += 1
    summary = ws.cell(row=r, column=19).value
    assert OLD_SUMMARY_MARK in summary, "row %d: the round-116 summary is not there" % r
    head, _sep, _tail = summary.partition(" | ")
    ws.cell(row=r, column=19).value = head + " | " + NEW_SUMMARY

    trig = ws.cell(row=r, column=22).value
    assert "round 114 - THE SIMPLE EDGE-GAP RULE" in trig, "row %d: not the round-116 trigger text" % r
    assert "AIR_DROP_DWELL_MID_S" in trig
    ws.cell(row=r, column=22).value = NEW_TRIGGER

assert rows == 19, "expected 19 air-drop rows, edited %d" % rows

# --------------------------------------------------------------------- Definitions
d = wb["Definitions"]

# the trigger-family glossary line (one line per evaluator)
g = d.cell(row=69, column=1).value
assert g == "air_drop_on_infantry", g
d.cell(row=69, column=3).value = (
    "not routing; the caster is AIRBORNE where its row says so (is_currently_flying() exactly true) "
    "and OUT of melee where the row says so (is_in_melee() not true); the nearest ALIVE enemy with "
    "number_of_men_alive() > 10 whose HORIZONTAL CENTRE-to-CENTRE distance (position() x/z, "
    "distance_xz with a sqrt fallback) is under FOURTH.AIR_DROP_CENTER_M = 6.0 m; NO delay, NO dwell, "
    "NO projection, NO fallback, NO edge measurement, NO infantry filter; cast on the OWNER "
    "(self-centred); pre-cast re-check re-measures the centre gap on fresh handles")

# section titles -> RETIRED, with one reason each
t12 = d.cell(row=187, column=1)
assert t12.value.startswith("12. THE AIR-DROP RULE IN FORCE (round 115)"), t12.value
t12.value = (
    "12. THE EDGE-GAP RULE AND THE 1-SECOND DWELL (rounds 114-115/116) - RETIRED IN ROUND 117 and 118. "
    "WHY: the engine's unit_distance() is EDGE-TO-EDGE on bounding boxes, so two wide formations read "
    "a fraction of a metre apart while their centres are 15 m apart (the drop fired with nothing "
    "underneath), and the user then removed the wait entirely. HISTORY ONLY - the rule in force is "
    "section 15.")

t13 = d.cell(row=216, column=1)
assert t13.value.startswith("13. THE DWELL MACHINERY"), t13.value
t13.value = (
    "13. THE DWELL MACHINERY (round 115) - RETIRED IN ROUND 118. WHY: the pair row (FOURTH.ad_pair), "
    "the poll clock, the purge hook and the short-crossing fallback existed only to HOLD a pair under "
    "the line for a while; with no wait there is no pair state, no clock and no crossing to rescue. "
    "HISTORY ONLY.")

t14 = d.cell(row=241, column=1)
assert t14.value.startswith("14. THE MEASURED DELAY (round 116)"), t14.value
t14.value = (
    "14. THE MEASURED DELAY (round 116) - RETIRED IN ROUND 118. WHY: the cosine delay formula, the "
    "velocity rebuild (is_moving / slow_speed / fast_speed / ordered_position) and the 'reads:' "
    "verification log existed only to MEASURE the wait and to prove the heading read that fed it; "
    "no wait, no measurement. HISTORY ONLY.")

for row, tag in ((106, "8. THE AIR-DROP PREDICTION CONSTANTS (round 110)"),
                 (113, "9. THE MOVING-CASTER DIALS (round 111) - ONLY THE CASTER'S LEAD MOVES"),
                 (128, "10. THE FOURTH DIAL AND THE COMPLETE FOUR-DIAL MAP (round 112) - the enemy's lead, plus all four "),
                 (147, "11. THE PATH RULE AND THE DERIVED FRONTAGE (round 113) - the threshold formula, the frontage deri")):
    c = d.cell(row=row, column=1)
    assert tag in c.value, (row, c.value[:80])
    c.value = c.value.rstrip() + (" - RETIRED in round 114: the user replaced projection with one "
                                  "simple comparison, so the dials and the frontage have nothing left "
                                  "to feed. HISTORY ONLY; section 15 is the rule in force.")

# ------------------------------------------------------------------- section 15
base = d.max_row + 2
sec = [
    ("15. THE AIR-DROP RULE IN FORCE (round 118 - reconciled at the sign-off pass in v18): ONE CONSTANT, ONE COMPARISON, NO WAIT", None, None),
    ("THE RULE, ONE LINE",
     "FIRE when the nearest ALIVE enemy with more than 10 models has a HORIZONTAL CENTRE-TO-CENTRE "
     "distance under FOURTH.AIR_DROP_CENTER_M = 6.0 m - on that same evaluation, with no wait of any "
     "kind.", None),
    ("THE DECISION, IN ORDER",
     "not routing -> air_only rows need is_currently_flying() exactly true (unreadable HOLDS) -> "
     "no_melee rows need is_in_melee() not true (unreadable HOLDS) -> walk the main enemy army, keep "
     "every enemy with number_of_men_alive() > 10 AND a readable centre distance -> take the NEAREST "
     "of those by centre distance -> FIRE if that distance is < 6.00 m. Nothing else decides.", None),
    ("WHY THE CENTRE AND NOT A GAP",
     "battle_unit:unit_distance() is the gap between the two units' bounding BOXES: a wide flying "
     "formation beside a wide infantry block reads a fraction of a metre while the flyer's centre is "
     "15 m from the block's centre. position() is 'the centre position of the main squad of the unit', "
     "and the ground plane is X/Z (get_y is height), so the two centres are compared with "
     "distance_xz() - the engine's own 'disregarding any height difference' read - and sqrt(dx^2+dz^2) "
     "as the fallback.", None),
    ("THE CONSTANTS", None, None),
    ("Constant", "Ships as", "What it does / how to tune it"),
    ("FOURTH.AIR_DROP_CENTER_M", "6.0 (m)",
     "THE LINE, and the ONLY air-drop knob. Under it -> FIRE on that evaluation; at or over it -> "
     "'-> NOT YET'. Lower it (6.0 -> 5.0 -> 4.0) if the ordnance still leaves while the enemy is not "
     "yet under the middle of the formation; raise it (6.0 -> 7.0) if the drop never fires. One "
     "number, read in x/z between the two centres, logged on every decision."),
    ("FOURTH.AIR_DROP_MIN_MEN", "10",
     "A candidate needs MORE alive models than this (number_of_men_alive() > 10). This is also what "
     "keeps one-model Lords / Heroes out - there is no separate single-entity test. Unchanged since "
     "round 114."),
    ("FOURTH.AIR_DROP_NEAR_M", "30 (m)",
     "Cadence only: the 0.2 s fast pass runs while a valid enemy is this close. It does not decide "
     "the cast."),
    ("FOURTH.AIR_DROP_FAST_S", "0.2 (s)",
     "Cadence only: the fast pass interval (200 ms, a second bm:repeat_callback). It adds "
     "EVALUATIONS, never time; the gates make it unable to cast twice inside one poll window. The "
     "global poll is POLL_MS = 250 ms and is untouched."),
    ("TOTAL", "1 decision knob + 3 scope/cadence values",
     "Tuning the rule means changing AIR_DROP_CENTER_M. Nothing else moves the decision."),
    ("THE LOG (per decision)",
     "[<ui id>] <marker> nearest valid:'<enemy land_units key>' entities=<n> centre=<d.dd>m (need < 6.00m) -> NOT YET | -> FIRING (the nearest of the valid enemies; the gap is centre-to-centre, x/z)",
     "The ui id is printed because several identical carriers (four Sky-junks, say) are otherwise "
     "indistinguishable. The pre-cast re-check prints '-> SKIPPED at re-check (...)' with "
     "caster_alive / flying / melee / enemy_alive / over_min_men / centre_ok / min_men, or '-> FIRING "
     "(re-checked)'. One 'fast poll: ON (nearest valid <d>m)' / 'fast poll: OFF' line per change."),
    ("RETIRED, WITH THE REASON EACH DIED (history kept, never re-litigated)", None, None),
    ("Block", "Retired in", "Why (one line)"),
    ("AIR_DROP_EDGE_M = 0.10 m - the edge / bounding-box gap", "round 117",
     "unit_distance() measures BOX edges, so a wide flier beside a wide block read 0.5 m apart with "
     "nothing underneath - the wrong measurement, not a wrong threshold."),
    ("AIR_DROP_BOUND_M = 1 m - the first edge test", "round 109",
     "It was still an EDGE measurement; the same bounding-box problem, only tighter."),
    ("AIR_DROP_DWELL_S = 1.0 s, FOURTH.ad_pair, the poll clock, the pair purge, the short-crossing fallback (AIR_DROP_MIN_CONTACT_S = 0.3 s)", "round 118",
     "The user removed the wait completely ('remove the delay we had completely'); with no wait there "
     "is no pair to stamp, no clock to run and no crossing to rescue."),
    ("AIR_DROP_DWELL_MID_S / AIR_DROP_DWELL_SWING_S and the cosine delay formula", "round 118",
     "They existed only to MEASURE the wait from the enemy's heading; no wait, no measurement."),
    ("the velocity rebuild (is_moving / is_moving_fast / slow_speed / fast_speed / ordered_position) and the 'reads:' verification log", "round 118",
     "The velocity existed only to feed the delay, and the reads line only to prove the heading read "
     "that fed it."),
    ("AIR_DROP_DELAY_S / AIR_DROP_ENEMY_LEAD / AIR_DROP_CASTER_DELAY_S / AIR_DROP_CASTER_LEAD / AIR_DROP_INHERIT - the four dials", "round 114",
     "The user replaced two-body projection with one simple comparison; four dials became zero."),
    ("AIR_DROP_MODEL_RADIUS_M / AIR_DROP_RANKS / AIR_DROP_FRONTAGE_MIN_M / _MAX_M and the path segment test", "round 114",
     "The derived frontage credited a side pass, but the API has no radius read at all, so it was an "
     "estimate of an estimate; one gap comparison needs no footprint."),
    ("NOTE on AIR_DROP_CENTER_M", "round 114, BACK in round 117",
     "It was retired with the dials in round 114 and the user brought it back in round 117 ('keep the "
     "distance to center'). It is LIVE: 6.0 m, the single decision constant."),
]
for i, (a, b, c) in enumerate(sec):
    row = base + i
    d.cell(row=row, column=1).value = a
    if b is not None:
        d.cell(row=row, column=2).value = b
    if c is not None:
        d.cell(row=row, column=3).value = c

# ------------------------------------------------------------------------- Numbers
n = wb["Numbers"]
n.cell(row=7, column=1).value = (
    "Date: 2026-10-18     Rule in force since: 2026-10-18     Inventory: 1,799 active abilities     "
    "(v18 - THE SIGN-OFF PASS: rounds 117 and 118 shipped in light mode and are reconciled here. The "
    "air_drop_on_infantry family (12 entries / 19 keys) now fires when the NEAREST enemy that is ALIVE "
    "with MORE THAN 10 models has a HORIZONTAL CENTRE-TO-CENTRE distance under "
    "FOURTH.AIR_DROP_CENTER_M = 6.0 m, on that same evaluation: no delay, no dwell, no velocity or "
    "position projection, no short-crossing fallback and no edge measurement. The retired machinery is "
    "listed block by block, with one reason each, in Definitions section 15. COUNTS UNCHANGED by both "
    "rounds: 1,799 inventory rows / 1,141 in-wheel / 658 excluded / 742 implemented keys over 689 "
    "entries / 46 evaluators.)")

assert n.cell(row=42, column=1).value.startswith("Trigger families after round 116")
n.cell(row=42, column=1).value = (
    "Trigger families after round 118 (the sign-off pass) - re-counted from the mod: 689 entries / "
    "742 keys / 46 evaluators. Rounds 117 and 118 changed NO count - they changed one measurement and "
    "then deleted a wait.")

assert n.cell(row=101, column=1).value.startswith("Round 116 reconciliation")
n.cell(row=101, column=1).value = (
    "SIGN-OFF RECONCILIATION (v18) - THE ARITHMETIC, IN THE UNIT EACH NUMBER IS COUNTED IN. "
    "(1) INVENTORY 1,799: the Abilities sheet holds 1,800 rows including the header, so 1,799 ability "
    "rows; they carry 1,867 key strings because some rows list a base key and its upgraded twin "
    "together. (2) IN-WHEEL vs EXCLUDED, 1,141 + 658 = 1,799: counted from the Status column of this "
    "workbook's own rows (1,141 rows read IN-WHEEL, 658 read EXCLUDED) - a ROW count on both sides, "
    "and the two sum to the inventory exactly. The 658 by family: spells 418 + army-bar 204 + "
    "cataclysm 16 + quest-battle 1 + boss-only 15 + illusion summons 4 = 658. (3) IMPLEMENTED 742 "
    "KEYS over 689 ENTRIES: counted by parsing the shipped ABILITIES table in "
    "mod_source/script/battle/mod/zz_test_deadly_onslaught.lua - 689 '{ marker = ... }' entries whose "
    "keys tables hold 742 distinct key strings (53 entries carry more than one key: Foe-Seeker's "
    "three, Drop Rocks' four, the Tz'arkan five, and so on). THIS workbook marks 741 rows "
    "IMPLEMENTED and those rows carry exactly 741 distinct keys, every one of them in the mod - so "
    "741 + 1 = 742. THE ONE MISSING KEY, NAMED RATHER THAN SMOOTHED OVER: "
    "'wh3_main_spell_slaanesh_slicing_shards_bound' (the mod entry 'slicing_shards') is implemented "
    "in the script and has NO row anywhere in this 1,799-row inventory - not implemented, not "
    "excluded, absent. (4) NOT IMPLEMENTED AMONG THE INCLUDED: 1,141 in-wheel rows - 741 implemented "
    "rows = 400 rows. The older '399' on this sheet is the same pair with the units mixed (1,141 "
    "rows - 742 keys); both are stated so neither is mistaken for a different fact. (5) 46 "
    "EVALUATORS: FOURTH.evaluators holds 46 keys, the family table above lists the same 46 families, "
    "and their entries / keys sum to 689 / 742 - the two counts agree three ways. (6) BOMBARDMENT 55: "
    "131 wh_type_bombardment rows in unit_abilities.tsv -> 58 unit-side with a real visible drawable "
    "ability row -> minus 3 army-bar junctions (Thorsen's Thunderstorm x2, Bubonic Broadside) = 55, "
    "all 55 implemented since round 108. (7) A LABELLING CAVEAT, NOT SMOOTHED OVER: the "
    "per-carrier-family table higher up this sheet is a KEY-level count carried over from "
    "docs/WH3_recount_wheel_only.md and its 'Included' column sums to 1,143 keys and its 'Implemented' "
    "column to 638 - they are NOT the 1,141 rows of (2) and the 742 keys of (3), and that block's "
    "vintage predates rounds 106-118. Read the headline figures from (1)-(6); treat the family block "
    "as a historical key-count breakdown until it is re-derived as one unit end to end.")

# ----------------------------------------------------------------------- Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-18"
ch.cell(row=r, column=2).value = "v18"
ch.cell(row=r, column=3).value = (
    "SIGN-OFF PASS - ROUNDS 117 AND 118 RECONCILED (both shipped in LIGHT mode: air-drop sections "
    "only, no workbook, per the user's standing instruction for tuning iterations, so v17 still "
    "described round 116's measured delay - machinery that no longer exists). (1) THE RULE NOW "
    "DESCRIBED: FIRE when the nearest ALIVE enemy with more than 10 models has a HORIZONTAL "
    "CENTRE-TO-CENTRE distance under FOURTH.AIR_DROP_CENTER_M = 6.0 m, cast on the evaluation that "
    "measures it. Round 117 replaced the edge gap with the centre distance ('I tried it. Let's keep "
    "the distance to center'); round 118 removed the wait ('and remove the delay we had completely'). "
    "(2) 19 AIR-DROP ROWS rewritten in columns 19 and 22 - the candidate rule (> 10 alive models, no "
    "infantry filter) is kept, and every reference to the delay, the dwell, the velocity projection, "
    "the closing-rate reads and the edge measurement is gone from those rows. (3) DEFINITIONS: the "
    "glossary line is rewritten; sections 8-11 (prediction constants, moving-caster dials, the fourth "
    "dial, the path rule and derived frontage) carry their round-114 retirement reasons; sections 12 "
    "(edge rule + dwell), 13 (the dwell machinery) and 14 (the measured delay) are RETITLED RETIRED "
    "with one reason each; new section 15 states the rule in force, the single decision constant, the "
    "log lines and the full retired list (AIR_DROP_EDGE_M, AIR_DROP_BOUND_M, AIR_DROP_DWELL_S + "
    "ad_pair + the clock + the purge + AIR_DROP_MIN_CONTACT_S, AIR_DROP_DWELL_MID_S / _SWING_S, the "
    "velocity rebuild and its reads log, the four dials, the frontage and the path test) with one "
    "line of WHY for each. (4) FULL HARNESS SUITE (the heavy mode) run against this source: 4,777 "
    "checks / 0 failures (harness 119 = harness 118 plus five pin fixes; harness 118's own full run "
    "found 5 failures, all ONE stale pin - h93's hand-kept copy of FOURTH.TRIGGER_TIP still quoted "
    "round 116's velocity-delay wording for air_drop_on_infantry, which is the PRE-118 text; the "
    "source is the truth and the pin followed it). The four air-drop suite-boundary pins left as "
    "floors by the light cycle are now exact: h114 4614, h115 4686, h116 4702, h117 4718. (5) "
    "NUMBERS: 1,799 rows = 1,141 IN-WHEEL + 658 EXCLUDED; 689 entries / 742 keys / 46 evaluators "
    "counted by parsing the shipped ABILITIES table; 741 IMPLEMENTED rows carry 741 distinct keys, so "
    "741 + 1 = 742 - the one remainder, 'wh3_main_spell_slaanesh_slicing_shards_bound' (entry "
    "'slicing_shards'), is implemented in the script and has NO row in the inventory, which is now "
    "named on the Numbers sheet instead of being absorbed by a rounded figure; 1,141 - 741 = 400 rows "
    "not implemented among the included (the older 399 is the same pair with keys subtracted from "
    "rows); 46 evaluators whose families sum to 689 / 742; bombardment 131 -> 58 -> 55, all 55 "
    "implemented. The per-carrier-family block is flagged as a key-level count of an older vintage "
    "rather than silently reconciled. (6) NO SOURCE CHANGE, NO REBUILD: the installed pack was "
    "already the round-118 build.")
ch.cell(row=r, column=4).value = (
    "user instruction 'Update the spreadsheet' (the agreed sign-off point: full suite + workbook); "
    "rounds 117 and 118 per the user's rulings of 2026-10-18. Installed md5s: round 117 "
    "516b16aaa33d26abede8738c4447ffbe, round 118 (and still installed) "
    "2f215bc4c35845452103327fb62ba554. Harness 119: 4,777 checks / 0 failures, run twice "
    "byte-identical; light mode still green at 1,586 / 0.")

wb.save(DST)
print("wrote", DST)
